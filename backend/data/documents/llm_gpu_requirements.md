# GPU Requirements for Open-Source Large Language Models

## Table of Contents

1. [Introduction](#introduction)
2. [Understanding VRAM Requirements](#understanding-vram-requirements)
3. [Memory Requirements by Model Size](#memory-requirements-by-model-size)
4. [Inference vs. Training](#inference-vs-training)
5. [GPU Selection Guide](#gpu-selection-guide)
6. [Quantization Techniques](#quantization-techniques)
7. [Fine-Tuning with LoRA and QLoRA](#fine-tuning-with-lora-and-qlora)
8. [Multi-GPU Setup and Distributed Training](#multi-gpu-setup-and-distributed-training)
9. [Memory Optimization Strategies](#memory-optimization-strategies)
10. [Practical Hardware Configurations](#practical-hardware-configurations)

## Introduction

Running open-source Large Language Models (LLMs) requires careful consideration of GPU hardware resources. The computational and memory demands scale dramatically with model size, from billions of parameters in smaller models to hundreds of billions in large-scale systems. Understanding GPU requirements is essential for selecting appropriate hardware, whether deploying models locally, in the cloud, or for training from scratch.

The GPU serves as the primary computational accelerator for LLMs because these models perform immense numbers of mathematical operations—primarily matrix multiplications on large datasets called tensors—that GPUs excel at through their massive parallel processing capabilities. The GPU's dedicated memory, known as VRAM (Video Random Access Memory), provides fast access to model parameters, which is crucial for quick text generation and training efficiency.

## Frontier Models

### GPT-4 Series (OpenAI)

| Model             | Parameters        | Architecture                          | Context Window | Estimated Training Data | Key Features                                                |
| ----------------- | ----------------- | ------------------------------------- | -------------- | ----------------------- | ----------------------------------------------------------- |
| GPT-4 (estimated) | ~1.0-1.8 trillion | Sparse MoE with 8 experts (220B each) | 8K-128K tokens | Proprietary             | Multimodal (text, image, video); Chain-of-thought reasoning |
| GPT-4 Turbo       | ~1.0-1.8 trillion | Sparse MoE                            | 128K tokens    | Proprietary             | Extended context; Optimized inference                       |
| GPT-4o            | ~1.0-1.8 trillion | Sparse MoE                            | 128K tokens    | Proprietary             | Native multimodal; Text, image, audio processing            |
| GPT-3.5           | 175 billion       | Dense Transformer                     | 4K tokens      | ~410 billion tokens     | Lightweight; Fast inference                                 |

**GPU Requirements (GPT-4):**

- **Inference**: 4× H100 80GB minimum (estimated)
- **Training**: Not publicly available for commercial use

---

### Claude Series (Anthropic)

| Model             | Parameters (Estimated) | Architecture      | Context Window | Training Tokens | Key Features                                            |
| ----------------- | ---------------------- | ----------------- | -------------- | --------------- | ------------------------------------------------------- |
| Claude 3.5 Opus   | ~2 trillion            | Dense Transformer | 200K tokens    | ~40 trillion    | State-of-the-art reasoning; Complex multi-task handling |
| Claude 3.5 Sonnet | ~70-100 billion        | Dense Transformer | 200K tokens    | Unknown         | Balanced performance/cost; Strong coding                |
| Claude 3.5 Haiku  | ~25-30 billion         | Dense Transformer | 200K tokens    | Unknown         | Fast inference; Efficient                               |
| Claude 3 Opus     | ~2 trillion            | Dense Transformer | 200K tokens    | ~40 trillion    | Previous generation flagship                            |

**GPU Requirements (Claude Inference):**

- **Sonnet**: 2× A100 80GB or 1× H100 80GB (estimated)
- **Haiku**: 1× A100 40GB or consumer GPU with quantization

---

### Gemini Series (Google)

| Model            | Parameters (Estimated)  | Architecture          | Context Window | Training Tokens | Key Features                          |
| ---------------- | ----------------------- | --------------------- | -------------- | --------------- | ------------------------------------- |
| Gemini 2.0 Ultra | Unknown                 | MoE-based             | 1M tokens      | Unknown         | Multimodal; Robotics integration      |
| Gemini 2.0 Flash | Unknown                 | Lightweight MoE       | 1M tokens      | Unknown         | Fast; Efficient inference             |
| Gemini 1.5 Pro   | 200+ billion            | MoE Transformer       | 1M tokens      | Unknown         | Long-context breakthrough; Multimodal |
| Gemini 1.5 Flash | ~100-150 billion        | Lightweight MoE       | 1M tokens      | Unknown         | Optimized for efficiency              |
| Gemini 1.0 Ultra | 1+ trillion (estimated) | Dense/MoE Transformer | 32K tokens     | Unknown         | Previous flagship                     |

**GPU Requirements (Gemini):**

- Not publicly disclosed (proprietary infrastructure)

---

## Large Open-Source Models

### DeepSeek-V3 (Best-in-Class Efficiency)

**Core Specifications:**

- **Total Parameters**: 671 billion
- **Activated Parameters**: 37 billion per token
- **Architecture**: Mixture-of-Experts (MoE) Transformer
- **Layers**: 61 Transformer blocks
- **Hidden Dimension**: 7168
- **Attention Heads**: 128
- **Attention Mechanism**: Multi-head Latent Attention (MLA)
- **MoE Configuration**: 256 routed experts + 1 shared expert per MoE layer
- **Active Routed Experts**: 8 per token
- **Context Length**: 128K tokens
- **Training Data**: 14.8 trillion tokens
- **Training Cost**: 2.788M H800 GPU hours (~$5.6M)

**Architecture Details:**

- Multi-head Latent Attention (MLA) for efficient KV-cache compression
- DeepSeekMoE with auxiliary-loss-free load balancing
- Multi-token prediction (MTP) objective
- FP8 mixed-precision training
- RoPE positional embeddings

**GPU Requirements (Inference):**

- **FP16 (Half-Precision)**: 810-900 GB VRAM
- **FP8**: 405-450 GB VRAM (with minimal accuracy loss)
- **INT4 (4-bit quantization)**: 200-250 GB VRAM
- **Minimum Setup**:
  - 10× H100 80GB GPUs for FP8
  - 8× H100 80GB or equivalent for INT4
  - Multi-node deployment for production

**GPU Requirements (Training):**

- 2048 NVIDIA H800 GPUs (full training)
- 2.788M GPU hours for complete pre-training + fine-tuning

---

### Llama 3.1 Series (Meta)

| Model          | Parameters  | Architecture      | Hidden Dim | Layers | Attention Heads | Context Window | Training Tokens |
| -------------- | ----------- | ----------------- | ---------- | ------ | --------------- | -------------- | --------------- |
| Llama 3.1 405B | 405 billion | Dense Transformer | 16K        | 126    | 128             | 128K           | 15+ trillion    |
| Llama 3.1 70B  | 70 billion  | Dense Transformer | 8K         | 80     | 64              | 128K           | 15+ trillion    |
| Llama 3.1 8B   | 8 billion   | Dense Transformer | 4K         | 32     | 32              | 128K           | 15+ trillion    |

**Architecture Details:**

- Grouped-Query Attention (GQA) for efficiency
- Rotary Position Embeddings (RoPE)
- RMSNorm normalization
- SwiGLU activation function
- Multilingual training (8 languages)

**GPU Requirements:**

| Model | FP16   | FP8    | INT4   | Recommended Setup        |
| ----- | ------ | ------ | ------ | ------------------------ |
| 405B  | 810 GB | 405 GB | 203 GB | 10× H100 80GB (FP8)      |
| 70B   | 140 GB | 70 GB  | 35 GB  | 2× H100 80GB             |
| 8B    | 16 GB  | 8 GB   | 4 GB   | 1× A100 40GB or RTX 4090 |

---

### Qwen3 Series (Alibaba)

| Model           | Parameters  | Type  | Active Parameters | Context Window | Key Features                   |
| --------------- | ----------- | ----- | ----------------- | -------------- | ------------------------------ |
| Qwen3-235B-A22B | 235 billion | MoE   | 22 billion        | 256K → 1M      | Flagship; Reasoning mode       |
| Qwen3-30B-A3B   | 30 billion  | MoE   | 3 billion         | 128K           | Small MoE with high efficiency |
| Qwen3-32B       | 32 billion  | Dense | 32 billion        | 128K           | Competitive with 72B models    |
| Qwen3-14B       | 14 billion  | Dense | 14 billion        | 128K           | Strong mid-range performance   |
| Qwen3-8B        | 8 billion   | Dense | 8 billion         | 128K           | Efficient inference            |

**Architecture Details:**

- MoE models: Mixture of Experts with selective token routing
- Dense models: Standard Transformer with grouped-query attention
- Supports "thinking mode" for complex reasoning
- Dynamic mode switching

**GPU Requirements:**

| Model     | FP16   | FP8    | INT4   | Recommended Setup  |
| --------- | ------ | ------ | ------ | ------------------ |
| 235B-A22B | 470 GB | 235 GB | 118 GB | 6× H100 80GB (FP8) |
| 32B       | 64 GB  | 32 GB  | 16 GB  | 1× H100 80GB       |
| 14B       | 28 GB  | 14 GB  | 7 GB   | 1× A100 40GB       |

---

### Qwen2.5 Series (Alibaba)

| Model       | Parameters | Architecture      | Hidden Dim | Layers | Attention Heads | Context Window |
| ----------- | ---------- | ----------------- | ---------- | ------ | --------------- | -------------- |
| Qwen2.5-72B | 72 billion | Dense Transformer | 12288      | 80     | 128             | 131K           |
| Qwen2.5-32B | 32 billion | Dense Transformer | 8192       | 64     | 128             | 131K           |
| Qwen2.5-7B  | 7 billion  | Dense Transformer | 3584       | 28     | 128             | 131K           |

**GPU Requirements:**

| Model | FP16   | FP8   | INT4   | Recommended Setup        |
| ----- | ------ | ----- | ------ | ------------------------ |
| 72B   | 144 GB | 72 GB | 36 GB  | 2× H100 80GB             |
| 32B   | 64 GB  | 32 GB | 16 GB  | 1× H100 80GB             |
| 7B    | 14 GB  | 7 GB  | 3.5 GB | 1× A100 40GB or RTX 4090 |

---

## Medium-Sized Models

### Mistral Series

| Model         | Parameters       | Type  | Active Parameters | Context Window          | Architecture Notes                       |
| ------------- | ---------------- | ----- | ----------------- | ----------------------- | ---------------------------------------- |
| Mistral Large | ~100-200 billion | Dense | -                 | 32K                     | Advanced reasoning                       |
| Mixtral 8x22B | ~176 billion     | MoE   | 39 billion        | 65K                     | 8 experts, top-2 routing                 |
| Mixtral 8x7B  | ~47 billion      | MoE   | 13 billion        | 32K                     | Efficient; Outperforms Llama 2 70B       |
| Mistral 7B    | 7.3 billion      | Dense | 7.3 billion       | 8K (32K variants exist) | Grouped-Query & Sliding-Window Attention |

**Mistral 7B Architecture Details:**

- 32 Transformer layers
- Model dimension: 4096
- FFN dimension: 14336
- 32 attention heads (head dim: 128)
- Sliding-Window Attention (SWA) with window size 3
- Grouped-Query Attention (GQA)

**GPU Requirements:**

| Model         | FP16   | FP8    | INT4   | Recommended Setup            |
| ------------- | ------ | ------ | ------ | ---------------------------- |
| Mixtral 8x22B | 200 GB | 100 GB | 50 GB  | 2-3× H100 80GB               |
| Mixtral 8x7B  | 94 GB  | 47 GB  | 24 GB  | 1× H100 80GB or 2× A100 40GB |
| Mistral 7B    | 14 GB  | 7 GB   | 3.5 GB | 1× A100 40GB or RTX 4090     |

---

### DeepSeek-V2.5

| Specification        | Value                |
| -------------------- | -------------------- |
| Total Parameters     | 236 billion          |
| Activated Parameters | 21 billion per token |
| Architecture         | MoE Transformer      |
| Layers               | 60                   |
| Hidden Dimension     | 5120                 |
| Routed Experts       | 160                  |
| Active Experts       | 6 per token          |
| Context Length       | 128K tokens          |

**GPU Requirements (Inference):**

- **FP16**: 472 GB VRAM (estimate)
- **FP8**: 236 GB VRAM
- **Minimum Setup**: 6× H100 80GB or equivalent

---

## Efficient Models

### Phi Series (Microsoft)

| Model            | Parameters  | Architecture               | Context Window | Key Features                     |
| ---------------- | ----------- | -------------------------- | -------------- | -------------------------------- |
| Phi-4-mini       | 3.8 billion | Dense Transformer          | 128K           | Strong reasoning in compact form |
| Phi-4-multimodal | 5.6 billion | Dense Transformer + Vision | 128K           | Multimodal (text, audio, vision) |
| Phi-3-medium     | 14 billion  | Dense Transformer          | 128K           | Outperforms Gemini 1.0 Pro       |
| Phi-3-mini       | 3.8 billion | Dense Transformer          | 4K-128K        | Lightweight; Fast inference      |

**Phi-4-mini Architecture:**

- 3.8B dense decoder-only Transformer
- Grouped-Query Attention
- 200K vocabulary
- Shared input-output embeddings

**GPU Requirements:**

| Model        | FP16   | FP8    | INT4 | Recommended Setup                  |
| ------------ | ------ | ------ | ---- | ---------------------------------- |
| Phi-4-mini   | 7.6 GB | 3.8 GB | 2 GB | 1× RTX 4090 (24GB) or consumer GPU |
| Phi-3-medium | 28 GB  | 14 GB  | 7 GB | 1× A100 40GB                       |

---

### Gemma Series (Google)

| Model       | Parameters | Architecture      | Layers | Hidden Dim | Context Window |
| ----------- | ---------- | ----------------- | ------ | ---------- | -------------- |
| Gemma 3-27B | 27 billion | Dense Transformer | 39     | 4864       | 128K           |
| Gemma 2-27B | 27 billion | Dense Transformer | 39     | 4864       | 8K             |
| Gemma 2-9B  | 9 billion  | Dense Transformer | 42     | 3072       | 8K             |
| Gemma 2-2B  | 2 billion  | Dense Transformer | 18     | 2048       | 8K             |

**Gemma Architecture Innovations:**

- Interleaved local-global attention
- Grouped-Query Attention (GQA)
- Knowledge distillation for 2B & 9B models
- Sliding-window attention variants

**GPU Requirements:**

| Model       | FP16  | FP8   | INT4  | Recommended Setup                 |
| ----------- | ----- | ----- | ----- | --------------------------------- |
| Gemma 3-27B | 54 GB | 27 GB | 14 GB | 1× H100 80GB                      |
| Gemma 2-9B  | 18 GB | 9 GB  | 5 GB  | 1× A100 40GB                      |
| Gemma 2-2B  | 4 GB  | 2 GB  | 1 GB  | Consumer GPU (RTX 3090, RTX 4090) |

---

### Other Efficient Models

| Model       | Parameters | Context Window | FP16 Memory | Recommended GPU |
| ----------- | ---------- | -------------- | ----------- | --------------- |
| Llama 2-70B | 70 billion | 4K             | 140 GB      | 2× A100 80GB    |
| Llama 2-13B | 13 billion | 4K             | 26 GB       | 1× A100 40GB    |
| Llama 2-7B  | 7 billion  | 4K             | 14 GB       | RTX 4090 (24GB) |

---

## GPU Requirements Guide

### Understanding GPU Memory Calculation

**Basic Formula:**

```
Memory (GB) = Parameters (B) × Precision (bytes) × 1.2
```

Where precision in bytes:

- **FP32 (32-bit)**: 4 bytes → 1 GB per 250M parameters
- **FP16/BF16 (16-bit)**: 2 bytes → 1 GB per 500M parameters
- **INT8 (8-bit)**: 1 byte → 1 GB per 1B parameters
- **INT4 (4-bit)**: 0.5 bytes → 1 GB per 2B parameters

**The 1.2× multiplier accounts for:**

- KV-cache for context
- Activation buffers
- Temporary tensors during computation
- Memory fragmentation overhead

### GPU Specifications Reference

| GPU                     | Memory         | Memory Bandwidth | Use Case                           | Price Range  |
| ----------------------- | -------------- | ---------------- | ---------------------------------- | ------------ |
| **NVIDIA H100 SXM**     | 80 GB HBM3     | 3.35 TB/s        | Large-scale inference/training     | $30-40K/unit |
| **NVIDIA A100 SXM**     | 80 GB HBM2e    | 2.04 TB/s        | Medium-large scale inference       | $10-15K/unit |
| **NVIDIA A100 PCIe**    | 40/80 GB HBM2e | 2.04 TB/s        | Server deployments                 | $8-12K/unit  |
| **NVIDIA L40S**         | 48 GB GDDR6    | 864 GB/s         | Video processing, medium inference | $6-8K/unit   |
| **NVIDIA RTX 6000 Ada** | 48 GB          | 576 GB/s         | Professional workstations          | $6-8K/unit   |
| **NVIDIA RTX 5090**     | 32 GB GDDR7    | 1.79 TB/s        | High-end consumer (2025)           | $1,999       |
| **NVIDIA RTX 4090**     | 24 GB GDDR6X   | 1.01 TB/s        | Consumer flagship (2022)           | $1,599       |

### Inference Deployment Recommendations

**Ultra-Large Models (405B - 671B):**

- **Setup**: 8-10× H100 80GB GPUs
- **Alternative**: 16-20× A100 40GB GPUs
- **Typical Cost**: $250K-$350K hardware investment

**Large Models (70B - 150B):**

- **Setup**: 2× H100 80GB GPUs
- **Alternative**: 4× A100 40GB GPUs
- **Typical Cost**: $60K-$100K hardware investment

**Medium Models (30B - 50B):**

- **Setup**: 1× H100 80GB or 2× A100 40GB
- **Alternative**: 2-4× L40S 48GB
- **Typical Cost**: $10K-$40K hardware investment

**Small Models (7B - 14B):**

- **Setup**: 1× A100 40GB or 1× L40S 48GB
- **Consumer Alternative**: RTX 4090 24GB with quantization
- **Typical Cost**: $2K-$8K hardware investment

**Efficient Models (3B - 8B):**

- **Setup**: RTX 4090 24GB or RTX 5090 32GB
- **Alternative**: Intel Arc B580, RTX 6000
- **Typical Cost**: $500-$2K hardware investment

### Quantization Impact on Memory

| Quantization | Memory Reduction | Accuracy Impact | Speed Gain |
| ------------ | ---------------- | --------------- | ---------- |
| FP32 → FP16  | 50%              | Minimal         | 1-2%       |
| FP16 → INT8  | 75%              | Negligible      | 5-10%      |
| FP16 → INT4  | 87.5%            | 2-5%            | 15-25%     |
| FP16 → FP8   | 75%              | Negligible      | 10-15%     |

---

## Architecture Overview

### Transformer Components in Modern LLMs

**1. Attention Mechanisms:**

- **Multi-Head Attention (MHA)**: Standard attention with multiple representation subspaces
- **Grouped-Query Attention (GQA)**: Reduces KV-cache; fewer KV heads than query heads
- **Multi-head Latent Attention (MLA)**: Compresses KV pairs into low-dimensional latent space
- **Sliding-Window Attention (SWA)**: Limits attention to local window; reduces memory quadratic growth

**2. Feed-Forward Networks:**

- **Standard FFN**: Two linear transformations with activation function
- **SwiGLU Activation**: GLU variant used in Qwen models
- **Mixture of Experts (MoE)**: Sparse routing; only subset of parameters activated per token

**3. Position Encodings:**

- **RoPE (Rotary Position Embedding)**: Relative position awareness; extrapolates to longer sequences
- **Absolute Position Embeddings**: Fixed positional encodings

**4. Normalization:**

- **RMSNorm**: Root Mean Square Normalization; computationally efficient
- **LayerNorm**: Traditional normalization

### Common Architecture Patterns

**Dense Transformer (Llama, Mistral, Gemma):**

- All parameters active on every forward pass
- Predictable memory and compute requirements
- Better for single-GPU deployments
- Example: Mistral 7B, Llama 3.1 70B

**Mixture-of-Experts (DeepSeek-V3, Qwen3-235B, Mixtral):**

- Sparse routing; only top-K experts activated per token
- Reduces per-token compute while maintaining capacity
- Better for multi-GPU distributed setups
- Higher memory due to storing all expert weights
- Example: DeepSeek-V3 (671B total, 37B active), Mixtral 8x7B (47B total, 13B active)

**Multi-Token Prediction:**

- Predict multiple future tokens during training
- Improves training efficiency
- Enables speculative decoding at inference
- Example: DeepSeek-V3, upcoming models

---

## Training Considerations

### Training Memory Requirements (Approximate)

**Full Fine-Tuning:**

```
Memory ≈ Model Weights + Optimizer State + Gradients + Activations
       ≈ Params × (Precision + Optimizer) + Activation Memory
```

For a 70B model with AdamW optimizer (FP16):

- Weights: 140 GB
- Optimizer states: 140 GB
- Gradients: 140 GB
- Activations: 100-200 GB
- **Total**: 500-620 GB (requires 8× H100 80GB minimum)

**Parameter-Efficient Fine-Tuning:**

- **LoRA**: 10-20% of full training memory
- **QLoRA**: 5-10% of full training memory
- Example: 70B model with LoRA: ~80-100 GB

### Scaling Laws

Modern LLMs follow predictable scaling laws:

```
Loss ≈ a × N^(-α) + b × D^(-β) + c × C^(-γ)

Where:
- N = number of parameters
- D = number of training tokens
- C = compute (FLOPs)
- α ≈ 0.08, β ≈ 0.1, γ ≈ 0.15 (empirically derived)
```

**Practical Implication:**

- Doubling model size requires ~20% more compute to maintain quality
- Doubling training data improves loss by ~10-15%
- Optimal ratio: ~20 training tokens per parameter (increasingly refined by recent models)

---

## Emerging Trends (2025-2026)

### 1. **Mixture-of-Experts Dominance**

- More models adopting sparse routing (DeepSeek-V3, Qwen3, Gemini 1.5)
- Better efficiency-quality tradeoffs than dense models
- Enables larger model capacity on same compute

### 2. **Extended Context Windows**

- 128K → 256K → 1M+ tokens now standard
- Requires innovations in positional encodings (YaRN, NTK, etc.)
- Enables new use cases (full document processing, long-form reasoning)

### 3. **Multi-Token Prediction**

- Training objective predicting multiple future tokens
- Improves data efficiency during training
- Enables speculative decoding at inference

### 4. **FP8 Training at Scale**

- DeepSeek-V3 successfully trained entire 671B model in FP8
- 50% memory savings over FP16 without accuracy loss
- Becoming industry standard

### 5. **Reasoning-Enhanced Models**

- Extended thinking/chain-of-thought architectures
- Models like DeepSeek-R1, QwQ show capability density improvements
- Supports both fast and slow modes

### 6. **Efficient Inference Techniques**

- Flash Attention: 2-4× memory reduction
- Paged Attention: Dynamic KV-cache management
- Speculative Decoding: Accelerated token generation

## Understanding VRAM Requirements

### Why LLMs Need GPUs and High VRAM

**Parameter Storage**: All model parameters (the billions of weights and biases) need to be loaded into memory. A 7-billion parameter model in full 16-bit (FP16) precision requires approximately 14 GB of VRAM just for the weights.

**Speed of Access**: VRAM provides much faster access to model parameters than regular system RAM. This speed is critical for both training and inference performance.

**Parallel Processing Power**: GPUs can perform the necessary matrix calculations far more rapidly than CPUs, offering orders of magnitude improvement in computational throughput.

**Memory Bandwidth**: High memory bandwidth allows the GPU to move data quickly between its memory and processing units. For efficient LLM execution, bandwidth above 800 GB/s is typically desired. GPUs like the NVIDIA A100 and H100 reach these speeds, while consumer GPUs like the RTX 4090 provide approximately 1100 GB/s.

### Memory Calculation Formula

To estimate GPU memory requirements for inference:

```
Required VRAM ≈ (Model Parameters × Precision Bits) / 8 + Overhead
```

For example, a 7B parameter model in FP16 (16-bit):

- Model weights: 7,000,000,000 × 2 bytes = 14 GB
- Additional overhead for activations, batch processing, and context: 2-4 GB
- Total: approximately 16-18 GB

## Memory Requirements by Model Size

### Small Models (3B - 13B Parameters)

**Inference Requirements (FP16 precision)**:

- 3B model: ~6-8 GB VRAM
- 7B model: ~14-16 GB VRAM
- 13B model: ~26-28 GB VRAM

**Recommended GPUs**:

- NVIDIA RTX 3060 (12 GB)
- NVIDIA RTX 4070 (12 GB)
- NVIDIA RTX 3080 (10 GB)
- AMD RX 6900 XT (16 GB)

**Common Models**: LLaMA 2/3 7B, Mistral 7B, Qwen 7B

### Medium Models (30B Parameters)

**Inference Requirements (FP16 precision)**:

- 30B model: ~60-70 GB VRAM

**Recommended GPUs**:

- NVIDIA RTX 3090 (24 GB) - with memory optimization
- NVIDIA RTX 4090 (24 GB) - with memory optimization
- NVIDIA A100 (40 GB) - sufficient with headroom
- NVIDIA A6000 (48 GB)

### Large Models (65B - 70B Parameters)

**Inference Requirements (FP16 precision)**:

- 65-70B model: ~130-140 GB VRAM

**Recommended Configurations**:

- Dual NVIDIA RTX 3090/4090 (48 GB combined)
- Dual NVIDIA A6000 (96 GB combined)
- Single NVIDIA A100 (80 GB)
- Single NVIDIA H100 (80 GB)

### Very Large Models (405B Parameters and beyond)

**Inference Requirements (FP16 precision)**:

- 405B model: ~810 GB VRAM

**Recommended Configurations**:

- 10× NVIDIA RTX 3090/4090 (240 GB combined)
- 6× NVIDIA A100 80GB (480 GB combined)
- 3× NVIDIA H100 80GB (240 GB combined)

## Inference vs. Training

### Inference Requirements

Inference (running a trained model to generate text) is significantly less demanding than training. You need enough VRAM to:

1. Load the model weights
2. Store input tokens and intermediate activations
3. Generate output tokens sequentially

**Memory scaling rule**: For inference, required VRAM scales roughly linearly with model size. A 13B model requires approximately twice the VRAM of a 7B model.

**Batch Size Impact**: Running multiple requests in parallel increases memory needs. Single token-at-a-time inference is the most memory-efficient approach.

**Context Window**: Longer context windows require additional memory for storing Key-Value (KV) cache. For a 13B model with 8K context:

- KV cache at FP16: approximately 1-2 GB additional

### Training Requirements

Training requires significantly more GPU memory due to:

1. **Model weights**: Full precision parameters
2. **Gradients**: Same size as weights for backpropagation
3. **Optimizer states**: Adam optimizer requires 2× the weight storage for momentum and variance
4. **Activations**: Intermediate tensors stored for backward pass
5. **Batch processing**: Multiple samples processed simultaneously

**Rough estimation**: Full-precision training typically requires 4-6× the model size in VRAM:

- 7B model training: 28-42 GB VRAM minimum
- 70B model training: 280-420 GB VRAM minimum

**Fine-tuning vs. Full Training**: Fine-tuning a pre-trained model requires less memory than training from scratch, as you don't need to optimize all parameters. However, without memory optimization techniques, memory requirements remain substantial.

## GPU Selection Guide

### Consumer-Grade GPUs

**Advantages**:

- Significantly lower cost (5-10× cheaper than data center GPUs)
- Excellent performance-per-dollar ratio
- Easy availability and straightforward setup
- Sufficient for inference on models up to 70B parameters
- Good for rapid prototyping and development

**Disadvantages**:

- Lower memory bandwidth than data center GPUs
- Fewer reliability features (no ECC memory)
- Not designed for continuous 24/7 operation
- Limited support for multi-GPU scaling without workarounds
- Higher power consumption per FLOP

**Best Models**:

- NVIDIA RTX 4090 (24 GB VRAM, 1100 GB/s bandwidth) - Top choice for consumers
- NVIDIA RTX 3090 (24 GB VRAM, 900 GB/s bandwidth)
- NVIDIA RTX 4080 (16 GB VRAM)
- AMD RX 7900 XTX (24 GB VRAM) - with ROCm support

### Data Center GPUs

**Advantages**:

- Higher memory bandwidth (A100: 2 TB/s, H100: 3.35 TB/s)
- Better thermal management and reliability
- ECC memory for error detection
- NVLink support for efficient multi-GPU communication
- Optimized for production workloads
- Better long-term support and stability

**Disadvantages**:

- Much higher cost
- Typically purchased through cloud providers or enterprise channels
- May be overkill for inference-only deployments

**Key Models**:

- **NVIDIA A100 (40GB/80GB)**: Established workhorse with 2 TB/s memory bandwidth
- **NVIDIA H100 (80GB)**: Latest generation with 3.35 TB/s bandwidth, up to 30× better inference performance
- **NVIDIA L40S**: Inference-optimized GPU with good cost-efficiency
- **AMD MI300**: Open alternative with ROCm support

### GPU Comparison Table

| GPU Model | VRAM  | Memory Bandwidth | Use Case                       | Estimated Cost |
| --------- | ----- | ---------------- | ------------------------------ | -------------- |
| RTX 3060  | 12 GB | 360 GB/s         | Small models (up to 13B)       | $300-400       |
| RTX 4070  | 12 GB | 432 GB/s         | Small models (up to 13B)       | $500-600       |
| RTX 3090  | 24 GB | 900 GB/s         | Medium models (up to 30B)      | $1,000-1,500   |
| RTX 4090  | 24 GB | 1100 GB/s        | Large models with optimization | $1,500-2,000   |
| A100 40GB | 40 GB | 2 TB/s           | Large models (up to 70B)       | $8,000-10,000  |
| A100 80GB | 80 GB | 2 TB/s           | Very large models              | $10,000-15,000 |
| H100 80GB | 80 GB | 3.35 TB/s        | Largest models, training       | $20,000-30,000 |

## Quantization Techniques

Quantization reduces GPU memory requirements by storing model weights and activations in lower precision formats. This is one of the most effective techniques for running larger models on limited hardware.

### How Quantization Works

Quantization converts floating-point numbers (typically 32-bit or 16-bit) to lower-precision formats (typically 8-bit or 4-bit integers). This reduces memory usage while maintaining acceptable accuracy through careful scaling and calibration.

### Quantization Formats

**8-Bit Quantization (INT8)**:

- Reduces memory usage by 50% compared to FP16
- Minimal accuracy loss for most models
- Example: 7B model in FP16 (14 GB) → 7 GB in INT8
- Faster inference with modern GPU support
- Good balance between quality and efficiency

**4-Bit Quantization (INT4)**:

- Reduces memory usage by 75% compared to FP16
- Acceptable accuracy loss for inference tasks
- Example: 7B model in FP16 (14 GB) → 3.5 GB in INT4
- Can run models that wouldn't fit in VRAM otherwise
- May have slightly slower inference than 8-bit

**Advanced Quantization Schemes**:

- **NF4 (Normalized Float 4)**: Specialized 4-bit format designed for LLMs, better than standard INT4
- **GPTQ**: Post-training quantization optimized for attention-based models
- **AWQ (Activation-Aware Quantization)**: Considers activation patterns for better accuracy
- **Mixed-Precision**: Different layers quantized to different precisions based on sensitivity

### Quantization Impact on Performance

**Inference Speed**:

- 8-bit quantization typically maintains 95-100% of full-precision speed
- 4-bit quantization may reduce speed by 10-20% due to dequantization overhead

**Accuracy**:

- 8-bit: <1% perplexity increase on standard benchmarks
- 4-bit: 2-5% perplexity increase (varies by model and data)
- High-quality quantization schemes (NF4, GPTQ) minimize degradation

### Practical Examples

**LLaMA 2 7B Quantization**:

- FP16: 14 GB
- INT8: 7 GB
- INT4 (GPTQ): 3.5 GB
- 4-bit (RTX 3060 compatible): Runs comfortably on 12 GB GPU

**LLaMA 2 70B Quantization**:

- FP16: 140 GB (requires A100 80GB or 2× RTX 4090)
- INT8: 70 GB (fits on A100 40GB)
- INT4: 35 GB (fits on RTX 4090 with headroom)

## Fine-Tuning with LoRA and QLoRA

### Low-Rank Adaptation (LoRA)

LoRA is a parameter-efficient fine-tuning method that dramatically reduces memory requirements by training only small adapter layers instead of the entire model.

**How LoRA Works**:

- Freezes the original model weights
- Adds small trainable matrices (low-rank decomposition) to each layer
- Typically updates only 1-2% of parameters
- Dramatically reduces memory needed for optimizer states and gradients

**Memory Requirements with LoRA (16-bit precision)**:

- 7B model: ~16 GB VRAM (down from ~28-42 GB full training)
- Optimizer states dominate memory for the small LoRA matrices
- Batch size limited by activation memory, not weight memory

**Recommended GPUs for LoRA Fine-tuning**:

- RTX 4090 (24 GB)
- A6000 (48 GB)
- A100 40GB

### Quantized Low-Rank Adaptation (QLoRA)

QLoRA combines quantization with LoRA to achieve extreme memory efficiency. The original model is quantized to 4-bit (or 8-bit), while LoRA adapters remain in full precision.

**How QLoRA Works**:

- Loads pre-trained model in 4-bit quantization
- Adds low-rank adapters in FP16/FP32
- During training, 4-bit model is dequantized on-the-fly only when needed
- Effectively trains on quantized weights with minimal quality loss

**Memory Requirements with QLoRA (4-bit base + FP32 LoRA)**:

- 7B model: ~6-7 GB VRAM
- 13B model: ~12 GB VRAM
- 70B model: ~48 GB VRAM
- 405B model: theoretical support on multi-A100 clusters

**Breakthrough Achievement**: QLoRA enables fine-tuning of previously untrainable models on consumer hardware. A 70B parameter model can be fine-tuned on a single A100 80GB or dual RTX 4090 setup.

**Recommended GPUs for QLoRA**:

- RTX 3060 12GB (suitable for 7-13B models)
- RTX 4070 12GB (suitable for 7-13B models)
- RTX 3090 24GB (suitable for 30-70B models)
- RTX 4090 24GB (suitable for 30-70B models)
- A100 40GB (suitable for 70B+ models)

### LoRA vs. QLoRA Comparison

| Aspect               | Standard LoRA (16-bit)            | QLoRA (4-bit + LoRA)                      |
| -------------------- | --------------------------------- | ----------------------------------------- |
| 7B Model VRAM        | ~16 GB                            | ~6-7 GB                                   |
| 70B Model VRAM       | ~160 GB                           | ~48 GB                                    |
| Training Quality     | Full precision, highest quality   | Slight quality reduction, very acceptable |
| Speed                | Faster inference                  | Slightly slower (dequantization overhead) |
| Accessibility        | High-end consumer GPU needed      | Mid-range GPU sufficient                  |
| Recommended Approach | For quality-critical applications | For accessibility and cost-efficiency     |

## Multi-GPU Setup and Distributed Training

### Why Multi-GPU Training?

- **Larger Models**: Models exceeding single GPU memory capacity
- **Faster Training**: Distribute computation across multiple GPUs
- **Higher Throughput**: Process larger batch sizes
- **Data Parallelism**: Process different data on different GPUs simultaneously

### GPU Interconnect Technologies

**PCIe (PCI Express)**:

- Standard connection between GPUs and motherboard
- PCIe Gen 4: ~32 GB/s per GPU
- PCIe Gen 5: ~64 GB/s per GPU
- Sufficient for data parallelism across 2-4 GPUs
- Bottleneck for model/pipeline parallelism

**NVLink** (NVIDIA exclusive):

- Dedicated high-speed link between GPUs
- A100 NVLink: 600 GB/s
- H100 NVLink: 900 GB/s
- Essential for efficient multi-GPU training beyond 4 GPUs
- Enables 2-3× faster training on properly written code

**NVSwitch**:

- Enables full-mesh connectivity between GPUs in a server
- All GPUs can communicate at full NVLink speeds simultaneously
- Critical for scaling beyond 8 GPUs per node

### Distributed Training Strategies

**Data Parallelism (DDP)**:

- Each GPU holds the full model
- Different batches processed on different GPUs
- Gradients synchronized across GPUs
- Bandwidth requirement: 2-3× model size for gradient communication
- Works well with PCIe; NVLink provides 2-3× speedup

**Model/Tensor Parallelism (TP)**:

- Model split across multiple GPUs
- Each layer computation distributed across GPUs
- Requires high-bandwidth communication (NVLink essential)
- Enables fitting models larger than single GPU memory
- Higher communication overhead than data parallelism

**Pipeline Parallelism (PP)**:

- Model split into stages, each on a different GPU
- Sequential processing through stages
- Reduces communication overhead but can cause load imbalance
- Often combined with other strategies

**Multi-GPU Training Examples**:

For LLaMA 70B:

- Single H100 80GB: Possible with 4-bit quantization and gradient checkpointing
- 2× A100 80GB with NVLink: Efficient training with model parallelism
- 8× A100 40GB with NVLink: Very fast training with tensor and data parallelism
- 64× RTX 4090 with optimized pipeline parallelism: Achieves comparable training speed to A100 clusters

### Scaling Efficiency

Research shows:

- Perfect scaling (linear speedup) achievable up to 4-8 GPUs on same node with NVLink
- Multi-node scaling (InfiniBand) typically achieves 70-90% of linear scaling
- Communication overhead becomes dominant beyond 100+ GPUs without optimization

## Memory Optimization Strategies

### Gradient Checkpointing

Reduces activation memory at the cost of recomputation time.

**How it works**:

- Don't store all intermediate activations
- Recompute activations during backpropagation
- Reduces memory by ~50% with minimal speed penalty

**Implementation**:

- Typically 5-10% slower training
- Enables larger batch sizes that compensate for slowdown
- Net result: better throughput-to-memory ratio

**Memory savings example**: 7B model training memory reduction from 42 GB to 21 GB

### Activation Offloading

Move activations to CPU RAM during forward pass, retrieve during backward pass.

**Trade-offs**:

- Reduces GPU memory by 30-50%
- Adds PCIe bandwidth overhead
- Typically 10-20% slower
- Valuable when GPU memory is bottleneck

### Flash Attention

Optimized attention implementation with better memory efficiency.

**Benefits**:

- Reduces attention memory complexity from O(n²) to O(n)
- ~2× faster attention computation
- Enables longer sequences on same GPU memory
- Standard in modern frameworks

### Mixed Precision Training

Use lower precision (FP16 or BF16) for most computation while maintaining full precision (FP32) for loss scaling.

**Benefits**:

- ~50% memory reduction vs. FP32
- Faster computation (especially on Tensor Cores)
- Minimal accuracy impact with proper loss scaling
- Standard practice in modern training

**Implementation**:

- Automatic mixed precision (AMP) in PyTorch
- Minimal code changes required
- Recommended for all large-scale training

### KV Cache Optimization

Key-Value cache optimization for inference memory reduction.

**Standard KV Cache**:

- Grows with sequence length: Memory ∝ sequence_length × batch_size
- For 70B model with 8K sequence: ~30 GB KV cache alone

**Optimization Techniques**:

- Quantize KV to 8-bit or 4-bit: 50-75% reduction
- Sparse attention patterns: 30-50% reduction
- Eviction policies: 50-60% reduction with minimal quality loss
- Combined approaches: Up to 400× compression reported in research

## Practical Hardware Configurations

### Configuration 1: Budget Home Setup ($1,500-2,000)

**Hardware**:

- RTX 4070 (12 GB VRAM)
- Intel i7-13700K CPU
- 32 GB DDR5 RAM

**Capabilities**:

- Run 7B quantized models at full speed (100+ tokens/s)
- Run 13B quantized models at reasonable speed (30-50 tokens/s)
- Fine-tune 7B models with QLoRA
- Inference for chatbots and assistants

**Performance**: ~50-100 tokens/second on small models

### Configuration 2: Advanced Enthusiast Setup ($3,000-4,000)

**Hardware**:

- RTX 4090 (24 GB VRAM)
- Intel i9-13900K CPU
- 64 GB DDR5 RAM

**Capabilities**:

- Run 30B models with 4-bit quantization
- Run 70B models with aggressive optimization
- Fine-tune 30-70B models with QLoRA
- Batch inference for production prototypes

**Performance**: ~40-80 tokens/second on medium models, ~10-20 on large models

### Configuration 3: Small Team Research Setup ($15,000-20,000)

**Hardware**:

- Dual RTX 4090 or A6000 with NVLink bridge
- Threadripper PRO CPU
- 128 GB RAM

**Capabilities**:

- Train small models from scratch
- Fine-tune and evaluate large models at scale
- Production-grade inference on multiple models
- Research and experimentation

**Performance**: Parallel training/inference on multiple models simultaneously

### Configuration 4: Enterprise Data Center Setup ($50,000+)

**Hardware**:

- NVIDIA A100 or H100 cluster (4-8 GPUs with NVLink)
- High-end server CPUs
- Fast interconnects (InfiniBand or high-speed Ethernet)

**Capabilities**:

- Train large models from scratch
- Multi-tenant inference serving
- Large-scale fine-tuning operations
- Production SLAs (99.9%+ uptime)

**Performance**: 24/7 production-grade serving with SLA guarantees

### Configuration 5: Cloud-Based Development (Pay-as-you-go)

**Popular Providers**:

- Lambda Labs, Paperspace, RunPod, Modal
- A100/H100 GPUs at $1-3 per hour

**Advantages**:

- No upfront hardware costs
- Scale up/down as needed
- Professional support and infrastructure
- Perfect for training and research

**Cost Calculation Example**:

- Training 7B model: 24 hours on A100 = $25-75
- Fine-tuning with QLoRA: 4 hours on RTX 4090 = $10-20
- Inference during development: On-demand pricing

## Key Takeaways and Recommendations

### For Inference Only

1. **Small models (≤13B)**: RTX 4070 or RTX 3060 sufficient
2. **Medium models (30B)**: RTX 4090 or A6000 recommended
3. **Large models (70B+)**: Dual GPUs or A100/H100
4. **Always consider quantization**: 4-bit can reduce requirements by 75%

### For Fine-Tuning

1. **LoRA without quantization**: Requires significant VRAM (16GB+)
2. **QLoRA approach**: Recommended for most users; enables access to large models
3. **Batch size trade-off**: Smaller batches allow training on smaller GPUs

### For Training from Scratch

1. **Requires cluster-scale resources**: 100+ GPUs for meaningful models
2. **Not practical for individual researchers**: Use cloud providers
3. **Focus on optimization**: Gradient checkpointing, mixed precision essential

### GPU Selection Decision Tree

- **Budget under $500**: RTX 3060 (12GB) for small model inference
- **Budget $1,000-2,000**: RTX 4070 or 4080 for balanced performance
- **Budget $2,000-3,000**: RTX 4090 for most use cases
- **Professional use**: Consider A100/H100 for production deployments
- **Research/Training**: Cloud providers offer better value than ownership

### Important Considerations

- **Software matters**: Optimization frameworks (vLLM, Ollama, LM Studio) can improve performance by 2-3×
- **Driver updates**: Keep NVIDIA drivers current for best performance
- **Thermal management**: Continuous operation requires good cooling
- **Power supply**: GPU power requirements scale dramatically with model size
- **Future-proofing**: Budget for models growing 2-3× larger every 6-12 months
