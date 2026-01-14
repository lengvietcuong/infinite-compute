# GPU Requirements for Computer Vision Models

---

## Table of Contents

1. [GPU Specifications Reference](#gpu-specifications-reference)
2. [Object Detection Models](#object-detection-models)
3. [Image Classification Backbones](#image-classification-backbones)
4. [Vision Transformers](#vision-transformers)
5. [Semantic Segmentation Models](#semantic-segmentation-models)
6. [Instance Segmentation Models](#instance-segmentation-models)
7. [Lightweight & Mobile Models](#lightweight--mobile-models)
8. [Memory Guidelines & Best Practices](#memory-guidelines--best-practices)
9. [GPU Hardware Recommendations](#gpu-hardware-recommendations)

---

## GPU Specifications Reference

### NVIDIA Consumer GPUs

| Model    | VRAM | CUDA Cores | Tensor Cores | Memory Bandwidth | Use Case                 |
| -------- | ---- | ---------- | ------------ | ---------------- | ------------------------ |
| RTX 3060 | 12GB | 3,584      | 112          | 360 GB/s         | Budget-friendly CV tasks |
| RTX 3080 | 10GB | 8,704      | 272          | 760 GB/s         | Medium-scale training    |
| RTX 3090 | 24GB | 10,496     | 328          | 936 GB/s         | Professional CV work     |
| RTX 4070 | 12GB | 5,888      | 184          | 504 GB/s         | Balanced performance     |
| RTX 4080 | 16GB | 9,728      | 304          | 576 GB/s         | High-performance CV      |
| RTX 4090 | 24GB | 16,384     | 512          | 1,008 GB/s       | Advanced/Production      |

### NVIDIA Professional GPUs

| Model | VRAM    | CUDA Cores   | Use Case                   |
| ----- | ------- | ------------ | -------------------------- |
| A5000 | 24GB    | 8,192        | Professional deep learning |
| A6000 | 48GB    | 10,752       | Large-scale training       |
| L40   | 48GB    | 18,176       | Inference & training       |
| H100  | 80GB    | 16,896       | State-of-the-art training  |
| A100  | 40-80GB | 6,912-16,384 | Enterprise training        |

### NVIDIA Data Center GPUs

| Model | VRAM    | Use Case                         |
| ----- | ------- | -------------------------------- |
| T4    | 16GB    | Cloud inference, video analytics |
| V100  | 16-32GB | Research & training              |
| L4    | 24GB    | Cost-effective inference         |

---

## Object Detection Models

### YOLO Series

#### YOLOv8

- **Model Variants**: YOLOv8n, YOLOv8s, YOLOv8m, YOLOv8l, YOLOv8x
- **Inference VRAM**:
  - YOLOv8n: 2-4GB
  - YOLOv8s: 4-6GB
  - YOLOv8m: 6-8GB
  - YOLOv8l: 8-12GB
  - YOLOv8x: 12GB+
- **Training VRAM** (with batch size 16):
  - YOLOv8n: 4-6GB
  - YOLOv8s: 8-10GB
  - YOLOv8m: 12-16GB
  - YOLOv8l: 16-24GB
  - YOLOv8x: 24GB+
- **Recommended GPU**: RTX 3060 (12GB) minimum; RTX 4090 for production
- **Inference Speed**: ~15ms per image on RTX GPU vs ~500ms on CPU
- **Batch Processing**: Supports batch sizes 16-32 on 12-24GB GPUs

#### YOLOv12 (Latest)

- **YOLOv12-N Inference**: 1.64ms on T4 GPU
- **Performance**: 40.6% mAP with attention-centric architecture
- **Memory**: 4-8GB for inference on edge devices
- **Recommended GPU**: RTX 3060 minimum for real-time processing

#### YOLO-NAS

- **Architecture**: Neural Architecture Search variants
- **Inference VRAM**: 8-16GB depending on model size
- **Training VRAM**: 16-24GB for medium models
- **Speed**: Optimized for real-time detection

#### DAMO-YOLO

- **Model Variants**: DAMO-YOLO-T/S/M/L
- **Inference Latency on T4**:
  - T: 2.78ms
  - S: 3.83ms
  - M: 5.62ms
  - L: 7.95ms
- **Memory Profile**: 4-12GB VRAM range
- **Target**: Low-latency inference on edge devices

### Other Object Detectors

#### Faster R-CNN

- **Backbone Options**: ResNet-50/101
- **Training VRAM**: 12-16GB (batch size 2-4)
- **Inference VRAM**: 4-6GB
- **Inference Speed**: 100-300ms per image
- **Use Case**: High accuracy, moderate speed tradeoff

#### RetinaNet

- **Backbone**: ResNet-50/101
- **Training VRAM**: 12-16GB (batch size 4-8)
- **Inference VRAM**: 4-6GB
- **Focal Loss**: Better handles class imbalance
- **Speed**: ~150-250ms per image

---

## Image Classification Backbones

### ResNet Family

#### ResNet-50

- **Parameters**: 25.5M
- **Training VRAM**:
  - Batch size 32: ~10-12GB
  - Batch size 64: ~18-20GB
  - Batch size 128: 24GB+
- **Inference VRAM**: 2-4GB
- **Model Size**: ~98MB (FP32)
- **Inference Speed**:
  - GPU: ~20-50ms per image
  - CPU: ~500ms per image
- **Recommended GPU**: RTX 3060 (12GB) minimum

#### ResNet-101

- **Parameters**: 44.5M
- **Training VRAM**: 14-18GB (batch size 16-32)
- **Inference VRAM**: 4-6GB
- **Model Size**: ~170MB (FP32)
- **Recommended GPU**: RTX 4080 (16GB) or higher

#### ResNet-152

- **Parameters**: 60.2M
- **Training VRAM**: 20-24GB (batch size 8-16)
- **Inference VRAM**: 6-8GB
- **Model Size**: ~230MB (FP32)
- **Recommended GPU**: RTX 4090 or A5000

### VGG Family

#### VGG-16

- **Parameters**: 138M
- **Training VRAM**: 12-14GB (batch size 8)
- **Inference VRAM**: 4-6GB
- **Model Size**: ~528MB (FP32)
- **Note**: Larger model size and memory requirements than ResNet

#### VGG-19

- **Parameters**: 143M
- **Training VRAM**: 14-16GB (batch size 8)
- **Inference VRAM**: 6-8GB
- **Model Size**: ~548MB (FP32)

### EfficientNet Family

#### EfficientNet-B0

- **Parameters**: 5.3M
- **Training VRAM**: 4-6GB (batch size 32)
- **Inference VRAM**: 1-2GB
- **Model Size**: ~20MB
- **Advantages**: Small, fast, energy-efficient
- **Inference Speed**: 2.3x faster than ViT-B/16, 40% less memory

#### EfficientNet-B1 to B7

- **Parameters Range**: 7.8M (B1) to 66M (B7)
- **Training VRAM**:
  - B1-B3: 6-10GB
  - B4-B5: 12-16GB
  - B6-B7: 18-24GB+
- **Inference VRAM**: 2-12GB depending on variant
- **Best Performance**: EfficientNetB1 achieved 98.6% accuracy on AD detection

### Inception/GoogLeNet

#### GoogLeNet (Inception v1)

- **Parameters**: 6.6M
- **Training VRAM**: 4-6GB (batch size 32)
- **Inference VRAM**: 1-2GB
- **Inference Speed**: ~1.8ms on V100 GPU
- **Model Size**: ~26MB

#### InceptionV3

- **Parameters**: 23.9M
- **Training VRAM**: 8-10GB (batch size 16)
- **Inference VRAM**: 2-4GB
- **Model Size**: ~91MB

#### InceptionResNetV2

- **Parameters**: 55.9M
- **Training VRAM**: 12-14GB (batch size 8)
- **Inference VRAM**: 4-6GB
- **Hybrid Architecture**: ResNet + Inception modules

### DenseNet Family

#### DenseNet-121

- **Parameters**: 7.98M
- **Training VRAM**: 6-8GB (batch size 32)
- **Inference VRAM**: 2-3GB
- **Model Size**: ~30MB
- **Memory Consideration**: Feature reuse can cause quadratic memory growth if not optimized

#### DenseNet-169

- **Parameters**: 14.2M
- **Training VRAM**: 10-12GB (batch size 16)
- **Inference VRAM**: 3-5GB

#### DenseNet-201

- **Parameters**: 20.0M
- **Training VRAM**: 12-16GB (batch size 8-12)
- **Inference VRAM**: 4-6GB
- **Optimization**: Memory-efficient implementations can reduce 4.2x with quantization

---

## Vision Transformers

### ViT (Vision Transformer)

#### ViT-Base (ViT-B/16)

- **Architecture**: 12 layers, 12 attention heads, 768 hidden size
- **Parameters**: 86.6M
- **Input Resolution**: 224×224 (patch size 16)
- **Training VRAM**: 16-24GB (batch size 4-8)
- **Inference VRAM**: 8-12GB
- **Model Size**: ~330MB
- **Memory Bandwidth Requirement**: Higher than CNNs due to attention mechanisms
- **Inference Speed**: Slower than CNNs at comparable accuracy
- **Inference Speed Comparison**: ViT-B/16 2.3x slower than EfficientNet-B0

#### ViT-Large (ViT-L/16)

- **Parameters**: 304M
- **Training VRAM**: 32-40GB+
- **Inference VRAM**: 16-24GB
- **Model Size**: ~1.15GB
- **Recommended GPU**: A5000 or RTX 4090

#### ViT-Huge (ViT-H/14)

- **Parameters**: 630M
- **Training VRAM**: 40GB+ (multi-GPU recommended)
- **Inference VRAM**: 24GB+
- **Model Size**: ~2.4GB
- **Recommended GPU**: A100 (40GB) or H100

### DeiT (Data-efficient Image Transformers)

#### DeiT-Tiny

- **Parameters**: 5.7M
- **Training VRAM**: 4-6GB
- **Inference VRAM**: 1-2GB
- **Knowledge Distillation**: Enables training with smaller datasets

#### DeiT-Small

- **Parameters**: 22.1M
- **Training VRAM**: 8-12GB
- **Inference VRAM**: 4-6GB

#### DeiT-Base

- **Parameters**: 86.6M
- **Training VRAM**: 16-24GB
- **Inference VRAM**: 8-12GB

### Swin Transformer

#### Swin-Tiny

- **Parameters**: 28.3M
- **Training VRAM**: 10-14GB
- **Inference VRAM**: 5-8GB
- **Advantages**: Hierarchical structure, local window attention
- **Better Memory Efficiency**: Compared to ViT-Base

#### Swin-Small

- **Parameters**: 49.6M
- **Training VRAM**: 16-22GB
- **Inference VRAM**: 8-12GB

#### Swin-Base

- **Parameters**: 87.8M
- **Training VRAM**: 24-32GB
- **Inference VRAM**: 12-16GB

### Other Vision Transformer Variants

#### BEiT (BERT Pre-training of Image Transformers)

- **Self-supervised pretraining** approach
- **Parameters**: Similar to ViT variants
- **Training VRAM**: 20-40GB (with masked image modeling)
- **Benefits**: Better transfer learning performance

#### MAE (Masked Autoencoders)

- **Pretraining Strategy**: Mask 75% of patches
- **Training VRAM**: 24-40GB
- **Memory Efficient**: Compared to supervised pretraining
- **Fine-tuning VRAM**: 16-24GB

---

## Semantic Segmentation Models

### FCN (Fully Convolutional Networks)

#### FCN-8, FCN-16, FCN-32

- **Backbone**: VGG-16 variant
- **Training VRAM**: 8-10GB
- **Inference VRAM**: 4-6GB
- **Input Resolution**: 224×224 to 500×500
- **GPU Memory (224×224)**: ~1.2GB on GTX 1080 Ti
- **Speed**: Fast inference, moderate accuracy

### U-Net

#### U-Net (2D)

- **Parameters**: ~7.76M (encoder-decoder)
- **Training VRAM**: 6-8GB (batch size 4-8)
- **Inference VRAM**: 2-4GB
- **Model Size**: ~30MB
- **Typical Input**: 512×512 patches
- **Memory (512×512)**: 6-8GB for training with batch size 2

#### U-Net++ (Nested)

- **Enhanced Architecture**: Multiple decoder paths
- **Training VRAM**: 8-10GB (batch size 4)
- **Inference VRAM**: 4-6GB
- **Improved Accuracy**: At cost of increased memory

#### 3D U-Net

- **For Medical Imaging**: Volumetric data
- **Training VRAM**: 12-16GB (batch size 1-2)
- **Inference VRAM**: 6-8GB
- **Input Typical**: 128×128×128 volumes

### DeepLab Family

#### DeepLabV3

- **Backbone Options**: ResNet-50/101, MobileNet
- **ASPP Module**: Multi-scale feature extraction
- **Training VRAM** (ResNet-50 backbone):
  - Input 512×512: 16-20GB
  - Input 256×256: 10-12GB
- **Inference VRAM**: 6-8GB (ResNet-50)
- **GPU Memory (224×224)**: ~1.2GB on GTX 1080 Ti
- **Inference Speed**: Slightly slower than FCN

#### DeepLabV3+

- **Enhanced Decoder**: Skip connections
- **Training VRAM**: 18-24GB (ResNet-50, 512×512 input)
- **Inference VRAM**: 8-10GB
- **Advantages**: Better boundary segmentation than V3

#### DeepLab with MobileNet

- **Lightweight Option**: MobileNet backbone
- **Training VRAM**: 4-6GB
- **Inference VRAM**: 2-3GB
- **Real-time Performance**: Mobile/edge device capable

### PSPNet (Pyramid Scene Parsing Network)

#### PSPNet-ResNet-50

- **Pyramid Pooling Module**: Multi-scale context
- **Training VRAM**: 14-18GB (batch size 4)
- **Inference VRAM**: 6-8GB
- **Input Resolution**: 473×473 optimal
- **Advantages**: Captures global context

#### PSPNet-ResNet-101

- **Deeper Backbone**: More parameters
- **Training VRAM**: 18-24GB (batch size 2-4)
- **Inference VRAM**: 8-10GB

### FastFCN

- **Optimization**: Joint Pyramid Upsampling
- **Training VRAM**: 10-12GB
- **Inference VRAM**: 5-6GB
- **Speed Improvement**: Addresses DeepLab's dilated convolution bottleneck
- **Memory Efficient**: Reduced spatial dimension growth

---

## Instance Segmentation Models

### Mask R-CNN

#### Mask R-CNN with ResNet-50

- **Training VRAM**: 12-16GB (batch size 2)
- **Inference VRAM**: 6-8GB
- **Inference Speed**: 5 FPS on GTX 1080
- **Architecture**: ResNet-50 + FPN + RPN + ROI Align + Mask Head
- **Model Size**: ~165MB

#### Mask R-CNN with ResNet-101

- **Training VRAM**: 18-24GB (batch size 1-2)
- **Inference VRAM**: 8-12GB
- **Inference Speed**: 3-4 FPS on GTX 1080

#### Optimized Mask R-CNN

- **NVIDIA Implementation**: 1.3x faster training with mixed precision
- **Tensor Core Utilization**: Volta/Turing/Ampere architectures
- **Training VRAM**: 10-12GB with optimization (batch size 2-4)

### Cascade R-CNN

- **Architecture**: Series of R-CNN heads with increasing IoU thresholds
- **Training VRAM**: 16-20GB (batch size 2)
- **Inference VRAM**: 8-10GB
- **Performance**: Higher accuracy than Mask R-CNN

### RetinaMask (RetinaNet + Mask Head)

- **Training VRAM**: 10-14GB
- **Inference VRAM**: 5-8GB
- **Speed**: Faster than Mask R-CNN

---

## Lightweight & Mobile Models

### MobileNet Family

#### MobileNetV2

- **Parameters**: 3.5M
- **Training VRAM**: 2-4GB (batch size 32-64)
- **Inference VRAM**: 500MB-1GB
- **Model Size**: ~14MB
- **Target**: Mobile phones, edge devices
- **Inference Speed**: Real-time on mobile GPUs

#### MobileNetV3-Small

- **Parameters**: 2.5M
- **Training VRAM**: 2GB (batch size 128)
- **Inference VRAM**: 300-500MB
- **Model Size**: ~10MB
- **Architecture Search**: NAS-optimized for mobile

#### MobileNetV3-Large

- **Parameters**: 5.4M
- **Training VRAM**: 4GB (batch size 32)
- **Inference VRAM**: 1GB
- **Model Size**: ~21MB

#### MobileNetV4

- **Universal Architecture**: Optimized for CPU, DSP, GPU, accelerators
- **Parameters**: Multiple variants from 3.8M to 38M
- **Training VRAM**: 2-8GB range
- **Pareto Optimal**: Across different hardware platforms

### ShuffleNet

#### ShuffleNetV2

- **Parameters**: 2.3M (Small)
- **Training VRAM**: 2-4GB
- **Inference VRAM**: 500MB-1GB
- **Channel Shuffle**: Memory-efficient feature mixing
- **Target**: Mobile deployment

### SqueezeNet

- **Parameters**: 1.2M
- **Training VRAM**: 1-2GB
- **Inference VRAM**: 256-512MB
- **Model Size**: ~5MB
- **Fire Module**: Compression through strategic dimensionality reduction

### TinyNet

- **Minimal Parameters**: <1M
- **Training VRAM**: 1GB
- **Inference VRAM**: 128-256MB
- **Model Size**: <4MB
- **Target**: Embedded systems, IoT devices

---

## Memory Guidelines & Best Practices

### Memory Requirements Formula

```
Training Memory =
  (Model Parameters × Precision Bytes) × 2.5 +
  (Batch Size × Input Size × Precision Bytes) +
  (Optimizer State Memory)

Inference Memory =
  (Model Parameters × Precision Bytes) +
  (Batch Size × Input Size × Precision Bytes)
```

### Data Type Memory Footprint

| Precision        | Bytes per Parameter | Memory Reduction |
| ---------------- | ------------------- | ---------------- |
| FP32 (Float32)   | 4 bytes             | Baseline         |
| FP16 (Float16)   | 2 bytes             | 50% reduction    |
| INT8 (Quantized) | 1 byte              | 75% reduction    |
| INT4 (Quantized) | 0.5 bytes           | 87.5% reduction  |
| BF16 (BFloat16)  | 2 bytes             | 50% reduction    |

### Mixed Precision Training

- **FP16 + FP32**: Combines speed of FP16 with stability of FP32
- **Memory Savings**: ~50% reduction in forward pass, ~25% overall
- **Speed Improvement**: 2-3x faster on Tensor Core-equipped GPUs
- **Loss Scaling**: Prevents gradient underflow

### Batch Size Impact on Memory

- Memory usage scales **linearly** with batch size
- Doubling batch size roughly doubles intermediate activation memory
- Recommended batch sizes by GPU:
  - 4GB GPU: Batch size 2-4
  - 8GB GPU: Batch size 4-8
  - 12GB GPU: Batch size 8-16
  - 16GB GPU: Batch size 16-32
  - 24GB GPU: Batch size 32-64

### System RAM Requirements

- **Rule of Thumb**: System RAM ≥ GPU VRAM × 1.25
- **Recommended Configurations**:
  - 8GB GPU VRAM → 16GB System RAM (2 cores)
  - 12GB GPU VRAM → 16-32GB System RAM (4-8 cores)
  - 24GB GPU VRAM → 32-48GB System RAM (8-16 cores)
  - 40GB+ GPU VRAM → 64GB+ System RAM (16+ cores)
- **Data Pipeline**: CPU preprocesses images/data before GPU consumption

### CPU Core Recommendations

- **Basic**: 4-6 cores @ 3.5 GHz
- **Intermediate**: 8 cores @ 3.5+ GHz
- **Advanced**: 16+ cores @ 3.5+ GHz with 25MB+ L3 cache
- **Effect**: Prevents CPU bottleneck during data loading

### Optimization Techniques

#### Gradient Checkpointing

- **Memory Savings**: 25-40% reduction
- **Trade-off**: Slight computational overhead (~20% slower)
- **Best For**: Training large models on memory-constrained GPUs
- **Implementation**: PyTorch `torch.utils.checkpoint` or TensorFlow `tf.recompute_grad`

#### Model Pruning

- **Structured Pruning**: Remove entire channels/filters
  - Memory: 2-4x reduction possible
  - Speed: Proportional speedup
- **Unstructured Pruning**: Remove individual weights
  - Memory: 4-10x reduction
  - Speed: Limited without special hardware

#### Quantization

- **Post-Training Quantization**: 4x memory reduction (FP32→INT8)
- **Quantization-Aware Training**: Better accuracy, similar compression
- **INT4 Quantization**: 8x memory reduction
- **Minimal Accuracy Loss**: <1% in most cases with proper calibration

#### Knowledge Distillation

- **Teacher-Student**: Smaller student model learns from larger teacher
- **Model Size**: 10-50x compression possible
- **Training Overhead**: Requires teacher model during training

#### Low-Rank Adaptation (LoRA)

- **Fine-tuning**: Fewer parameters to train than full fine-tune
- **Memory**: 50-90% reduction in training memory
- **Parameter Efficiency**: 0.5-5M additional parameters vs 1M+ for full fine-tune

### Input Resolution Impact

- Memory scales **quadratically** with image size
- Common resolutions and relative memory use:
  - 224×224: 1x baseline
  - 256×256: 1.3x
  - 384×384: 2.9x
  - 512×512: 5.1x
  - 1024×1024: 20.5x

---

## GPU Hardware Recommendations

### Beginner/Research Setup

- **GPU**: NVIDIA RTX 3060 or RTX 4070
- **GPU Memory**: 12GB
- **System RAM**: 16GB
- **Use Cases**: Learning, small model training, inference
- **Estimated Cost**: $300-500

### Intermediate Professional Setup

- **GPU**: NVIDIA RTX 4080 or A5000
- **GPU Memory**: 16-24GB
- **System RAM**: 32GB
- **CPU**: 8-core processor @ 3.5GHz
- **Use Cases**: Production model training, real-time inference
- **Estimated Cost**: $1,500-4,000

### Advanced Production Setup

- **GPU**: NVIDIA RTX 4090 or A6000
- **GPU Memory**: 24-48GB
- **System RAM**: 64GB
- **CPU**: 16+ core processor @ 3.5GHz
- **Storage**: NVMe SSD for data pipeline
- **Use Cases**: Large-scale training, multi-GPU setups
- **Estimated Cost**: $3,000-8,000

### Multi-GPU Distributed Training

- **Configuration**: 2-8 GPUs with NVLink
- **Recommended**: A100 40GB or H100 80GB
- **Interconnect**: NVLink for 600 GB/s bandwidth vs PCIe 4.0 (32 GB/s)
- **Framework**: PyTorch DDP, TensorFlow MultiGPU, Horovod
- **Typical Setup**: Cost $10,000-50,000+

### Cloud GPU Options (as of 2025)

- **Entry-level**: T4 (16GB) - $0.20-0.40/hour
- **Mid-tier**: RTX 4090 (24GB) - $1.50-3.00/hour
- **Enterprise**: A100 (40GB) - $2.00-4.00/hour
- **High-end**: H100 (80GB) - $3.00-5.00/hour

---

## Framework-Specific Recommendations

### PyTorch

- **Optimal GPU Memory**: 8GB+ for moderate models
- **Mixed Precision**: `torch.cuda.amp.autocast()` context manager
- **Batch Processing**: `.to(device)` for GPU transfer
- **Multi-GPU**: `torch.nn.DataParallel` or `DistributedDataParallel`

### TensorFlow/Keras

- **Optimal GPU Memory**: 8GB+ for model training
- **Mixed Precision**: `tf.keras.mixed_precision.Policy`
- **Strategy**: `tf.distribute.MirroredStrategy` for single-machine multi-GPU
- **XLA Compilation**: Further optimization with `jit_compile=True`

### CUDA Compatibility

- **Minimum**: CUDA 11.2 for modern models
- **Recommended**: CUDA 12.x with latest cuDNN (v9+)
- **Driver**: Ensure NVIDIA driver ≥ 535.x for RTX 40 series

---

## Benchmark Summary Table

| Model           | Parameters | Training VRAM | Inference VRAM | Inference Speed (RTX 3090) | Typical Accuracy    |
| --------------- | ---------- | ------------- | -------------- | -------------------------- | ------------------- |
| YOLOv8n         | 3.2M       | 4-6GB         | 2-4GB          | ~50 FPS                    | ~80% AP             |
| YOLOv8m         | 25.9M      | 12-16GB       | 6-8GB          | ~25 FPS                    | ~85% AP             |
| ResNet-50       | 25.5M      | 10-12GB       | 2-4GB          | ~100 FPS                   | ~76% Top-1          |
| EfficientNet-B0 | 5.3M       | 4-6GB         | 1-2GB          | ~150 FPS                   | ~77% Top-1          |
| ViT-Base        | 86.6M      | 16-24GB       | 8-12GB         | ~30 FPS                    | ~77% Top-1          |
| DenseNet-121    | 7.98M      | 6-8GB         | 2-3GB          | ~80 FPS                    | ~75% Top-1          |
| MobileNetV3     | 5.4M       | 4GB           | 1GB            | ~200 FPS                   | ~75% Top-1          |
| Mask R-CNN-50   | 44.2M      | 12-16GB       | 6-8GB          | ~5 FPS                     | ~37% AP             |
| DeepLabV3-50    | 39.7M      | 14-18GB       | 6-8GB          | ~20 FPS                    | ~78% mIoU           |
| U-Net           | 7.76M      | 6-8GB         | 2-4GB          | ~60 FPS                    | ~92% Dice (medical) |

---

## Conclusion & Selection Guidelines

1. **Inference-focused**: Choose models with <8GB inference VRAM (EfficientNet, MobileNet, YOLO)
2. **Training-focused**: Prioritize 16-24GB GPU VRAM with good CPU support (ResNet, EfficientNet)
3. **Real-time applications**: YOLO variants or lightweight models with <50ms latency
4. **Maximum accuracy**: ResNet-101+, Vision Transformers, or ensemble models
5. **Mobile deployment**: MobileNetV3, YOLO-tiny, TinyNet (<2GB model size)
6. **Medical imaging**: U-Net variants, DeepLabV3 with preprocessing optimization
7. **Edge devices**: <4GB inference VRAM requirement models with quantization