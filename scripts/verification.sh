#!/usr/bin/env bash
set -euo pipefail

echo "== Jetson Environment Report =="

MODEL="$(tr -d '\0' </proc/device-tree/model 2>/dev/null || echo 'unknown')"
echo "Model: $MODEL"

if [ -f /proc/device-tree/compatible ]; then
  COMPAT="$(tr -d '\0' </proc/device-tree/compatible)"
  echo "Compatible: $COMPAT"
fi

if [ -f /etc/nv_tegra_release ]; then
  L4T="$(head -n1 /etc/nv_tegra_release)"
  echo "L4T: $L4T"
else
  echo "L4T: not found"
fi

JP="$(apt-cache policy nvidia-jetpack 2>/dev/null | awk '/Installed:/ {print $2}')"
echo "nvidia-jetpack (apt): ${JP:-not-installed}"

echo "Kernel: $(uname -r)"

if command -v nvcc >/dev/null 2>&1; then
  echo "CUDA: $(nvcc --version | awk -F, '/release/ {print $3}' | sed 's/.*release //')"
else
  echo "CUDA: not found"
fi