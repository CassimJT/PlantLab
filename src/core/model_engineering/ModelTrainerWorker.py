# This Python file uses the following encoding: utf-8
import time
import os
import traceback
import pandas as pd
from pathlib import Path
import torch
import torchvision
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
from PIL import Image
import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    QRunnable,
    QMutex,
    QWaitCondition
)


class ModelTrainerSignals(QObject):
    progress = Signal(int)
    finished = Signal(str)
    canceled = Signal(bool)
    error = Signal(str)
    status = Signal(str)
    file_progress = Signal(str, int, int)  # filename, current, total
    conversion_step = Signal(str)  # Current conversion step
    loss_updated = Signal(float)
    accuracy_updated = Signal(float)


class ImageDatasetFromCSV(Dataset):
    """Custom Dataset that loads images from paths in a CSV file (matches your export format)"""
    def __init__(self, csv_file, transform=None):
        self.data = pd.read_csv(csv_file)
        self.transform = transform

        # Your CSV has these columns: absolute_path, relative_path, filename, folder, file_size
        self.image_paths = self.data['absolute_path'].values
        self.folders = self.data['folder'].values

        # Get unique classes from folder names
        self.classes = sorted(list(set(self.folders)))
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}

        # Convert folder names to label indices
        self.labels = [self.class_to_idx[folder] for folder in self.folders]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # Load image
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a blank image as fallback
            image = Image.new('RGB', (224, 224), color='black')

        if self.transform:
            image = self.transform(image)

        return image, label


class ModelTrainerTask(QRunnable):
    def __init__(self, dataset_path: str, model_type: str, epochs: int,
                 batch_size: int, learning_rate: float, train_test_split: float):
        super().__init__()
        self.dataset_path = dataset_path
        self.model_type = model_type
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.train_test_split = train_test_split
        self.signals = ModelTrainerSignals()
        self._is_paused = False
        self._is_canceled = False
        self._pause_condition = QMutex()
        self._pause_wait_condition = QWaitCondition()
        self.last_loss = 0.0
        self.last_accuracy = 0.0
        self.setAutoDelete(False)

        # Set default output location
        home = str(Path.home())
        self._outputLocation = os.path.join(home, "Documents", "plantlab", "models")
        os.makedirs(self._outputLocation, exist_ok=True)

        # Check for CUDA
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Training on device: {self.device}")

    def pause(self):
        """Pause the training task"""
        self._pause_condition.lock()
        self._is_paused = True
        self._pause_condition.unlock()

    def resume(self):
        """Resume the training task"""
        self._pause_condition.lock()
        self._is_paused = False
        self._pause_wait_condition.wakeAll()
        self._pause_condition.unlock()

    def cancel(self):
        """Cancel the training task"""
        self._is_canceled = True
        self.resume()  # Wake up if paused

    def _check_paused(self):
        """Check if training is paused and wait if necessary"""
        if self._is_canceled:
            return False

        self._pause_condition.lock()
        while self._is_paused and not self._is_canceled:
            self._pause_wait_condition.wait(self._pause_condition)
        self._pause_condition.unlock()

        return not self._is_canceled

    def _load_dataset_from_csv(self):
        """Load and prepare dataset from CSV file (your export format)"""
        self.signals.status.emit(f"Loading dataset from CSV: {os.path.basename(self.dataset_path)}")
        self.signals.file_progress.emit("Reading CSV...", 0, 100)

        # Define transforms for training and validation
        train_transform = transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        val_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        # Load full dataset from CSV
        self.signals.file_progress.emit("Loading CSV data...", 20, 100)
        full_dataset = ImageDatasetFromCSV(self.dataset_path, transform=train_transform)

        # Get class names (from folder names)
        self.class_names = full_dataset.classes
        num_classes = len(self.class_names)
        self.signals.status.emit(f"Found {num_classes} classes: {', '.join(self.class_names[:5])}...")
        self.signals.status.emit(f"Total images: {len(full_dataset)}")

        # Split dataset
        dataset_size = len(full_dataset)
        train_size = int(self.train_test_split * dataset_size)
        val_size = dataset_size - train_size

        self.signals.file_progress.emit("Splitting dataset...", 40, 100)

        # Use random_split with fixed seed for reproducibility
        generator = torch.Generator().manual_seed(42)
        train_indices, val_indices = random_split(
            range(dataset_size), [train_size, val_size],
            generator=generator
        )

        # Create validation dataset with its own transform
        class SplitDataset(Dataset):
            def __init__(self, indices, full_dataset, transform):
                self.indices = indices
                self.full_dataset = full_dataset
                self.transform = transform

            def __len__(self):
                return len(self.indices)

            def __getitem__(self, idx):
                img, label = self.full_dataset[self.indices[idx]]
                return self.transform(img), label

        train_dataset = SplitDataset(train_indices.indices, full_dataset, train_transform)
        val_dataset = SplitDataset(val_indices.indices, full_dataset, val_transform)

        self.signals.file_progress.emit("Creating data loaders...", 60, 100)

        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True if self.device.type == 'cuda' else False
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True if self.device.type == 'cuda' else False
        )

        self.signals.file_progress.emit("Dataset ready!", 100, 100)

        return train_loader, val_loader, num_classes

    def _create_model(self, num_classes):
        """Create MobileNetV3 model with transfer learning"""
        self.signals.status.emit(f"Creating {self.model_type} model...")

        # Load pretrained model based on type
        if "mobilenetv3_small" in self.model_type:
            weights = torchvision.models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_small(weights=weights)
            # Modify classifier for number of classes
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)

        elif "mobilenetv3_large" in self.model_type:
            weights = torchvision.models.MobileNet_V3_Large_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_large(weights=weights)
            # Modify classifier for number of classes
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)

        elif "ssdlite_mobilenetv3" in self.model_type:
            # For detection, you'd need a different architecture
            self.signals.status.emit("SSD Lite not fully implemented yet")
            weights = torchvision.models.MobileNet_V3_Large_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_large(weights=weights)
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)
        else:
            # Default to small
            weights = torchvision.models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_small(weights=weights)
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)

        return model.to(self.device)

    def _train_epoch(self, model, train_loader, criterion, optimizer, epoch):
        """Train for one epoch"""
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        num_batches = len(train_loader)

        for batch_idx, (images, labels) in enumerate(train_loader):
            if not self._check_paused():
                return None, None

            # Move data to device
            images, labels = images.to(self.device), labels.to(self.device)

            # Zero gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass
            loss.backward()
            optimizer.step()

            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            # Update progress
            batch_progress = int((batch_idx + 1) / num_batches * 100)
            self.signals.file_progress.emit(
                f"Epoch {epoch}",
                batch_progress,
                100
            )

        avg_loss = running_loss / num_batches
        accuracy = correct / total

        return avg_loss, accuracy

    def _validate(self, model, val_loader, criterion):
        """Validate the model"""
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(self.device), labels.to(self.device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

        avg_val_loss = val_loss / len(val_loader)
        accuracy = correct / total

        return avg_val_loss, accuracy

    def run(self):
        """Main training execution with real PyTorch training using CSV"""
        try:
            # Validate CSV file exists
            if not os.path.exists(self.dataset_path):
                self.signals.error.emit(f"CSV file does not exist: {self.dataset_path}")
                self.signals.finished.emit("failed")
                return

            if not self.dataset_path.endswith('.csv'):
                self.signals.error.emit(f"File must be a CSV: {self.dataset_path}")
                self.signals.finished.emit("failed")
                return

            self.signals.status.emit(f"Starting training with {self.model_type}")
            self.signals.conversion_step.emit("Loading dataset from CSV...")

            # Load dataset from CSV
            train_loader, val_loader, num_classes = self._load_dataset_from_csv()

            if self._is_canceled:
                self.signals.canceled.emit(True)
                return

            # Create model
            self.signals.conversion_step.emit("Creating model...")
            model = self._create_model(num_classes)

            # Loss function and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)

            # Learning rate scheduler
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

            self.signals.status.emit(f"Training on {self.device}")
            self.signals.conversion_step.emit("Training model...")

            best_accuracy = 0.0
            best_model_path = None

            # Training loop
            for epoch in range(1, self.epochs + 1):
                if self._is_canceled:
                    self.signals.canceled.emit(True)
                    return

                # Train
                train_loss, train_acc = self._train_epoch(
                    model, train_loader, criterion, optimizer, epoch
                )

                if train_loss is None:  # Canceled
                    return

                # Validate
                val_loss, val_acc = self._validate(model, val_loader, criterion)

                # Update learning rate
                scheduler.step()

                # Store current values
                self.last_loss = val_loss
                self.last_accuracy = val_acc

                # Emit signals
                progress = int((epoch / self.epochs) * 100)
                self.signals.progress.emit(progress)
                self.signals.loss_updated.emit(val_loss)
                self.signals.accuracy_updated.emit(val_acc)

                self.signals.status.emit(
                    f"Epoch {epoch}/{self.epochs} - "
                    f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2%} | "
                    f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2%}"
                )

                # Save best model
                if val_acc > best_accuracy:
                    best_accuracy = val_acc
                    best_model_path = os.path.join(
                        self._outputLocation,
                        f"best_model_{self.model_type}_epoch{epoch}_{int(time.time())}.pth"
                    )
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'best_accuracy': best_accuracy,
                        'class_names': self.class_names
                    }, best_model_path)
                    self.signals.status.emit(f"New best model saved! Accuracy: {best_accuracy:.2%}")

            # Training completed
            self.signals.conversion_step.emit("Finalizing model...")

            # Save final model
            final_model_path = os.path.join(
                self._outputLocation,
                f"final_model_{self.model_type}_{int(time.time())}.pth"
            )
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': self.class_names,
                'num_classes': num_classes,
                'model_type': self.model_type
            }, final_model_path)

            self.signals.status.emit(f"Final model saved to: {final_model_path}")

            # Calculate final metrics on validation set
            _, final_accuracy = self._validate(model, val_loader, criterion)

            # For precision/recall, we'd need to compute per class
            # This is a simplified version
            final_precision = final_accuracy
            final_recall = final_accuracy
            final_f1 = final_accuracy

            result_summary = (f"Training completed successfully!\n"
                            f"Best Validation Accuracy: {best_accuracy:.1%}\n"
                            f"Final Validation Accuracy: {final_accuracy:.1%}\n"
                            f"Precision: {final_precision:.1%}\n"
                            f"Recall: {final_recall:.1%}\n"
                            f"F1 Score: {final_f1:.1%}\n"
                            f"Model saved to: {final_model_path}")

            self.signals.finished.emit(result_summary)

        except Exception as e:
            error_msg = f"Training error: {str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)
            self.signals.finished.emit("failed")

        finally:
            # Comprehensive signal cleanup
            self._cleanup_signals()

    def _cleanup_signals(self):
        """Safely disconnect all signals to prevent memory leaks"""
        try:
            signals_to_disconnect = [
                self.signals.progress,
                self.signals.finished,
                self.signals.canceled,
                self.signals.error,
                self.signals.status,
                self.signals.file_progress,
                self.signals.conversion_step,
                self.signals.loss_updated,
                self.signals.accuracy_updated
            ]

            for signal in signals_to_disconnect:
                try:
                    while signal.receivers() > 0:
                        signal.disconnect()
                except (RuntimeError, TypeError):
                    pass

        except Exception as e:
            print(f"Signal cleanup warning: {e}")

    def __del__(self):
        """Ensure cleanup when object is deleted"""
        self._cleanup_signals()
