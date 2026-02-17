import QtQuick 2.15

ListModel {
    ListElement { name: "llama-7b"; framework: "PyTorch"; _size: "50 MB"; accuracy: 87.3; learningRate: 0.0003; epochs: 12; status: "Ready" }
    ListElement { name: "llama-13b"; framework: "TensorFlow"; _size: "120 MB"; accuracy: 89.1; learningRate: 0.0002; epochs: 15; status: "Training" }
    ListElement { name: "mistral-7b"; framework: "PyTorch"; _size: "45 MB"; accuracy: 85.6; learningRate: 0.0004; epochs: 10; status: "Ready" }
    ListElement { name: "falcon-40b"; framework: "JAX"; _size: "320 MB"; accuracy: 91.8; learningRate: 0.0001; epochs: 20; status: "Queued" }
    ListElement { name: "phi-2"; framework: "ONNX"; _size: "20 MB"; accuracy: 82.4; learningRate: 0.0005; epochs: 8; status: "Ready" }
}
