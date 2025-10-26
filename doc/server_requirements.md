# Server Requirements – VRX Tunnel (ROS 2 Jazzy + Gazebo Harmonic)

This document outlines hardware and software requirements to deploy and run the VRX Tunnel simulation pulled from GitLab.

## Target OS

- Ubuntu 24.04 LTS (preferred for ROS 2 Jazzy)

## Profiles

- Minimal (headless, no RGL LiDAR)
  - vCPU: 4
  - RAM: 8–16 GB
  - Disk: 30–50 GB SSD
  - GPU: none
  - Use case: CI/build, smoke tests. Do not enable RGL sensors.

- Recommended (single sim with RGL LiDAR; optional RViz)
  - vCPU: 8–16
  - RAM: 32 GB
  - Disk: 100+ GB NVMe SSD (workspace + assets + some bags)
  - GPU: NVIDIA, 8+ GB VRAM (RTX 3060/4060/3070, A2000 12GB, A4000)
  - Driver/CUDA: LTS driver ≥ 535, CUDA 12.x (verify with `nvidia-smi`)
  - Use case: Development and single-run testing.

- Heavy (multi-sim, long recordings)
  - vCPU: 32+
  - RAM: 64–128 GB
  - Disk: 500 GB–1 TB NVMe (large rosbag storage)
  - GPU: 16+ GB VRAM (RTX 4080/5000 Ada, L40S)
  - Use case: Batch experiments, large datasets.

## Storage guidance

- Source + build + apt cache: 15–30 GB
- Gazebo assets and models: 5–15 GB
- Rosbags: size grows quickly; plan 100–500 GB if recording frequently
- Recommendation: NVMe SSD; mount a dedicated data volume for bags (e.g., `/data`).

## GPU and rendering

- RGL requires NVIDIA GPU (CUDA/OptiX). CPU-only is possible if RGL is disabled.
- Prefer production driver branch (≥ 535). Keep kernel userspace and NVML in sync.
- Use the repo script `scripts/check_nvidia_versions.sh` to diagnose driver/NVML mismatches.
- For multi-GPU/iGPU systems, use `scripts/with_gpu.sh` to force the dGPU for `gz`/RViz.

## Network

- Outbound HTTPS to pull from GitLab and package mirrors.
- For remote visualization, prefer a remote desktop solution (X11/VNC/NoMachine/DCV) if running RViz on the server.

## Verification checklist (run on server)

```bash
# CPU and threads
lscpu | egrep 'Model name|CPU\(s\)|Thread|Core|Socket'

# Memory
free -h

# Disk
df -h /
# (optional data mount)
df -h /data

# OS and kernel
cat /etc/os-release
uname -r

# NVIDIA GPU & driver (if present)
nvidia-smi || true

# Deep driver/NVML check (provided in this repo)
chmod +x scripts/check_nvidia_versions.sh
scripts/check_nvidia_versions.sh
```

## Acceptance targets (recommended profile)

- vCPU ≥ 8
- RAM ≥ 32 GB
- Disk ≥ 500 GB total (esp. if recording rosbag)
- Ubuntu 24.04 LTS
- NVIDIA GPU with ≥ 8 GB VRAM; driver ≥ 535; CUDA 12.x
