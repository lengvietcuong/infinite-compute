# Setting Up an NVIDIA GPU After Purchase

## Introduction

Setting up an NVIDIA GPU involves multiple stages, from physical hardware installation to software driver configuration and optimization for deep learning frameworks. This guide covers the entire process, whether you're using a gaming card (GeForce) or a data center card (Tesla/A100), on Windows, Linux, or macOS systems.

---

## Part 1: Physical Installation

### 1.1 Pre-Installation Checklist

Before opening your case, ensure you have the following:

- Anti-static wrist strap (recommended to prevent ESD damage)
- Thermal paste (if your GPU requires manual application)
- PCIe power cables from your PSU
- Motherboard manual (to identify the primary PCIe x16 slot)
- Phillips head screwdriver
- Isopropyl alcohol and microfiber cloth (for cleaning)

### 1.2 System Preparation

**Power Down Safely:**

- Completely power off your PC
- Unplug the power cable from the wall
- Wait at least 20 seconds to allow all capacitors to discharge
- Press the power button once to ground any remaining electricity

**Prepare Your Case:**

- Open the PC case following your case manufacturer's instructions
- Locate the primary PCIe x16 slot on your motherboard (usually the topmost full-length slot, just below the RAM)
- Remove the two metal bracket covers from the rear of your case that align with your GPU's output ports

### 1.3 Installing the GPU into the PCIe Slot

**Motherboard Preparation:**

- Locate the retention clip at the right end of the primary PCIe x16 slot
- Gently push this clip downward to the unlocked position

**Inserting the GPU:**

1. Align the GPU's gold connector fingers with the PCIe x16 slot
2. The notch on the GPU connector should align with the key in the motherboard slot
3. Gently but firmly insert the GPU into the slot, applying even downward pressure
4. Continue pushing until you hear a click—the retention clip will automatically lock the GPU in place
5. Secure the GPU's mounting bracket to the case using the provided screws or thumbscrews

**Important:** Never force the GPU into the slot. If resistance is encountered, remove it and check for obstructions or incorrect alignment.

### 1.4 Power Supply Connections

**Determine Power Requirements:**

- Check your GPU's specifications on the manufacturer's website for power consumption (TDP)
- Identify the type and number of PCIe power connectors required (6-pin, 8-pin, or 12-pin)

**Power Cable Guidelines:**

- PCIe x16 motherboard slot: provides up to 75W
- 6-pin PCIe connector: provides up to 75W
- 8-pin PCIe connector: provides up to 150W
- 12-pin PCIe connector: provides up to 400W (newer NVIDIA designs)

**Connecting Power Cables:**

1. Locate the PCIe power connectors on the top of your GPU
2. Route cables from your PSU to the GPU, avoiding sharp bends
3. Connect each cable firmly—the connector should fit only one way (keyed design)
4. For high-end GPUs (RTX 4090, RTX 4080), use separate cables from the PSU rather than daisy-chained connections
5. Ensure all connections are fully inserted until you see a click or feel resistance

**Power Supply Requirements:**

- Minimum PSU capacity: GPU TDP + CPU + system overhead
- For example, an RTX 4090 (575W) + high-end CPU requires at least a 1000W PSU
- Always consult the GPU manufacturer's recommended system power supply rating

### 1.5 Thermal Paste Application (If Required)

Many modern GPUs come with pre-applied thermal paste on the cooler. Check the base plate of your cooler before proceeding.

**If Manual Application is Needed:**

1. **Preparation:**

   - Remove the GPU from the case
   - Remove the heatsink/cooler from the GPU die
   - Clean the GPU die surface using isopropyl alcohol and a microfiber cloth
   - Let it dry completely (2-3 minutes)
   - Clean the heatsink base plate the same way

2. **Thermal Paste Application Methods:**

   **Dot Method (Recommended for Most GPUs):**

   - Apply a small dot of thermal paste (rice grain size, ~0.3-0.4ml) in the center of the GPU's integrated heat spreader (IHS)
   - The mounting pressure will spread the paste evenly

   **Line Method:**

   - Create a thin line of thermal paste along the center of the IHS
   - The line length should equal the width of the IHS

   **Spread Method:**

   - Use a plastic spreader or old credit card to apply a thin, even layer
   - Ensure complete coverage but keep the layer thin

3. **Reassembly:**
   - Align the heatsink with the GPU die
   - Use gentle, even downward pressure to mount the cooler
   - Tighten mounting screws in a diagonal pattern (top-left → bottom-right → top-right → bottom-left)
   - Avoid over-tightening, which can damage the GPU

---

## Part 2: NVIDIA Driver Installation

### 2.1 Identifying Your GPU

**On Windows:**

1. Right-click on the Windows Start button
2. Select "Device Manager"
3. Expand "Display adapters"
4. Note your GPU model name

**On Linux:**

```bash
lspci | grep -i nvidia
```

**On macOS:**

- Click the Apple menu
- Select "About This Mac"
- Go to "System Report"
- Look under "Graphics/Displays"

### 2.2 Windows Driver Installation

**Step 1: Check CUDA Compatibility**

- Visit NVIDIA's [CUDA-Enabled GPU List](https://developer.nvidia.com/cuda-gpus)
- Verify your GPU supports CUDA

**Step 2: Download the Latest Driver**

1. Go to [NVIDIA Driver Downloads](https://www.nvidia.com/Download/index.aspx)
2. Select your GPU product line, series, and OS
3. Choose between:
   - **Game Ready Driver (GRD):** For gaming and general graphics use
   - **Studio Driver (SD):** For professional applications and creative work
4. Download the latest version

**Step 3: Perform a Clean Installation (Optional but Recommended)**

For problematic drivers or switching from AMD, perform a clean install using Display Driver Uninstaller (DDU):

1. Download [DDU (Display Driver Uninstaller)](https://www.guru3d.com/files-details/display-driver-uninstaller-download.html)
2. Boot into Windows Safe Mode (hold Shift during shutdown → Troubleshoot → Advanced Options → Startup Settings)
3. Run DDU in Safe Mode
4. Select "GPU" and "NVIDIA" in dropdowns
5. Click "Clean and Restart"

**Step 4: Install the Driver**

1. Run the downloaded NVIDIA installer
2. Review and accept the license agreement
3. Choose **Custom (Advanced)** installation type
4. Check "Perform a clean installation"
5. Uncheck unnecessary components (GeForce Experience, HD Audio, Shield Wireless)
6. Select installation location
7. Click Install and wait for completion

**Step 5: Restart System**

- Reboot once installation completes
- Let Windows fully load

**Step 6: Verify Installation**

1. Right-click on desktop
2. Select "NVIDIA Control Panel"
3. Go to "Help" → "System Information"
4. Verify driver version and GPU name

### 2.3 Linux Driver Installation (Ubuntu/Debian)

**Automatic Installation (Recommended):**

```bash
# Update package list
sudo apt update

# Automatically install appropriate NVIDIA drivers
sudo ubuntu-drivers autoinstall

# Reboot system
sudo reboot
```

**Manual Installation with DKMS:**

```bash
# Install required packages
sudo apt install linux-headers-$(uname -r)

# Add NVIDIA repository
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update

# Install DKMS driver (replace 555 with desired driver version)
sudo apt install nvidia-driver-555 nvidia-dkms-555

# Reboot
sudo reboot
```

**For Fedora/RHEL-based Systems:**

```bash
# Add NVIDIA repository
sudo dnf config-manager --add-repo http://developer.download.nvidia.com/compute/cuda/repos/rhel10/$(uname -m)/cuda-rhel10.repo

# Clean cache
sudo dnf clean expire-cache

# Install driver
sudo dnf install nvidia-driver -y

# For Secure Boot enabled systems
sudo mokutil --import /var/lib/dkms/mok.pub

# Reboot
sudo reboot
```

### 2.4 macOS Driver Installation

NVIDIA drivers for macOS are limited. Most newer GPUs require alternatives like:

- Metal Performance Shaders (MPS) for native acceleration
- eGPU support through Thunderbolt 3/4
- Third-party tools like CUDA through Docker containers

Check [NVIDIA's macOS support page](https://www.nvidia.com/Download/driverResults.aspx/193113/) for compatible cards.

### 2.5 Verify Driver Installation

**Windows (Command Prompt):**

```bash
nvidia-smi
```

**Linux/macOS (Terminal):**

```bash
nvidia-smi
```

Expected output should display:

- GPU name and memory
- Driver version
- CUDA Compute Capability

---

## Part 3: CUDA Toolkit Installation

CUDA is required for GPU-accelerated computing and deep learning frameworks.

### 3.1 Windows CUDA Installation

**Step 1: Download CUDA Toolkit**

1. Visit [NVIDIA CUDA Toolkit Download](https://developer.nvidia.com/cuda-downloads)
2. Select:
   - OS: Windows
   - Architecture: x86_64
   - Version: Windows 10 or Windows 11
3. Choose either local .exe installer or network installer
4. Download the installer

**Step 2: Run the Installer**

1. Execute the downloaded .exe file with administrator privileges
2. Accept the license agreement
3. Select installation location (default: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\vX.X`)
4. Choose all essential components:
   - CUDA Toolkit
   - NVIDIA Nsight Systems
   - NVIDIA Nsight Compute
   - Documentation
   - Samples
5. Complete installation

**Step 3: Verify Installation**

1. Open Command Prompt
2. Run:

```bash
nvcc --version
```

Should display CUDA compiler version.

### 3.2 Linux CUDA Installation (Ubuntu)

**Step 1: Install CUDA Repository**

```bash
# Install curl if needed
sudo apt update && sudo apt install curl

# Add NVIDIA GPG key (Ubuntu 22.04 example)
curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-cuda-keyring.gpg

# Add CUDA repository
echo "deb [signed-by=/usr/share/keyrings/nvidia-cuda-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" | sudo tee /etc/apt/sources.list.d/cuda-repository.list
```

**Step 2: Install CUDA Toolkit**

```bash
sudo apt update
sudo apt install cuda
```

**Step 3: Configure Environment Variables**

Edit or create `~/.bashrc`:

```bash
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

Apply changes:

```bash
source ~/.bashrc
```

**Step 4: Verify Installation**

```bash
nvcc --version
```

---

## Part 4: cuDNN Installation (For Deep Learning)

cuDNN is a specialized library for deep neural network operations and is required for frameworks like TensorFlow and PyTorch.

### 4.1 Windows cuDNN Installation

**Option 1: Package Manager Installation**

```bash
# Download and run cuDNN installer for Windows
# Execute the installer and follow on-screen prompts
# Select installation location
```

**Option 2: Manual Installation**

1. Download cuDNN from [NVIDIA Developer site](https://developer.nvidia.com/cudnn)
2. Unzip the downloaded file
3. Copy files to CUDA directories:

   - `bin\cudnn*.dll` → `C:\Program Files\NVIDIA\CUDNN\vx.x\bin`
   - `include\cudnn*.h` → `C:\Program Files\NVIDIA\CUDNN\vx.x\include`
   - `lib\x64\cudnn*.lib` → `C:\Program Files\NVIDIA\CUDNN\vx.x\lib`

4. Update PATH variable:
   - Open System Properties → Environment Variables
   - Add `C:\Program Files\NVIDIA\CUDNN\vx.x\bin` to PATH

### 4.2 Linux cuDNN Installation

**Option 1: Package Manager (Ubuntu/Debian)**

```bash
# Install cuDNN via apt
sudo apt-get install libcudnn8=8.x.x.x-1+cudaX.X
sudo apt-get install libcudnn8-dev=8.x.x.x-1+cudaX.X
```

**Option 2: Manual Installation**

```bash
# Extract archive
tar -xf cudnn-linux-x86_64-x.x.x.x_cudaX.X-archive.tar.xz

# Copy files
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include/
sudo cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64/
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

# Refresh library cache
sudo ldconfig
```

**Verify Installation:**

```bash
cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2
```

### 4.3 Python Wheel Installation

```bash
# Update pip and wheel
python3 -m pip install --upgrade pip wheel

# Install cuDNN for CUDA 12
python3 -m pip install nvidia-cudnn-cu12

# Or for CUDA 11
python3 -m pip install nvidia-cudnn-cu11

# Specific version
python3 -m pip install nvidia-cudnn-cu12==9.x.y.z
```

---

## Part 5: Setting Up Deep Learning Frameworks

### 5.1 TensorFlow GPU Setup

**Installation:**

```bash
pip install tensorflow[and-cuda]
```

**Verification:**

```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

Should display your GPU as an available device.

### 5.2 PyTorch GPU Setup

**Installation (CUDA 12.1):**

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Installation (CUDA 11.8):**

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verification:**

```python
import torch
print(torch.cuda.is_available())      # Should return True
print(torch.cuda.device_count())      # Number of available GPUs
print(torch.cuda.get_device_name(0))  # GPU name
```

### 5.3 MXNet GPU Setup

**Installation:**

```bash
# For CUDA 11.0
pip install mxnet-cu110

# For CUDA 12.0
pip install mxnet-cu120
```

**Verification:**

```python
import mxnet as mx
print(mx.context.num_gpus())
```

---

## Part 6: Troubleshooting Common Issues

### 6.1 GPU Not Detected

**Windows:**

- Run Device Manager; if GPU shows yellow warning, update drivers
- Check BIOS settings for PCIe slot enablement
- Verify GPU is fully seated in PCIe slot

**Linux:**

```bash
# Check hardware detection
lspci | grep -i nvidia

# Check kernel module loading
lsmod | grep nvidia

# Load module if not loaded
sudo modprobe nvidia
```

### 6.2 Driver Installation Failures

**Solution Steps:**

1. Boot into Safe Mode (Windows) or single-user mode (Linux)
2. Use DDU to completely remove old drivers
3. Disable any conflicting drivers (nouveau on Linux)
4. Perform clean installation of drivers
5. Reboot system

**For Linux (disable Nouveau driver):**

```bash
sudo tee /etc/modprobe.d/blacklist-nouveau.conf <<< "blacklist nouveau"
sudo tee -a /etc/modprobe.d/blacklist-nouveau.conf <<< "options nouveau modeset=0"
sudo update-initramfs -u
sudo reboot
```

### 6.3 CUDA Not Detected by Applications

**Verify CUDA Installation:**

```bash
nvcc --version
echo $CUDA_PATH        # Windows
echo $LD_LIBRARY_PATH  # Linux
```

**Set Environment Variables Manually (Windows):**

1. Right-click "This PC" → Properties
2. Advanced system settings
3. Environment Variables
4. Add `CUDA_PATH` = `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\vX.X`
5. Add to PATH: `%CUDA_PATH%\bin`
6. Restart applications

### 6.4 High Temperatures

**Check Temperature:**

```bash
nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits
```

**Solutions:**

- Ensure proper thermal paste application
- Check cooler fan operation
- Clean dust from heatsink and fans
- Ensure adequate case airflow
- Reapply thermal paste if temperatures exceed 80°C under load

### 6.5 Low Performance / Underclocking

**Check GPU Clock Status:**

```bash
nvidia-smi -q -d CLOCK
```

**Possible Causes:**

- GPU thermal throttling (see above)
- PCIe bandwidth constraints
- Insufficient power delivery
- Outdated driver

### 6.6 Framework-Specific Issues

**TensorFlow GPU Not Used:**

- Verify CUDA compatibility: Check TensorFlow version requirements
- Reinstall TensorFlow: `pip install --upgrade tensorflow[and-cuda]`
- Check for conflicting CPU-optimized packages

**PyTorch CUDA Issues:**

- Verify CUDA version matches: `python -c "import torch; print(torch.__version__)"`
- Reinstall with correct CUDA version
- Check for conflicting older CUDA installations

---

## Part 7: Optimization Tips

### 7.1 GPU Memory Management

**Check Available Memory:**

```bash
nvidia-smi --query-gpu=memory.total,memory.used --format=csv
```

**Reduce Memory Usage in Python:**

```python
import tensorflow as tf
# Limit GPU memory usage
gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
```

### 7.2 Multi-GPU Setup

**PyTorch DataParallel:**

```python
model = torch.nn.DataParallel(model)
model.to(device)
```

**TensorFlow Distributed:**

```python
strategy = tf.distribute.MirroredStrategy()
with strategy.scope():
    model = tf.keras.Sequential([...])
```

### 7.3 Driver and CUDA Updates

**Windows Driver Update:**

- Use GeForce Experience for automatic updates, or
- Manually download from NVIDIA Driver Downloads page
- Always backup current driver before updating

**Linux Driver Update:**

```bash
sudo apt update && sudo apt upgrade cuda-drivers
sudo reboot
```

---

## Part 8: Compatibility Matrix

| Framework       | Min CUDA   | Min cuDNN | Notes                                         |
| --------------- | ---------- | --------- | --------------------------------------------- |
| TensorFlow 2.15 | 12.2       | 8.1+      | Supports latest CUDA versions                 |
| PyTorch 2.1+    | 11.8, 12.1 | 8.3.2+    | Multiple CUDA version support                 |
| MXNet 1.9+      | 10.1-11.7  | 7.6.5-8.5 | Requires manual compilation for some versions |
| JAX             | 11.2+      | 8.0+      | Supports latest CUDA releases                 |

---

## Conclusion

Setting up an NVIDIA GPU requires careful attention to both hardware and software installation. By following this comprehensive guide, you'll have:

1. ✅ Properly installed GPU hardware
2. ✅ Current NVIDIA drivers
3. ✅ CUDA Toolkit for GPU computing
4. ✅ cuDNN for deep learning acceleration
5. ✅ Configured deep learning frameworks
6. ✅ Troubleshooting knowledge for common issues

For the best performance and stability, regularly update drivers and CUDA components, monitor GPU temperatures, and consult official documentation for your specific frameworks and use cases.
