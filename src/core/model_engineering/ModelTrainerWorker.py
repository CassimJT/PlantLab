# This Python file uses the following encoding: utf-8
import time
import os
import json
import traceback
from pathlib import Path
from datetime import datetime
import pandas as pd
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
    file_progress = Signal(str, int, int)
    conversion_step = Signal(str)
    loss_updated = Signal(float)
    accuracy_updated = Signal(float)
    fitting_warning = Signal(str)


class ImageDatasetFromCSV(Dataset):
    """Custom Dataset that loads images from paths in a CSV file (matches your export format)"""
    def __init__(self, csv_file, transform=None, class_mapping=None):
        self.data = pd.read_csv(csv_file)
        self.transform = transform
        self.class_mapping = class_mapping

        # Your CSV has these columns: absolute_path, relative_path, filename, folder, file_size
        self.image_paths = self.data['absolute_path'].values
        self.folders = self.data['folder'].values

        if class_mapping:
            # Use provided mapping (folder names to actual class names)
            self.classes = sorted(list(set(class_mapping.values())))
            self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}

            # Map folder names to actual class names then to indices
            self.labels = []
            for folder in self.folders:
                actual_class = class_mapping[folder]
                self.labels.append(self.class_to_idx[actual_class])
        else:
            # Try to extract from filename as fallback
            def extract_class_name(filename):
                return filename.split('-')[0].lower()

            self.classes = []
            self.labels = []
            class_to_idx = {}

            for filename in self.data['filename'].values:
                class_name = extract_class_name(filename)
                if class_name not in class_to_idx:
                    class_to_idx[class_name] = len(class_to_idx)
                    self.classes.append(class_name)
                self.labels.append(class_to_idx[class_name])

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


class SplitDataset(Dataset):
    """Dataset for train/val splits that applies transforms only once"""
    def __init__(self, indices, image_paths, labels, transform):
        self.indices = indices
        self.image_paths = [image_paths[i] for i in indices]
        self.labels = [labels[i] for i in indices]
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # Load image (already normalized by NormalizationTask)
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            image = Image.new('RGB', (224, 224), color='black')

        if self.transform:
            image = self.transform(image)

        return image, label


class ModelTrainerTask(QRunnable):
    def __init__(self, dataset_path: str, model_type: str, epochs: int,
                 batch_size: int, learning_rate: float, train_test_split: float,
                 class_mapping: dict = None, custom_model_path: str = None):
        super().__init__()
        self.dataset_path = dataset_path
        self.model_type = model_type
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.train_test_split = train_test_split
        self.class_mapping = class_mapping
        self.custom_model_path = custom_model_path
        self.signals = ModelTrainerSignals()
        self._is_paused = False
        self._is_canceled = False
        self._pause_condition = QMutex()
        self._pause_wait_condition = QWaitCondition()
        self.last_loss = 0.0
        self.last_accuracy = 0.0
        self._final_model_path = None
        self._best_model_path = None
        self.setAutoDelete(False)

        # Training phase tracking
        self._phase1_complete = False
        self._unfreeze_epoch = None

        # Training history tracking
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': [],
            'learning_rate': [],
            'epoch_times': []
        }

        # Overfitting detection parameters
        self.early_stopping_patience = 7
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        self.epochs_no_improve = 0
        self.overfitting_warnings = []

        # Per-class metrics tracking
        self.per_class_metrics = {}

        # Metadata storage
        self.training_metadata = {
            'model_info': {},
            'dataset_info': {},
            'training_config': {},
            'performance_metrics': {},
            'fitting_analysis': {},
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }

        # Set default output location
        home = str(Path.home())
        self._outputLocation = os.path.join(home, "Documents", "plantlab", "models")
        os.makedirs(self._outputLocation, exist_ok=True)

        # Check for CUDA
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Training on device: {self.device}")

        # FINE-TUNING CONFIGURATION
        # Block indices to unfreeze during phase 2
        # MobileNetV3 has 16 inverted residual blocks (indices 0-15)
        # We freeze first 13 blocks, unfreeze last 3 blocks (indices 13, 14, 15)
        self.unfreeze_from_block = 13  # Unfreeze blocks 13, 14, 15 (final 3 blocks = ~35 layers)

        # Alternative: For more aggressive fine-tuning, use 12 (unfreeze last 4 blocks)
        # For less aggressive, use 14 (unfreeze last 2 blocks)

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
        self.resume()

    def _check_paused(self):
        """Check if training is paused and wait if necessary"""
        if self._is_canceled:
            return False

        self._pause_condition.lock()
        while self._is_paused and not self._is_canceled:
            self._pause_wait_condition.wait(self._pause_condition)
        self._pause_condition.unlock()

        return not self._is_canceled

    def _freeze_all_base_layers(self, model):
        """
        PHASE 1: Freeze ALL base layers of the model.
        Only the newly initialized classifier head will be trainable.
        This preserves all ImageNet knowledge while training the new head.
        """
        # Freeze every parameter in the model
        for param in model.parameters():
            param.requires_grad = False

        # Unfreeze ONLY the classifier head (new layers we added)
        for param in model.classifier.parameters():
            param.requires_grad = True

        # Count trainable parameters for logging
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())

        self.signals.status.emit(
            f"PHASE 1: Frozen all {total_params:,} parameters. "
            f"Only {trainable_params:,} classifier parameters trainable "
            f"({100*trainable_params/total_params:.2f}% of total)"
        )

        return trainable_params, total_params

    def _unfreeze_late_layers(self, model):
        """
        PHASE 2: Unfreeze the final N blocks of the model for fine-tuning.
        This allows the model to adapt its high-level features to Malawi-specific diseases
        while preserving low-level feature detectors (edges, colors, textures).

        MobileNetV3 structure:
        - Blocks 0-12: Low/mid-level features (edges, shapes, textures) - REMAIN FROZEN
        - Blocks 13-15: High-level task-specific features - UNFROZEN for fine-tuning
        """
        # First, ensure all layers are frozen
        for param in model.parameters():
            param.requires_grad = False

        # Unfreeze the classifier head (always trainable)
        for param in model.classifier.parameters():
            param.requires_grad = True

        # Unfreeze the final blocks of the features
        # MobileNetV3 features are organized as Sequential modules
        # Block indices: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
        unfrozen_blocks = 0

        for name, param in model.features.named_parameters():
            # Parse block index from parameter name
            # Format: "13.0.block.0.0.weight" -> block index 13
            parts = name.split('.')
            if len(parts) >= 1:
                try:
                    block_idx = int(parts[0])
                    if block_idx >= self.unfreeze_from_block:
                        param.requires_grad = True
                        if unfrozen_blocks == 0:
                            self.signals.status.emit(f"Unfreezing block {block_idx} and above")
                        unfrozen_blocks += 1
                except ValueError:
                    # Not a block index (e.g., "conv_stem" or "norm")
                    pass

        # Count trainable parameters after unfreezing
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())

        self.signals.status.emit(
            f"PHASE 2: Unfroze blocks {self.unfreeze_from_block}+. "
            f"Now {trainable_params:,} parameters trainable "
            f"({100*trainable_params/total_params:.2f}% of total)"
        )

        return trainable_params, total_params

    def _check_fitting_issues(self, train_loss, val_loss, train_acc, val_acc, epoch):
        """Lightweight check for overfitting/underfitting signs"""
        # Calculate gaps
        loss_gap = val_loss - train_loss
        acc_gap = train_acc - val_acc

        warning = None

        # Overfitting indicators
        if val_loss > train_loss * 1.15 and epoch > 3:
            warning = f"Possible overfitting: Val loss {val_loss:.4f} vs Train loss {train_loss:.4f}"
        elif acc_gap > 0.12 and epoch > 3:
            warning = f"Large accuracy gap: Train {train_acc:.1%} vs Val {val_acc:.1%}"
        elif train_acc > 0.94 and val_acc < 0.82 and epoch > 5:
            warning = "Severe overfitting: Model memorizing training data"
        elif train_acc < 0.65 and epoch > 10:
            warning = "Possible underfitting: Low training accuracy"
        elif train_loss > 1.2 and epoch > 10:
            warning = "Model not learning effectively"
        elif len(self.training_history['val_acc']) >= 5:
            recent_vals = self.training_history['val_acc'][-5:]
            if max(recent_vals) - min(recent_vals) < 0.01 and epoch > 10:
                warning = "Model plateaued: Consider adjusting learning rate"

        if warning:
            self.training_metadata['warnings'].append({
                'epoch': epoch,
                'warning': warning,
                'train_acc': train_acc,
                'val_acc': val_acc,
                'train_loss': train_loss,
                'val_loss': val_loss
            })

            if len(self.overfitting_warnings) < 10:
                self.overfitting_warnings.append(warning)
                self.signals.fitting_warning.emit(warning)
                self.signals.status.emit(warning)

    def _load_dataset_from_csv(self):
        """Load and prepare dataset from CSV file"""
        self.signals.status.emit(f"Loading dataset from CSV: {os.path.basename(self.dataset_path)}")
        self.signals.file_progress.emit("Reading CSV...", 0, 100)

        # Define transforms for training and validation
        train_transform = transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        val_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        # Load raw dataset WITHOUT transforms
        self.signals.file_progress.emit("Loading CSV data...", 20, 100)
        raw_dataset = ImageDatasetFromCSV(
            self.dataset_path,
            transform=None,
            class_mapping=self.class_mapping
        )

        # Get class names
        self.class_names = raw_dataset.classes
        num_classes = len(self.class_names)

        # Store dataset info in metadata
        self.training_metadata['dataset_info'] = {
            'num_classes': num_classes,
            'class_names': self.class_names,
            'total_images': len(raw_dataset),
            'csv_path': self.dataset_path,
            'class_mapping': self.class_mapping
        }

        self.signals.status.emit(f"Found {num_classes} classes: {', '.join(self.class_names[:5])}...")
        self.signals.status.emit(f"Total images: {len(raw_dataset)}")

        # Split dataset
        dataset_size = len(raw_dataset)
        train_size = int(self.train_test_split * dataset_size)
        val_size = dataset_size - train_size

        self.signals.file_progress.emit("Splitting dataset...", 40, 100)

        # Use random_split with fixed seed for reproducibility
        generator = torch.Generator().manual_seed(42)
        train_indices, val_indices = random_split(
            range(dataset_size), [train_size, val_size],
            generator=generator
        )

        # Create split datasets with transforms applied ONCE
        train_dataset = SplitDataset(
            train_indices.indices,
            raw_dataset.image_paths,
            raw_dataset.labels,
            train_transform
        )

        val_dataset = SplitDataset(
            val_indices.indices,
            raw_dataset.image_paths,
            raw_dataset.labels,
            val_transform
        )

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

    def _load_custom_model(self, num_classes):
        """Load a custom base model from file for fine-tuning"""
        self.signals.status.emit(f"Loading custom base model: {os.path.basename(self.custom_model_path)}")

        try:
            checkpoint = torch.load(self.custom_model_path, map_location=self.device)

            # Determine model architecture from checkpoint
            model_type = checkpoint.get('model_type', self.model_type)

            # Create model based on type
            if "mobilenetv3_small" in model_type or "small" in model_type:
                model = torchvision.models.mobilenet_v3_small(weights=None)
                in_features = model.classifier[3].in_features
                model.classifier[3] = nn.Linear(in_features, num_classes)
            elif "mobilenetv3_large" in model_type or "large" in model_type:
                model = torchvision.models.mobilenet_v3_large(weights=None)
                in_features = model.classifier[3].in_features
                model.classifier[3] = nn.Linear(in_features, num_classes)
            else:
                model = torchvision.models.mobilenet_v3_small(weights=None)
                in_features = model.classifier[3].in_features
                model.classifier[3] = nn.Linear(in_features, num_classes)

            # Load the pretrained weights (excluding classifier)
            if 'model_state_dict' in checkpoint:
                pretrained_dict = {k: v for k, v in checkpoint['model_state_dict'].items()
                                  if 'classifier' not in k}
                model_dict = model.state_dict()
                model_dict.update(pretrained_dict)
                model.load_state_dict(model_dict, strict=False)
            else:
                pretrained_dict = {k: v for k, v in checkpoint.items()
                                  if 'classifier' not in k}
                model_dict = model.state_dict()
                model_dict.update(pretrained_dict)
                model.load_state_dict(model_dict, strict=False)

            self.signals.status.emit(f"Custom model loaded successfully!")

            self.training_metadata['model_info'] = {
                'model_type': 'custom_finetuned',
                'base_model_source': self.custom_model_path,
                'original_model_type': checkpoint.get('model_type', 'unknown'),
                'num_classes': num_classes,
                'pretrained': True,
                'input_size': (3, 224, 224)
            }

            return model

        except Exception as e:
            self.signals.status.emit(f"Error loading custom model: {str(e)}")
            self.signals.status.emit("Falling back to default pretrained model")
            return None

    def _create_model(self, num_classes):
        """Create MobileNetV3 model with transfer learning"""

        # Try to load custom model first if specified
        if self.custom_model_path and os.path.exists(self.custom_model_path):
            custom_model = self._load_custom_model(num_classes)
            if custom_model is not None:
                return custom_model

        # Fall back to default pretrained models
        self.signals.status.emit(f"Creating {self.model_type} model with ImageNet pretrained weights...")

        # Load pretrained model based on type
        if "mobilenetv3_small" in self.model_type:
            weights = torchvision.models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_small(weights=weights)
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)

        elif "mobilenetv3_large" in self.model_type:
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

        # Store model info in metadata
        self.training_metadata['model_info'] = {
            'model_type': self.model_type,
            'num_classes': num_classes,
            'base_architecture': 'mobilenetv3',
            'pretrained': True,
            'pretrained_weights': 'ImageNet1K_V1',
            'input_size': (3, 224, 224),
            'fine_tuning_config': {
                'phase1_frozen_blocks': 'all except classifier',
                'phase2_unfreeze_from_block': self.unfreeze_from_block,
                'unfrozen_blocks_count': 16 - self.unfreeze_from_block,
                'approx_unfrozen_layers': 35
            }
        }

        return model.to(self.device)

    def _train_epoch(self, model, train_loader, val_loader, criterion, optimizer, epoch, phase):
        """Train for one epoch with validation tracking"""
        epoch_start = time.time()

        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            if not self._check_paused():
                return None, None, None, None

            images, labels = images.to(self.device), labels.to(self.device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        # Calculate averages
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        train_acc = train_correct / train_total
        val_acc = val_correct / val_total
        epoch_time = time.time() - epoch_start

        # Store in history
        self.training_history['train_loss'].append(avg_train_loss)
        self.training_history['val_loss'].append(avg_val_loss)
        self.training_history['train_acc'].append(train_acc)
        self.training_history['val_acc'].append(val_acc)
        self.training_history['learning_rate'].append(optimizer.param_groups[0]['lr'])
        self.training_history['epoch_times'].append(epoch_time)

        # Check for fitting issues
        self._check_fitting_issues(avg_train_loss, avg_val_loss, train_acc, val_acc, epoch)

        # Early stopping check
        if avg_val_loss < self.best_val_loss:
            self.best_val_loss = avg_val_loss
            self.best_val_acc = val_acc
            self.epochs_no_improve = 0
        else:
            self.epochs_no_improve += 1

        return avg_train_loss, avg_val_loss, train_acc, val_acc

    def _calculate_per_class_metrics(self, model, val_loader):
        """Calculate precision, recall, F1 per class (only at end of training)"""
        model.eval()
        num_classes = len(self.class_names)
        confusion_matrix = torch.zeros(num_classes, num_classes)

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)

                for t, p in zip(labels.view(-1), predicted.view(-1)):
                    confusion_matrix[t.long(), p.long()] += 1

        # Calculate per-class metrics
        per_class_metrics = {}
        for i in range(num_classes):
            tp = confusion_matrix[i, i].item()
            fp = confusion_matrix[:, i].sum().item() - tp
            fn = confusion_matrix[i, :].sum().item() - tp

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            per_class_metrics[self.class_names[i]] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'support': tp + fn
            }

            if precision < 0.7 or recall < 0.7:
                self.signals.status.emit(
                    f"⚠ Low performance for class '{self.class_names[i]}': "
                    f"Prec={precision:.2f}, Recall={recall:.2f}"
                )

        return per_class_metrics, confusion_matrix

    def _save_training_metadata(self, model_path, final_accuracy, best_accuracy):
        """Save comprehensive training metadata to JSON file"""
        train_acc_history = self.training_history['train_acc']
        val_acc_history = self.training_history['val_acc']

        final_train_acc = train_acc_history[-1] if train_acc_history else 0
        final_val_acc = val_acc_history[-1] if val_acc_history else 0
        acc_gap = final_train_acc - final_val_acc

        # Determine fitting status
        if acc_gap > 0.15:
            fitting_status = "Severe Overfitting"
        elif acc_gap > 0.08:
            fitting_status = "Moderate Overfitting"
        elif final_train_acc < 0.7:
            fitting_status = "Underfitting"
        elif acc_gap < 0.05 and final_val_acc > 0.9:
            fitting_status = "Excellent Fit"
        elif acc_gap < 0.08 and final_val_acc > 0.8:
            fitting_status = "Good Fit"
        else:
            fitting_status = "Acceptable Fit"

        self.training_metadata.update({
            'training_config': {
                'epochs': self.epochs,
                'batch_size': self.batch_size,
                'learning_rate': self.learning_rate,
                'train_test_split': self.train_test_split,
                'device': str(self.device),
                'early_stopping_patience': self.early_stopping_patience,
                'actual_epochs_completed': len(train_acc_history),
                'custom_base_model': self.custom_model_path,
                'fine_tuning_strategy': {
                    'phase1': 'Frozen all base layers, trained only classifier',
                    'phase2': f'Unfroze blocks {self.unfreeze_from_block}+ (final {16 - self.unfreeze_from_block} blocks)',
                    'unfreeze_trigger_epoch': self._unfreeze_epoch
                }
            },
            'performance_metrics': {
                'final_train_accuracy': final_train_acc,
                'final_val_accuracy': final_val_acc,
                'best_val_accuracy': best_accuracy,
                'final_train_loss': self.training_history['train_loss'][-1] if self.training_history['train_loss'] else 0,
                'final_val_loss': self.training_history['val_loss'][-1] if self.training_history['val_loss'] else 0,
                'train_val_accuracy_gap': acc_gap,
                'total_training_time': sum(self.training_history['epoch_times']),
                'avg_epoch_time': np.mean(self.training_history['epoch_times']) if self.training_history['epoch_times'] else 0
            },
            'fitting_analysis': {
                'status': fitting_status,
                'warnings_count': len(self.training_metadata['warnings']),
                'early_stopping_triggered': self.epochs_no_improve >= self.early_stopping_patience,
                'epochs_without_improvement': self.epochs_no_improve
            },
            'per_class_metrics': self.per_class_metrics,
            'training_history_summary': {
                'train_acc_max': max(train_acc_history) if train_acc_history else 0,
                'train_acc_min': min(train_acc_history) if train_acc_history else 0,
                'val_acc_max': max(val_acc_history) if val_acc_history else 0,
                'val_acc_min': min(val_acc_history) if val_acc_history else 0,
                'final_epoch': len(train_acc_history)
            }
        })

        metadata_path = model_path.replace('.pth', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.training_metadata, f, indent=2, default=str)

        self.signals.status.emit(f"Training metadata saved to: {metadata_path}")
        self.signals.status.emit(f"Fitting Analysis: {fitting_status}")

    def _validate(self, model, val_loader, criterion):
        """Validate the model (simple version for final metrics)"""
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
        """Main training execution with proper two-phase transfer learning"""
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

            # ================================================================
            # PHASE 1: FREEZE ALL BASE LAYERS - Train only classifier head
            # ================================================================
            self.signals.conversion_step.emit("PHASE 1: Freezing base layers, training classifier head...")

            # Freeze all base layers, keep only classifier trainable
            self._freeze_all_base_layers(model)

            # Phase 1 uses higher learning rate since only new layers are training
            phase1_lr = self.learning_rate  # e.g., 0.001
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=phase1_lr)

            self.signals.status.emit(f"PHASE 1: Training classifier head for {self.epochs // 2} epochs at LR={phase1_lr}")

            best_accuracy = 0.0
            best_model_path = None
            phase1_epochs = max(5, self.epochs // 3)  # Phase 1: ~1/3 of epochs or at least 5

            for epoch in range(1, phase1_epochs + 1):
                if self._is_canceled:
                    self.signals.canceled.emit(True)
                    return

                train_loss, val_loss, train_acc, val_acc = self._train_epoch(
                    model, train_loader, val_loader, criterion, optimizer, epoch, phase=1
                )

                if train_loss is None:
                    return

                self.last_loss = val_loss
                self.last_accuracy = val_acc

                progress = int((epoch / self.epochs) * 50)  # Phase 1 is first 50% of progress bar
                self.signals.progress.emit(progress)
                self.signals.loss_updated.emit(val_loss)
                self.signals.accuracy_updated.emit(val_acc)

                self.signals.status.emit(
                    f"[PHASE 1] Epoch {epoch}/{phase1_epochs} - "
                    f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2%} | "
                    f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2%}"
                )

                # Save best model from phase 1
                if val_acc > best_accuracy:
                    best_accuracy = val_acc
                    timestamp = int(time.time())
                    best_model_path = os.path.join(
                        self._outputLocation,
                        f"best_model_phase1_{self.model_type}_epoch{epoch}_{timestamp}.pth"
                    )
                    torch.save({
                        'epoch': epoch,
                        'phase': 1,
                        'model_state_dict': model.state_dict(),
                        'best_accuracy': best_accuracy,
                        'class_names': self.class_names,
                        'num_classes': num_classes,
                        'model_type': self.model_type,
                    }, best_model_path)

            # ================================================================
            # PHASE 2: UNFREEZE LATE LAYERS - Fine-tune for Malawi context
            # ================================================================
            self.signals.conversion_step.emit("PHASE 2: Unfreezing late layers for fine-tuning...")
            self._unfreeze_late_layers(model)
            self._unfreeze_epoch = phase1_epochs + 1

            # Phase 2 uses LOWER learning rate (1/10 of phase 1) to avoid destroying pretrained weights
            phase2_lr = self.learning_rate / 10.0  # e.g., 0.0001
            optimizer = optim.Adam(model.parameters(), lr=phase2_lr)

            # Optional: Use a scheduler for phase 2
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)

            self.signals.status.emit(f"PHASE 2: Fine-tuning with LR={phase2_lr} for remaining epochs")

            phase2_start_epoch = phase1_epochs + 1
            phase2_best_accuracy = best_accuracy

            for epoch in range(phase2_start_epoch, self.epochs + 1):
                if self._is_canceled:
                    self.signals.canceled.emit(True)
                    return

                train_loss, val_loss, train_acc, val_acc = self._train_epoch(
                    model, train_loader, val_loader, criterion, optimizer, epoch, phase=2
                )

                if train_loss is None:
                    return

                # Update learning rate scheduler
                scheduler.step(val_loss)

                self.last_loss = val_loss
                self.last_accuracy = val_acc

                progress = 50 + int(((epoch - phase1_epochs) / (self.epochs - phase1_epochs)) * 50)
                self.signals.progress.emit(progress)
                self.signals.loss_updated.emit(val_loss)
                self.signals.accuracy_updated.emit(val_acc)

                self.signals.status.emit(
                    f"[PHASE 2] Epoch {epoch}/{self.epochs} - "
                    f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2%} | "
                    f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2%}"
                )

                # Save best model from phase 2
                if val_acc > phase2_best_accuracy:
                    phase2_best_accuracy = val_acc
                    timestamp = int(time.time())
                    best_model_path = os.path.join(
                        self._outputLocation,
                        f"best_model_{self.model_type}_epoch{epoch}_{timestamp}.pth"
                    )
                    torch.save({
                        'epoch': epoch,
                        'phase': 2,
                        'model_state_dict': model.state_dict(),
                        'best_accuracy': phase2_best_accuracy,
                        'class_names': self.class_names,
                        'num_classes': num_classes,
                        'model_type': self.model_type,
                        'fine_tuning_info': {
                            'unfrozen_from_block': self.unfreeze_from_block,
                            'phase2_learning_rate': phase2_lr
                        }
                    }, best_model_path)
                    self.signals.status.emit(f"New best model saved! Accuracy: {phase2_best_accuracy:.2%}")

                # Early stopping check
                if self.epochs_no_improve >= self.early_stopping_patience:
                    self.signals.status.emit(
                        f"Early stopping triggered after {epoch} epochs"
                    )
                    break

            # Training completed
            self.signals.conversion_step.emit("Calculating final metrics...")

            # Calculate per-class metrics
            self.per_class_metrics, confusion_matrix = self._calculate_per_class_metrics(model, val_loader)

            # Calculate final metrics
            _, final_accuracy = self._validate(model, val_loader, criterion)

            # Save final model
            timestamp = int(time.time())
            final_model_path = os.path.join(
                self._outputLocation,
                f"final_model_{self.model_type}_{timestamp}.pth"
            )

            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': self.class_names,
                'num_classes': num_classes,
                'model_type': self.model_type,
                'input_size': (3, 224, 224),
                'final_accuracy': final_accuracy,
                'best_accuracy': phase2_best_accuracy,
                'training_history': self.training_history,
                'per_class_metrics': self.per_class_metrics,
                'confusion_matrix': confusion_matrix.tolist(),
                'hyperparameters': {
                    'epochs': self.epochs,
                    'batch_size': self.batch_size,
                    'learning_rate': self.learning_rate,
                    'phase1_learning_rate': phase1_lr,
                    'phase2_learning_rate': phase2_lr,
                    'train_test_split': self.train_test_split,
                    'device': str(self.device),
                    'custom_base_model': self.custom_model_path,
                    'fine_tuning_strategy': {
                        'unfreeze_from_block': self.unfreeze_from_block,
                        'unfrozen_blocks': f"blocks {self.unfreeze_from_block} through 15",
                        'approx_layers_unfrozen': 35
                    }
                },
                'timestamp': timestamp,
                'class_mapping': self.class_mapping,
                'dataset_info': {
                    'num_classes': num_classes,
                    'class_names': self.class_names,
                    'total_images': len(train_loader.dataset) + len(val_loader.dataset)
                }
            }, final_model_path)

            self._final_model_path = final_model_path
            self._best_model_path = best_model_path

            # Save comprehensive metadata
            self._save_training_metadata(final_model_path, final_accuracy, phase2_best_accuracy)

            self.signals.status.emit(f"Final model saved to: {final_model_path}")

            # Calculate average metrics
            avg_precision = np.mean([m['precision'] for m in self.per_class_metrics.values()])
            avg_recall = np.mean([m['recall'] for m in self.per_class_metrics.values()])
            avg_f1 = np.mean([m['f1'] for m in self.per_class_metrics.values()])

            result_summary = (f"Training completed successfully!\n"
                            f"Best Validation Accuracy: {phase2_best_accuracy:.1%}\n"
                            f"Final Validation Accuracy: {final_accuracy:.1%}\n"
                            f"Average Precision: {avg_precision:.1%}\n"
                            f"Average Recall: {avg_recall:.1%}\n"
                            f"Average F1 Score: {avg_f1:.1%}\n"
                            f"Model saved to: {final_model_path}\n"
                            f"\nFine-tuning Strategy:\n"
                            f"- Phase 1: Frozen all {sum(p.numel() for p in model.parameters()):,} params\n"
                            f"- Phase 2: Unfroze blocks {self.unfreeze_from_block}+ (~35 layers)")

            self.signals.finished.emit(result_summary)

        except Exception as e:
            error_msg = f"Training error: {str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)
            self.signals.finished.emit("failed")

        finally:
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
                self.signals.accuracy_updated,
                self.signals.fitting_warning
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