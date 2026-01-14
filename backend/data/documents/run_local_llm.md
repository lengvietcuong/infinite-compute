# Running Large Language Models Locally with NVIDIA GPUs

## Table of Contents

1. [Prerequisites and System Requirements](#prerequisites-and-system-requirements)
2. [NVIDIA CUDA Setup](#nvidia-cuda-setup)
3. [Choosing Your Inference Framework](#choosing-your-inference-framework)
4. [Model Quantization Techniques](#model-quantization-techniques)
5. [Installation and Configuration](#installation-and-configuration)
6. [Running Your First LLM](#running-your-first-llm)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting and Best Practices](#troubleshooting-and-best-practices)

---

## Prerequisites and System Requirements

### Hardware Requirements

Before attempting to run LLMs locally with NVIDIA GPUs, ensure you have the following:

**GPU Specifications:**

- **NVIDIA GPU**: GeForce RTX series (20, 30, 40, or 50 series) or professional-grade GPUs (A100, A6000, H100)
- **Minimum VRAM**: 4-6GB for 1.5B parameter models; 8-12GB for 7B models; 16GB+ for larger models
- **Note**: NVIDIA CUDA support is essential; AMD or Intel GPUs require different toolchains

**System RAM:**

- At minimum, 1.5-2x the amount of VRAM available on your GPU
- Example: For a GPU with 12GB VRAM, maintain 18-24GB of system RAM
- This allows for model weights, activations, and temporary data structures

**Storage:**

- 50-100GB free disk space for model files and dependencies
- SSDs are strongly recommended for faster model loading

**Operating System:**

- Windows 10/11
- Ubuntu 20.04 or newer
- macOS (for older GPU models; newer Macs use Apple Silicon instead)

### Verify NVIDIA GPU Compatibility

```bash
# Check if NVIDIA GPU is detected (Windows Command Prompt)
nvidia-smi

# Check if NVIDIA GPU is detected (Linux/macOS Terminal)
nvidia-smi
```

If this command returns GPU information, your system is NVIDIA-compatible. If not, you'll need to install or update NVIDIA drivers.

---

## NVIDIA CUDA Setup

### Step 1: Update NVIDIA Drivers

Visit [NVIDIA's official driver download page](https://www.nvidia.com/Download/driverDetails.aspx) and download the latest driver for your GPU model and operating system.

**Installation:**

- **Windows**: Run the executable installer and follow the on-screen instructions. Restart your computer after installation.
- **Linux**: Use your package manager or NVIDIA's official CUDA installer

Verify the installation:

```bash
nvidia-smi
```

Expected output shows your GPU model, CUDA Compute Capability, and available VRAM.

### Step 2: Install CUDA Toolkit

Download the **CUDA Toolkit 12.x** or newer from [NVIDIA Developer Tools](https://developer.nvidia.com/cuda-toolkit-archive).

**For Windows:**

1. Download the local installer (`.exe`)
2. Run the installer
3. During installation, ensure you select:
   - CUDA Toolkit
   - CUDA Samples
   - CUDA Documentation (optional)
   - Visual Studio Integration (if you have Visual Studio installed)

**For Linux (Ubuntu 22.04 example):**

```bash
# Download CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda_12.4.0_550.54.14_linux.run

# Run the installer
sudo sh cuda_12.4.0_550.54.14_linux.run

# Follow the on-screen prompts
```

### Step 3: Set Environment Variables

**For Windows:**

1. Open Environment Variables (search "Environment Variables" in Start Menu)
2. Add the following to your PATH:
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\libnvvp
   ```
3. Create new environment variables:
   - `CUDA_HOME`: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4`
   - `CUDA_PATH`: Same as CUDA_HOME

**For Linux:**
Add to your `~/.bashrc` file:

```bash
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export CUDA_HOME=/usr/local/cuda
```

Then apply changes:

```bash
source ~/.bashrc
```

### Step 4: Verify CUDA Installation

```bash
# Check CUDA version
nvcc --version

# Test CUDA with a simple check
nvidia-smi
```

Both commands should complete without errors.

### Step 5: Install cuDNN (Optional but Recommended)

cuDNN (CUDA Deep Neural Network library) accelerates deep learning operations.

1. Download cuDNN from [NVIDIA Developer Portal](https://developer.nvidia.com/cudnn) (requires free account)
2. Extract the archive
3. Copy files to your CUDA installation directory:
   - Copy contents of `bin/` to `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin`
   - Copy contents of `include/` to `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\include`
   - Copy contents of `lib/` to `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\lib`

---

## Choosing Your Inference Framework

### Comparison of Popular Frameworks

Three primary frameworks dominate local LLM inference on NVIDIA GPUs:

#### 1. **llama.cpp**

- **Best for**: Flexible, hybrid CPU/GPU inference
- **Quantization formats**: GGUF (primary), with support for multiple compression levels
- **Performance**: Excellent single-GPU performance; supports layer offloading to CPU
- **Use cases**: Resource-constrained setups, CPU fallback capability
- **Community**: Very active; frequent performance optimizations

#### 2. **Ollama**

- **Best for**: Beginners; ease of use prioritized over performance
- **Setup**: Simplest to get started; one-command model loading
- **Model switching**: Automatic model unloading when switching between models
- **Performance**: Built on llama.cpp; slightly higher overhead than raw llama.cpp
- **Limitations**: Not ideal for multi-concurrent-user production environments
- **Use cases**: Casual experimentation, local development, single-user deployments

#### 3. **vLLM**

- **Best for**: High-throughput, multi-user production environments
- **Performance**: Highest throughput with concurrent requests; dynamic batching optimizes resource usage
- **Concurrency**: Excels with 25+ simultaneous users
- **Limitations**: Requires model to fit entirely in GPU VRAM; no CPU offloading
- **Quantization**: Supports GPTQ and AWQ; challenging for lower-end GPUs
- **Use cases**: API servers, multi-user applications, data centers

#### Benchmark Comparison (NVIDIA A6000, 48GB VRAM, Llama-2-7B-Chat):

- **Single request**: vLLM: 0.65s | Ollama: 0.76s
- **25 concurrent users**: vLLM: 2.95s/request (8.41 req/s) | Ollama: 16.79s/request (1.31 req/s)

**Recommendation Decision Tree:**

- GPU with limited VRAM (≤12GB) → **llama.cpp or Ollama**
- Single user or CPU fallback needed → **llama.cpp**
- Casual experimentation → **Ollama**
- Production with multiple concurrent users → **vLLM**

---

## Model Quantization Techniques

Quantization reduces model size and improves inference speed by using lower-precision representations. Understanding quantization is crucial for efficient local inference.

### Why Quantization Matters

- **7B parameter model in FP32**: ~28GB storage and VRAM
- **7B parameter model in INT4**: ~3.5GB storage and VRAM
- **Speed improvement**: 2-5x faster inference on GPUs with optimized kernels
- **Accuracy impact**: Minimal to none with modern quantization methods

### Quantization Methods for NVIDIA GPUs

#### 1. **GGUF (GGML Universal Format)** - Best for CPU/Hybrid

**When to use**: CPU-only or when GPU cannot fit the full model

**Quantization levels** (ordered by precision/size):

- `IQ2_XXS`: Extra-extra-small, extreme compression (~2-bit equivalent)
- `IQ3_S`: Ultra-compact, best for very limited resources
- `Q4_K_S`: Aggressive 4-bit, smallest file size
- **`Q4_K_M`**: Recommended balance (most popular choice)
- `Q5_K_S`: High quality 5-bit, slightly smaller
- **`Q5_K_M`**: Excellent quality/size tradeoff
- `Q6_K`: Premium quality, larger files
- `Q8_0`: Near-original quality, substantial file size

**K-quants explanation**: The "K" indicates mixed-precision quantization. Critical weights receive higher precision (e.g., 6-bit), while less important weights use lower precision (e.g., 4-bit). This intelligently preserves model quality while maintaining compression.

**Conversion example** (using llama.cpp):

```bash
# Convert model to FP16 first
python llama.cpp/convert.py path/to/model --outtype f16 --outfile model.fp16.bin

# Quantize to Q4_K_M
./llama.cpp/quantize model.fp16.bin model.Q4_K_M.gguf q4_k_m
```

#### 2. **GPTQ (Generalized Post-Training Quantization)** - GPU Optimized

**When to use**: NVIDIA GPU with sufficient VRAM; prioritize GPU inference speed

**Characteristics**:

- Excellent accuracy at very low bit widths (2-4 bits)
- ~5x faster than GGUF on GPU with optimized kernels like Marlin
- Requires calibration dataset during quantization (quality depends on calibration data)
- Quantization process is time-intensive for large models
- Limited to single model per instance (cannot switch models easily)

**Installation**:

```bash
pip install auto_gptq optimum[exporters] transformers accelerate
```

**Quantization code** (example):

```python
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer

model_name = "mistralai/Mistral-7B"
quantize_config = BaseQuantizeConfig(
    bits=4,
    group_size=128,
    damp_percent=0.1
)

# Load and quantize
model = AutoGPTQForCausalLM.from_pretrained(
    model_name,
    quantize_config,
    device_map="auto"
)

# Provide calibration data
tokenizer = AutoTokenizer.from_pretrained(model_name)
calibration_prompts = [
    "Artificial intelligence is...",
    "Machine learning enables...",
    # Include 100-500 diverse examples
]
calibration_data = [tokenizer(p, return_tensors="pt") for p in calibration_prompts]

# Quantize
model.quantize(calibration_data)
model.save_quantized("model-gptq")
```

#### 3. **AWQ (Activation-Aware Weight Quantization)** - Cutting Edge

**When to use**: NVIDIA GPU; balance speed, quality, and ease of calibration

**Characteristics**:

- Activation-aware: identifies and protects important weights
- Maintains model accuracy better than GPTQ at same bit-width
- Faster quantization than GPTQ; requires less calibration data
- Excellent for instruction-tuned and multi-modal models
- Often 2-3x faster than GPTQ with good optimization

**Installation**:

```bash
pip install autoawq
```

**Quantization example**:

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = "mistralai/Mistral-7B"
model = AutoAWQForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM"  # or "exllama" for specific kernels
}

# Load small calibration dataset (128-256 examples)
from datasets import load_dataset
calibration_data = load_dataset("wikitext", "wikitext-2-v1", split="train[:128]")

# Quantize
model.quantize(tokenizer, quant_config=quant_config)
model.save_quantized("model-awq")
```

### VRAM Requirements by Model Size and Precision

Using the formula: **VRAM (GB) = (Parameters × Precision Bytes × 1.2) / 10^9**

| Model Size | FP32  | FP16/BF16 | INT8 | INT4 (GPTQ/AWQ) | INT4 (GGUF Q4_K_M) |
| ---------- | ----- | --------- | ---- | --------------- | ------------------ |
| 1.5B       | 6GB   | 3GB       | 2GB  | 1.5GB           | 0.8-1GB            |
| 7B         | 28GB  | 14GB      | 8GB  | 5-6GB           | 4-5GB              |
| 13B        | 52GB  | 26GB      | 14GB | 8-10GB          | 8-9GB              |
| 32B        | 128GB | 64GB      | 36GB | 20-24GB         | 18-20GB            |
| 70B        | 280GB | 140GB     | 70GB | 40-48GB         | 35-40GB            |

---

## Installation and Configuration

### Option 1: Using LM Studio (Easiest for Beginners)

LM Studio is a user-friendly desktop application built on llama.cpp with NVIDIA optimization.

**Installation**:

1. Download from [LM Studio official website](https://lmstudio.ai)
2. Install for your operating system (Windows, macOS, or Linux)
3. Launch the application

**First Run Setup**:

1. Click the magnifying glass icon to open the Discover menu
2. Navigate to Runtime settings
3. Search for "CUDA 12 llama.cpp (Windows)" or appropriate platform
4. Click Download and Install
5. Set as default runtime in Dropdown selections

**Loading a Model**:

1. Search for a model (e.g., "llama2", "mistral", "neural-chat")
2. Click Download
3. Once downloaded, click Load in the chat interface

**GPU Optimization**:

1. Load a model
2. Click the gear icon next to the model name
3. Toggle "Flash Attention" to ON
4. Drag "GPU Offload" slider fully to the right

**27% Performance Improvement** with latest CUDA 12.8, Flash Attention, and GPU layer offloading.

### Option 2: Using Ollama (Quick Start)

Ollama simplifies model management with minimal configuration.

**Installation**:

```bash
# Windows: Download installer from https://ollama.ai

# macOS:
# Download from https://ollama.ai

# Linux:
curl -fsSL https://ollama.ai/install.sh | sh
```

**Run a Model**:

```bash
# Download and run in one command
ollama run llama2

# Run specific version
ollama run mistral:7b

# List available models
ollama list

# Stop running model
ollama stop
```

**Create Custom Modelfile**:

```dockerfile
FROM mistral:7b

PARAMETER temperature 0.7
PARAMETER num_ctx 4096
SYSTEM "You are a helpful coding assistant."
```

Save as `Modelfile` and run:

```bash
ollama create my-custom-model -f ./Modelfile
ollama run my-custom-model
```

### Option 3: Using llama.cpp Directly (Most Control)

**Clone and Build**:

```bash
# Clone repository
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build with CUDA support (Windows)
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release

# Build with CUDA support (Linux)
make LLAMA_CUDA=1

# Build with GPU offloading optimization (Linux)
make LLAMA_CUDA=1 -j$(nproc)
```

**Download a Model**:

```bash
# Use Hugging Face CLI
pip install huggingface_hub

# Download GGUF format model (Q4_K_M is recommended)
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.1-GGUF mistral-7b-instruct-v0.1.Q4_K_M.gguf --local-dir . --local-dir-use-symlinks False
```

**Run Inference via CLI**:

```bash
# Basic inference
./main -m mistral-7b-instruct-v0.1.Q4_K_M.gguf -p "Explain quantum computing" -n 256

# Optimized for GPU with full layer offloading
./main -m mistral-7b-instruct-v0.1.Q4_K_M.gguf \
  -ngl 32 \
  -p "Your prompt here" \
  -n 256 \
  -t 8 \
  --mlock \
  --gpu-layers 32

# Interactive chat
./main -m mistral-7b-instruct-v0.1.Q4_K_M.gguf \
  -i \
  -p "You are a helpful assistant." \
  -n 256 \
  -ngl 32 \
  -t 8
```

### Option 4: Using vLLM (Production Serving)

**Installation**:

```bash
pip install vllm
```

**Run vLLM Server**:

```bash
# Basic server
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.1 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.9

# With quantization (GPTQ example)
python -m vllm.entrypoints.openai.api_server \
  --model TheBloke/Mistral-7B-Instruct-v0.1-GPTQ \
  --quantization gptq \
  --gpu-memory-utilization 0.9
```

**Query the API**:

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/completions",
    json={
        "model": "mistral-7b",
        "prompt": "Explain machine learning in simple terms",
        "max_tokens": 256,
        "temperature": 0.7
    }
)
print(response.json())
```

---

## Running Your First LLM

### Step-by-Step with LM Studio

1. **Install and launch LM Studio**
2. **Download a model**: Click Discover → Search "Llama 2 7B" → Download Q4_K_M version
3. **Load the model**: Click Load in chat interface
4. **Start chatting**: Type in the message box and wait for response
5. **Verify GPU usage**: Open Task Manager (Windows) → GPU tab should show activity

### Step-by-Step with Ollama

```bash
# Pull a model
ollama pull mistral:7b

# Run it
ollama run mistral:7b

# Type your prompt
> What is machine learning?
```

### Step-by-Step with llama.cpp

```bash
# Create directory for models
mkdir models && cd models

# Download a GGUF quantized model
huggingface-cli download TheBloke/Llama-2-7B-chat-GGML llama-2-7b-chat.Q4_K_M.gguf --local-dir .

# Run inference
cd .. # Back to llama.cpp directory
./main -m models/llama-2-7b-chat.Q4_K_M.gguf \
  -n 256 \
  -ngl 32 \
  -p "What is artificial intelligence?" \
  --color
```

---

## Performance Optimization

### GPU-Specific Optimizations

#### Enable Flash Attention (15% throughput boost)

```bash
# In LM Studio: Toggle "Flash Attention" in model settings

# In llama.cpp: Add -fa flag
./main -m model.gguf -fa -ngl 32 -p "Your prompt"
```

#### CUDA Graph Enablement (35% throughput improvement)

```bash
# Enable in llama.cpp/LM Studio (automatic with CUDA 12.8+)
# Reduces CPU-GPU synchronization overhead
```

#### Optimal GPU Layer Offloading

```bash
# General rule: Find maximum n_ctx that fits in VRAM
# For a 7B Q4_K_M model on 12GB GPU:
./main -m model.gguf -ngl 32 -n 4096 --mlock
```

### CPU Thread Optimization

For hybrid CPU/GPU inference:

```bash
# Start with number of physical cores
# Example: 6-core CPU
./main -m model.gguf -t 6 -ngl 16 -p "Test prompt"

# Benchmark different thread counts
for threads in 4 6 8 12; do
  echo "Testing with $threads threads"
  ./main -m model.gguf -t $threads -ngl 32 -p "test" -n 100
done
```

### Batch Processing

```bash
# Batch multiple prompts to improve throughput
# In vLLM: Dynamic batching automatic
# In llama.cpp: Multiple sequential prompts

cat << 'EOF' | ./main -m model.gguf -ngl 32 --batch-size 32
Prompt 1
Prompt 2
Prompt 3
EOF
```

### Memory-Efficient Context Windows

```bash
# Balance context length with VRAM available
# Estimate: ~128 bytes per token for activations

# 4096 token context on 12GB GPU
./main -m model.gguf -n 4096 -ngl 32

# 8192 token context requires larger GPU or quantization
# Use GGUF over GPTQ for memory efficiency at longer contexts
```

---

## Troubleshooting and Best Practices

### Common Issues and Solutions

#### **Issue: "CUDA out of memory" Error**

```bash
# Solution 1: Reduce context window
./main -m model.gguf -n 2048 -ngl 32

# Solution 2: Use more aggressive quantization
# Try Q4_K_S instead of Q5_K_M

# Solution 3: Reduce number of GPU layers
./main -m model.gguf -ngl 16  # Instead of -ngl 32

# Solution 4: Enable CPU offloading
./main -m model.gguf -ngl 20 -t 8  # Use remaining on CPU
```

#### **Issue: Very Slow Inference Speed**

```bash
# Verify GPU is being used
nvidia-smi

# Check GPU utilization (should show compute activity)
nvidia-smi dmon  # Real-time monitoring

# Enable all optimizations
./main -m model.gguf \
  -ngl 32 \
  -fa \
  -t 8 \
  --mlock \
  -b 128 \
  -n 256
```

#### **Issue: Model Not Found or CUDA Errors**

```bash
# Verify CUDA installation
nvcc --version
nvidia-smi

# Rebuild llama.cpp if using pre-built binary
make clean
make LLAMA_CUDA=1 -j$(nproc)
```

#### **Issue: Model Produces Incoherent Responses**

```bash
# Problem: Too aggressive quantization
# Solution: Use higher-quality GGUF level

# Instead of Q4_K_S, try:
# - Q4_K_M (recommended)
# - Q5_K_M (high quality)
# - Q6_K (very high quality)

# Or use GPTQ/AWQ instead of GGUF
```

### Best Practices

#### 1. **Choose Appropriate Model Size**

- **12GB GPU**: 7B models maximum (Q4/Q5 quantization)
- **16GB GPU**: 13B models (Q4 quantization) or 7B full precision
- **24GB GPU**: 32B models (Q4 quantization)
- **48GB+ GPU**: 70B models or custom fine-tuned models

#### 2. **VRAM Allocation Strategy**

- Reserve 1-2GB for OS and background processes
- Allocate remaining VRAM for model, KV cache, and activations
- Example on 12GB GPU: 10GB for model inference

#### 3. **Quantization Quality Matrix**

| Quality Requirement | VRAM Budget | Recommended           |
| ------------------- | ----------- | --------------------- |
| Maximum quality     | Abundant    | FP16/FP32             |
| High quality        | Moderate    | Q5_K_M (GGUF) or AWQ  |
| Balanced            | Limited     | Q4_K_M (GGUF) or GPTQ |
| Extreme compression | Minimal     | IQ2_XXS or IQ3_S      |

#### 4. **Production Deployment Checklist**

- [ ] Test model with representative prompts
- [ ] Monitor GPU memory during peak load
- [ ] Set appropriate context window limits
- [ ] Enable logging for debugging
- [ ] Test with expected concurrent user load
- [ ] Use vLLM or similar for multi-user scenarios
- [ ] Implement prompt caching for repeated queries

#### 5. **Security Considerations**

- Run inference in isolated environments for untrusted inputs
- Monitor VRAM usage to prevent DoS attacks (context bombing)
- Sanitize system prompts to prevent prompt injection
- Use rate limiting on inference endpoints

#### 6. **Finding Pre-Quantized Models**

- Visit [Hugging Face Model Hub](https://huggingface.co/models?library=gguf)
- Search for "GGUF", "GPTQ", or "AWQ" tags
- Popular creators: TheBloke (GGUF/GPTQ), AutoGPTQ team (AWQ)
- Filter by: model size, quantization level, license

---

## Performance Benchmarks (Reference Data)

**Test Setup**: NVIDIA RTX 5080, DeepSeek-R1-Distill-Llama-8B (Q4_K_M GGUF)

| Configuration             | Tokens/Second | Throughput   |
| ------------------------- | ------------- | ------------ |
| Without optimizations     | 35 tok/s      | Baseline     |
| With Flash Attention      | 40 tok/s      | +15%         |
| With CUDA Graphs          | 47 tok/s      | +35%         |
| All optimizations enabled | ~45 tok/s     | +27% average |

**Model Loading Time**:

- GGUF Q4_K_M (7B): ~2-3 seconds with GPU offloading
- GPTQ (7B): ~1-2 seconds
- Full precision (7B): ~4-5 seconds

---

## Resources and Further Learning

### Official Documentation

- [llama.cpp GitHub Repository](https://github.com/ggerganov/llama.cpp)
- [NVIDIA CUDA Toolkit Documentation](https://docs.nvidia.com/cuda/)
- [Ollama Official Guide](https://ollama.ai/library)
- [vLLM Documentation](https://docs.vllm.ai/)

### Community Resources

- Hugging Face Model Hub with GGUF filters
- LocalLLaMA subreddit for troubleshooting
- NVIDIA RTX AI Garage blog for latest optimizations

### Recommended Models for Local Inference

- **Llama 2 7B** (Meta): Excellent all-rounder
- **Mistral 7B** (Mistral AI): Fast and capable
- **Neural Chat 7B** (Intel): Optimized for CPU/GPU hybrid
- **Orca 2** (Microsoft): Strong reasoning tasks
- **Qwen 2** (Alibaba): Multimodal capable

---

## Conclusion

Running LLMs locally on NVIDIA GPUs is now highly accessible through modern frameworks like LM Studio, Ollama, and llama.cpp. By understanding quantization techniques, GPU optimization, and appropriate model selection for your hardware, you can deploy powerful AI capabilities entirely on your local machine with full privacy and control.

Start with LM Studio for ease of use, experiment with Ollama for different models, and graduate to llama.cpp or vLLM for production deployments as your needs grow.
