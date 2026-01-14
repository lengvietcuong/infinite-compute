# Troubleshooting NVIDIA GPUs

## Table of Contents

1. [Overview](#overview)
2. [Initial Diagnostics](#initial-diagnostics)
3. [Driver Issues](#driver-issues)
4. [Memory Problems](#memory-problems)
5. [Thermal Issues](#thermal-issues)
6. [Hardware Detection](#hardware-detection)
7. [CUDA and Application Errors](#cuda-and-application-errors)
8. [Performance and Throttling](#performance-and-throttling)
9. [Xid Error Messages](#xid-error-messages)
10. [Advanced Diagnostics](#advanced-diagnostics)
11. [Best Practices](#best-practices)

---

## Overview

NVIDIA GPU troubleshooting requires a systematic approach to identify whether issues stem from drivers, hardware, software configuration, or application code. This guide covers common problems and resolution strategies across consumer and data center GPU environments.

### When to Troubleshoot vs Replace

GPU issues can manifest in various ways, but not all require hardware replacement. Common symptoms include:

- **Thermal throttling** (performance drops during intensive use)
- **Driver crashes** or "Display driver stopped responding" messages
- **Out-of-memory errors** during CUDA execution
- **GPU not detected** by the operating system
- **Artifacts or display glitches**
- **Excessive power consumption** or thermal behavior
- **XID errors** in system logs

### Prerequisites Before Starting

Ensure you have:

- The **latest NVIDIA driver** installed for your GPU model
- Updated **BIOS/firmware** on your system
- Sufficient **power supply capacity** and properly connected cables
- Adequate **airflow and cooling** in your system
- **nvidia-smi** utility available (comes with driver)

---

## Initial Diagnostics

### Quick Status Check with nvidia-smi

The **NVIDIA System Management Interface (nvidia-smi)** is your primary diagnostic tool. Start with basic queries:

```bash
# Display all GPU information
nvidia-smi

# Detailed GPU information
nvidia-smi -q

# Monitor GPUs in real-time
nvidia-smi -l 1  # Update every 1 second
```

The output shows:

- **GPU Name and Index**: Which GPUs are detected
- **Driver Version**: Currently installed driver version
- **CUDA Version**: Compatible CUDA version
- **Memory Usage**: Current VRAM allocation
- **GPU Utilization**: Compute and memory utilization percentages
- **Temperature**: Current GPU temperature
- **Power Draw**: Current power consumption vs power limit
- **Running Processes**: Applications using the GPU

### Specific Queries

```bash
# List all GPUs with serial numbers and bus IDs
nvidia-smi --query-gpu=name,index,serial,pci.bus_id --format=csv

# Check GPU memory allocation
nvidia-smi --query-gpu=memory.total,memory.free,memory.used --format=csv,noheader

# Display power information
nvidia-smi -q -d POWER

# Check driver persistence mode
nvidia-smi -q | grep "Persistence Mode"

# List processes using GPU memory
nvidia-smi --query-compute-apps=pid,process_name,gpu_memory_usage --format=csv

# Check for throttling reasons
nvidia-smi --query-gpu=clocks_throttle_reasons.active --format=csv
```

### Return Codes

When using nvidia-smi commands, return codes indicate success or failure:

- **0**: Success
- **8**: Device's external power cables not properly attached
- **9**: NVIDIA driver not loaded
- **10**: NVIDIA Kernel detected an interrupt issue with GPU
- **14**: infoROM is corrupted (requires GPU replacement)
- **15**: GPU has fallen off the bus (hardware issue)
- **255**: Other error or internal driver error

---

## Driver Issues

### Detecting Driver Problems

Common driver-related symptoms:

- Black screen or no signal to monitor
- Game/application crashes without errors
- "Display driver stopped responding and has recovered" messages
- GPU not appearing in device listings
- Performance significantly below expected baseline

### Step 1: Verify Driver Installation

```bash
# Check if driver is loaded
nvidia-smi

# For Linux, check if nouveau driver is blocking NVIDIA driver
lsmod | grep -i nouveau  # Should return nothing

# Check kernel messages for driver errors
sudo dmesg | grep -i NVRM
sudo dmesg | grep -i Xid
```

If the nouveau driver is loaded on Linux, disable it:

```bash
# Create blacklist file
sudo tee /etc/modprobe.d/blacklist-nouveau.conf << EOF
blacklist nouveau
options nouveau modeset=0
EOF

# Rebuild initramfs
sudo update-initramfs -u

# Reboot
sudo reboot
```

### Step 2: Clean Driver Reinstallation (Windows)

For persistent driver issues, perform a clean uninstall:

1. **Download DDU (Display Driver Uninstaller)** from wagnardsoft.com
2. **Boot into Safe Mode**:

   - Hold Shift while clicking Restart
   - Navigate to Troubleshoot → Advanced Options → Startup Settings
   - Select Restart and press F4 for Safe Mode

3. **Run DDU**:

   - Select your GPU manufacturer and model
   - Check "Remove driver software" option
   - Click Clean and Restart

4. **Reinstall Driver**:
   - Download latest driver from nvidia.com
   - Run installer and follow prompts
   - Restart computer

### Step 3: Driver Rollback

If issues started after a recent driver update:

```bash
# Windows: Use Device Manager
# Device Manager → Display Adapters → Right-click GPU → Properties
# Driver tab → Roll Back Driver

# Linux: Downgrade package (example for Ubuntu)
sudo apt-get install nvidia-driver-570  # Specific version
sudo apt autoremove  # Remove newer version
sudo reboot
```

### Step 4: Update NVIDIA Control Panel Settings (Windows)

Open NVIDIA Control Panel and verify:

```
Manage 3D Settings → Global Settings

- Power management mode: Prefer maximum performance
- Vertical sync: Off (unless screen tearing is visible)
- Preferred refresh rate: Highest available
```

### Step 5: Check Internet Connectivity (For Driver Installation)

If using GPU containers or automated driver deployment:

```bash
# Test DNS resolution
ping 8.8.8.8

# Test package repository connectivity
ping archive.ubuntu.com  # Ubuntu
ping vault.centos.org    # CentOS
```

---

## Memory Problems

### Out-of-Memory (OOM) Errors

**Symptom**: `RuntimeError: CUDA error: out of memory` or `GL_OUT_OF_MEMORY`

This occurs when VRAM is exhausted, even if GPU shows free memory.

### Investigation Steps

```bash
# Check total and free memory
nvidia-smi --query-gpu=memory.total,memory.free,memory.used --format=csv

# Identify which processes are consuming memory
nvidia-smi pmon  # Real-time process monitoring
ps aux | grep cuda  # Find CUDA-related processes
```

### Common Causes and Solutions

**Cause 1: Insufficient GPU Memory for Task**

Solution:

```python
# Reduce batch size in your code
batch_size = 32  # Instead of 64

# Enable gradient checkpointing (PyTorch)
model = torch.nn.utils.checkpoint.checkpoint(model, input)

# Use mixed precision training
from torch.cuda.amp import autocast
with autocast():
    output = model(input)
```

**Cause 2: Memory Leaks from Previous Processes**

Solution:

```bash
# Kill all GPU processes
sudo fuser -k /dev/nvidia*  # Linux

# Clear NVIDIA cache
sudo rm -rf ~/.nv
sudo reboot

# For Python/PyTorch, explicitly free memory
import torch
torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()
```

**Cause 3: GPU Visibility Issue on Multi-GPU Systems**

Solution:

```bash
# Check which GPUs are visible
nvidia-smi

# If a GPU is full, use a different one
export CUDA_VISIBLE_DEVICES=1,2,3  # Skip GPU 0

# Or disable GPU entirely
export CUDA_VISIBLE_DEVICES=""  # Run on CPU instead
```

**Cause 4: Memory Fragmentation**

Solution:

```bash
# Restart NVIDIA persistence daemon
sudo systemctl restart nvidia-persistenced

# Or disable and re-enable persistence mode
sudo nvidia-smi -pm 0
sudo nvidia-smi -pm 1
```

### Memory Testing

To test for faulty memory:

```bash
# Install NVIDIA Data Center GPU Manager (DCGM)
sudo apt-get install datacenter-gpu-manager

# Run memory diagnostic
sudo dcgmi diag -r 3  # Comprehensive test (30 min)
```

If errors are found in all memory channels, the Integrated Memory Controller (IMC) may be faulty and require GPU replacement.

---

## Thermal Issues

### Monitoring GPU Temperature

```bash
# Display current temperature
nvidia-smi --query-gpu=temperature.gpu,temperature.memory --format=csv

# Continuous monitoring
watch -n 1 nvidia-smi

# Historical temperature data (if available)
nvidia-smi --query-gpu=timestamp,temperature.gpu --format=csv -f temp_log.csv -l 1
```

### Temperature Thresholds

| Temperature      | Status   | Action                                    |
| ---------------- | -------- | ----------------------------------------- |
| < 70°C           | Normal   | No action needed                          |
| 70-85°C          | Warm     | Monitor, ensure cooling is adequate       |
| 85-95°C          | Hot      | Performance throttling may occur          |
| > 95°C           | Critical | Thermal throttling active, risk of damage |
| > 105°C (memory) | Severe   | Immediate action required                 |

### Overheating Solutions

**Step 1: Clean Cooling System**

```bash
# Physical inspection
# - Check heatsink for dust accumulation
# - Ensure all fans spin freely
# - Verify thermal paste/pads contact GPU die
```

**Step 2: Improve Airflow**

- Remove obstructions from GPU air intake/exhaust
- Position case to allow better ventilation
- Add additional case fans if needed
- Ensure cables are organized (not blocking fans)

**Step 3: Increase Fan Speed**

```bash
# Linux: Using nvidia-settings
sudo nvidia-settings -a "[gpu:0]/GPUFanControlState=1"
sudo nvidia-settings -a "[fan:0]/GPUCurrentFanSpeed=85"

# Or enable GUI:
nvidia-settings
# Enable "GPU Fan Settings" and adjust Fan 0 Speed to 85%
```

**Step 4: Replace Thermal Paste**

For advanced users (voids warranty):

1. Carefully remove heatsink (follow GPU manual)
2. Clean existing thermal paste with isopropyl alcohol
3. Apply thin layer of high-performance thermal paste
4. Reinstall heatsink with proper mounting pressure

**Step 5: Examine Power Delivery**

High temperature can indicate voltage regulation issues:

```bash
# Monitor power consumption
nvidia-smi --query-gpu=power.draw,power.limit --format=csv -l 1

# If consuming more than rated limit:
# - Check power cables for loose connections
# - Test power supply (may be failing)
# - Reduce power limit if safe
sudo nvidia-smi -pl 250  # Set 250W limit (adjust for your GPU)
```

---

## Hardware Detection

### GPU Not Visible in nvidia-smi

**Step 1: Verify PCI Detection**

```bash
# Check if GPU appears in PCI bus
lspci | grep -i nvidia
lspci -tvnn | grep -i nvidia

# If no NVIDIA entries, GPU not recognized by system
```

**Step 2: Physical Inspection**

- Reseat GPU in PCIe slot (power off first)
- Verify 6-pin or 8-pin power connectors are fully inserted
- Check for bent or damaged pins on GPU or slot
- Ensure GPU hasn't shifted (optical inspection)

**Step 3: BIOS Settings**

- Access BIOS/UEFI during boot (DEL, F2, or F12 key)
- Look for "PCIe" or "GPU" settings
- Enable "Above 4G Decoding" or "PCI-E Gen x" options
- Disable "Secure Boot" if issues persist
- Update BIOS to latest version

**Step 4: Check System Logs**

```bash
# For Linux
sudo dmesg | grep -i pci
sudo journalctl -xb | grep -i gpu

# Check for error messages like "GPU has fallen off the bus"
sudo dmesg | grep -i "Xid 79"
```

**Step 5: Test Individual Slot**

- Move GPU to different PCIe slot
- Try with minimal configuration (essential hardware only)
- Test with a different GPU if available

### GPU Visible but Not Responsive

```bash
# Test GPU responsiveness
nvidia-smi -q  # Should complete without hanging

# Monitor for Xid errors
sudo dmesg -w  # Watch for new messages

# Reset GPU
sudo nvidia-smi --gpu-reset
sudo reboot
```

---

## CUDA and Application Errors

### Checking CUDA Capability

```bash
# Verify CUDA support
nvidia-smi --query-gpu=compute_cap --format=csv

# Compute capability mapping:
# 3.0-3.2: Kepler
# 5.0-5.3: Maxwell
# 6.0-6.2: Pascal
# 7.0-7.5: Volta
# 8.0-8.6: Ampere
# 9.0: Hopper
```

### CUDA Error Handling in Code

Proper error checking prevents silent failures:

```c
// CUDA error checking macro
#define cudaCheck(err) \
    if (err != cudaSuccess) { \
        printf("CUDA error: %s\n", cudaGetErrorString(err)); \
        exit(-1); \
    }

// Example usage
cudaError_t err = cudaSetDevice(0);
cudaCheck(err);

// After kernel launch
kernel<<<blocks, threads>>>(data);
cudaCheck(cudaPeekAtLastError());
cudaCheck(cudaDeviceSynchronize());
```

### CUDA-GDB Debugging

For applications hanging or producing wrong results:

```bash
# Compile with debug symbols
nvcc -g -G mykernel.cu -o mykernel

# Debug with cuda-gdb
cuda-gdb ./mykernel

# Common commands
# (cuda-gdb) run              # Start program
# (cuda-gdb) break mykernel   # Set breakpoint at kernel
# (cuda-gdb) cuda kernel 0    # Switch to kernel 0
# (cuda-gdb) step             # Step through execution
# (cuda-gdb) print var_name   # Print variable value
```

### Common CUDA Errors

| Error                           | Cause                      | Solution                                  |
| ------------------------------- | -------------------------- | ----------------------------------------- |
| `cudaErrorInvalidDevice`        | Device ID invalid          | Check `CUDA_VISIBLE_DEVICES`              |
| `cudaErrorInsufficientDriver`   | Driver too old             | Update NVIDIA driver                      |
| `cudaErrorInvalidPtx`           | Compiled for wrong GPU     | Recompile with correct compute capability |
| `cudaErrorLaunchOutOfResources` | Too many threads/registers | Reduce grid/block dimensions              |
| `cudaErrorMemoryAllocation`     | Out of GPU memory          | Reduce allocation size                    |

---

## Performance and Throttling

### Identifying Throttling

```bash
# Check active throttle reasons
nvidia-smi --query-gpu=clocks_throttle_reasons.active --format=csv

# Possible throttle reasons
# - None: No throttling
# - Active: Unknown reason
# - Hw_Slowdown: Hardware issue
# - Sw_Thermal: Software thermal limit
# - Hw_Thermal: Hardware thermal limit
# - Sync_Boost: Synchronization boost
# - Sw_Power_Cap: Software power limit
# - Hw_Power_Brake: Hardware power limit
```

### Resolving Thermal Throttling

1. **Reduce Temperature** (see Thermal Issues section)
2. **Increase Power Limit** (if safe):

   ```bash
   # Check current and max power limits
   nvidia-smi -q -d POWER

   # Increase limit (requires adequate PSU)
   sudo nvidia-smi -pl 400  # Set to 400W (adjust based on GPU)
   ```

3. **Optimize Application**:
   - Reduce computational workload
   - Enable reduced precision (FP16 instead of FP32)
   - Use dynamic load balancing

### Clock Speed Management

```bash
# Display current clocks
nvidia-smi --query-gpu=clocks.current.graphics,clocks.current.memory --format=csv

# For consumer GPUs (with GFXBench or similar)
# Typically not adjustable without third-party tools

# For professional GPUs (Quadro, Tesla)
# Persistence daemon required:
sudo nvidia-smi -pm 1
```

---

## Xid Error Messages

**Xid errors** appear in system logs (`dmesg` on Linux) when GPU detects problems. These are critical for diagnosis.

### Common Xid Errors and Solutions

| Xid | Description                       | Action                                                     |
| --- | --------------------------------- | ---------------------------------------------------------- |
| 13  | Graphics Engine Exception         | Run DCGM diagnostics; debug application; check HW          |
| 31  | Suspected Hardware Problems       | Contact hardware vendor for diagnostics                    |
| 45  | Robust Channel Preemptive Removal | Informational only; can be ignored safely                  |
| 48  | Double Bit ECC Error              | Reset GPU; drain workloads; consider RMA                   |
| 61  | PMU Breakpoint                    | Report issue; reset GPU                                    |
| 62  | PMU Halt Error                    | Report issue; reset GPU                                    |
| 63  | Single Bit ECC Error (corrected)  | Monitor; reboot when convenient                            |
| 74  | NVLink Error                      | Check mechanical connections; reseat GPUs; run diagnostics |
| 79  | GPU has fallen off the bus        | Immediate action; GPU may be unrecoverable                 |
| 92  | High single-bit ECC error rate    | Run diagnostics; consider RMA                              |
| 94  | Contained ECC error               | Restart application; reset GPU when convenient             |
| 95  | Uncontained ECC error             | Reboot immediately; drain work if using MIG                |

### Checking for Xid Errors

```bash
# View recent Xid errors
sudo dmesg | grep -i "Xid"

# Continuous monitoring
sudo dmesg -w | grep -i "Xid"

# Full error context
sudo dmesg | grep -A 5 -B 5 "Xid"
```

### Response to Xid Errors

**For Xid 79** (GPU fallen off bus):

- Immediate GPU reset required: `sudo nvidia-smi --gpu-reset`
- May indicate loose connection or hardware failure
- Reseat GPU and power cables before reset

**For Xid 48** (Double Bit ECC Error):

- If followed by Xid 63 or 64: Drain workloads and reset GPU
- May indicate memory corruption
- RMA required if errors persist

**For Xid 63/64** (ECC Errors):

- Log errors; monitor for increasing frequency
- Reset GPU if needed
- Consider row remapping if available
- RMA if error rate exceeds threshold

---

## Advanced Diagnostics

### NVIDIA DCGM (Data Center GPU Manager)

DCGM provides comprehensive GPU health monitoring:

```bash
# Install DCGM
sudo apt-get install datacenter-gpu-manager

# Run short diagnostics (2-10 minutes)
sudo dcgmi diag -r 1

# Run standard diagnostics (10-20 minutes)
sudo dcgmi diag -r 2

# Run comprehensive diagnostics (20-30 minutes)
sudo dcgmi diag -r 3

# Export results as JSON
sudo dcgmi diag -r 3 -j > gpu_diagnostics.json
```

### NVIDIA Bug Report

Generate comprehensive system information:

```bash
# Create detailed bug report
nvidia-bug-report.sh

# This creates nvidia-bug-report.log.gz with:
# - Driver information
# - CUDA capabilities
# - dmesg logs
# - GLX information
# - System configuration
```

### Thermal Paste Quality Assessment

Monitor temperature delta between die and junction:

```bash
# Check temperature relationship
nvidia-smi --query-gpu=temperature.gpu,temperature.memory --format=csv -l 1

# Healthy delta: ~10-12°C (GPU vs Memory)
# Poor thermal contact: delta > 15°C indicates worn paste
```

### Fabric Manager (for NVSwitch systems)

For DGX or HGX systems with NVSwitch:

```bash
# Check fabric status
nvidia-smi -q | grep "Fabric State"

# If status is "In Progress", fabric manager needed
sudo systemctl start nvidia-fabric-manager

# Verify status
sudo systemctl status nvidia-fabric-manager

# View logs
tail -f /var/log/fabricmanager.log
```

---

## Best Practices

### Prevention and Maintenance

**Regular Monitoring**:

- Set up periodic DCGM diagnostics (weekly for servers)
- Monitor temperature, power, and clock speeds
- Log Xid errors and investigate immediately
- Track performance baselines for anomaly detection

**Preventive Maintenance**:

- Clean GPU and surrounding components every 3-6 months
- Update BIOS and drivers quarterly
- Test with standard benchmarks monthly
- Archive system logs for historical analysis

**Configuration Management**:

- Document GPU BIOS settings
- Record baseline performance metrics
- Maintain detailed change logs
- Test driver updates on test system first

### Proactive Checks

Implement pre-job validation:

```bash
#!/bin/bash
# GPU health check script

# 1. Check driver
if ! command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA driver not found"
    exit 1
fi

# 2. Check GPU count
GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
if [ $GPU_COUNT -lt 1 ]; then
    echo "No GPUs detected"
    exit 1
fi

# 3. Check for recent Xid errors
if dmesg | grep -i "Xid.*48\|Xid.*95\|Xid.*79" > /dev/null; then
    echo "Critical Xid errors detected"
    exit 1
fi

# 4. Check temperatures
MAX_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader | sort -rn | head -1)
if [ $MAX_TEMP -gt 85 ]; then
    echo "GPU temperature warning: ${MAX_TEMP}°C"
fi

# 5. Run quick diagnostic
sudo dcgmi diag -r 1 > /dev/null
if [ $? -ne 0 ]; then
    echo "DCGM diagnostics failed"
    exit 1
fi

echo "GPU health check passed"
exit 0
```

### When to Contact Support

Escalate to NVIDIA support with:

- Output of `nvidia-bug-report.sh`
- DCGM diagnostic logs
- Xid error messages and timestamps
- Steps taken to troubleshoot
- Hardware configuration details
- Reproduction steps for application errors

---

## Summary Table: Quick Troubleshooting Reference

| Problem           | First Action      | Second Action                          | Escalation            |
| ----------------- | ----------------- | -------------------------------------- | --------------------- |
| GPU not detected  | Check `lspci`     | Reseat GPU                             | Run DCGM diag         |
| Out of memory     | Reduce batch size | Clear cache (`torch.cuda.empty_cache`) | Check for leaks       |
| Overheating       | Clean heatsink    | Increase fan speed                     | Replace thermal paste |
| Driver crash      | Update driver     | Clean reinstall with DDU               | Rollback version      |
| Low performance   | Check throttling  | Reduce thermal load                    | Profile application   |
| Xid error         | Check `dmesg`     | Identify error code                    | Reset GPU             |
| Application hangs | Use cuda-gdb      | Add error checking                     | Review CUDA code      |

---

## References and Further Reading

- NVIDIA GPU Debug Guidelines: Official comprehensive debugging reference
- CUDA-GDB Documentation: Kernel debugging tools
- NVIDIA System Management Interface: nvidia-smi user guide
- DCGM Documentation: Advanced health monitoring
- NVIDIA Developer Forums: Community support and solutions
