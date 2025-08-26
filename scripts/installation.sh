#!/usr/bin/env bash
set -euo pipefail

echo "Starting installation"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOARD="jetson-agx-orin-devkit"

JP513_DIR="${SCRIPT_DIR}/jetpack_5_1_3"
JP62_DIR="${SCRIPT_DIR}/jetpack_6_2"

JP513_DRIVER="Jetson_Linux_R35.5.0_aarch64.tbz2"
JP513_ROOTFS="Tegra_Linux_Sample-Root-Filesystem_R35.5.0_aarch64.tbz2"

JP62_DRIVER_GLOB="Jetson_Linux_R36*.tbz2"
JP62_ROOTFS_GLOB="Tegra_Linux_Sample-Root-Filesystem_R36*.tbz2"

JP513_DRIVER_URL=""
JP513_ROOTFS_URL=""
JP62_DRIVER_URL=""
JP62_ROOTFS_URL=""

wait_for_recovery_device() {
  echo "Checking for NVIDIA recovery device"
  while true; do
    if lsusb | grep -qiE '(0955:|NVIDIA Corp)'; then
      echo "Device detected"
      break
    else
      echo "Device not detected. Connect the Jetson in Recovery Mode"
      sleep 2
    fi
  done
}

prepare_version_dir() {
  local ver="$1"
  local work_dir="$2"
  local driver="$3"
  local rootfs="$4"
  local driver_url="$5"
  local rootfs_url="$6"

  mkdir -p "$work_dir"
  cd "$work_dir"

  if [ "$ver" = "5.1.3" ]; then
    if [ ! -f "$driver" ]; then
      if [ -n "$driver_url" ]; then
        echo "Downloading driver package for 5.1.3"
        wget -O "$driver" "$driver_url"
      else
        echo "Driver package not found for 5.1.3"
        exit 1
      fi
    fi
    if [ ! -f "$rootfs" ]; then
      if [ -n "$rootfs_url" ]; then
        echo "Downloading sample rootfs for 5.1.3"
        wget -O "$rootfs" "$rootfs_url"
      else
        echo "Sample rootfs not found for 5.1.3"
        exit 1
      fi
    fi
  else
    DRIVER_FILE="$(ls $JP62_DRIVER_GLOB 2>/dev/null | head -n1 || true)"
    ROOTFS_FILE="$(ls $JP62_ROOTFS_GLOB 2>/dev/null | head -n1 || true)"
    if [ -z "${DRIVER_FILE:-}" ]; then
      if [ -n "$driver_url" ]; then
        echo "Downloading driver package for 6.2"
        DRIVER_FILE="Jetson_Linux_R36_download.tbz2"
        wget -O "$DRIVER_FILE" "$driver_url"
      else
        echo "Driver package not found for 6.2"
        exit 1
      fi
    fi
    if [ -z "${ROOTFS_FILE:-}" ]; then
      if [ -n "$rootfs_url" ]; then
        echo "Downloading sample rootfs for 6.2"
        ROOTFS_FILE="Tegra_Linux_Sample-Root-Filesystem_R36_download.tbz2"
        wget -O "$ROOTFS_FILE" "$rootfs_url"
      else
        echo "Sample rootfs not found for 6.2"
        exit 1
      fi
    fi
    driver="$DRIVER_FILE"
    rootfs="$ROOTFS_FILE"
    JP62_DRIVER_GLOB="$driver"
    JP62_ROOTFS_GLOB="$rootfs"
  fi

  if [ -d "Linux_for_Tegra" ]; then
    echo "Removing existing Linux_for_Tegra"
    sudo rm -rf Linux_for_Tegra
  fi

  echo "Extracting driver package"
  tar xf "$driver"

  echo "Preparing rootfs"
  sudo tar xpf "$rootfs" -C Linux_for_Tegra/rootfs/

  cd Linux_for_Tegra

  echo "Running prerequisites"
  if [ -x ./tools/l4t_flash_prerequisites.sh ]; then
    sudo ./tools/l4t_flash_prerequisites.sh
  fi

  echo "Applying binaries"
  sudo ./apply_binaries.sh

  cd "$work_dir"
}

echo "Select JetPack version:"
echo "1) 5.1.3"
echo "2) 6.2"
read -r VERSION_CHOICE

if [ "$VERSION_CHOICE" = "1" ]; then
  JP_VERSION="5.1.3"
  WORK_DIR="$JP513_DIR"
  DRIVER_FILE="$JP513_DRIVER"
  ROOTFS_FILE="$JP513_ROOTFS"
  prepare_version_dir "$JP_VERSION" "$WORK_DIR" "$DRIVER_FILE" "$ROOTFS_FILE" "$JP513_DRIVER_URL" "$JP513_ROOTFS_URL"
elif [ "$VERSION_CHOICE" = "2" ]; then
  JP_VERSION="6.2"
  WORK_DIR="$JP62_DIR"
  DRIVER_FILE="$JP62_DRIVER_GLOB"
  ROOTFS_FILE="$JP62_ROOTFS_GLOB"
  prepare_version_dir "$JP_VERSION" "$WORK_DIR" "$DRIVER_FILE" "$ROOTFS_FILE" "$JP62_DRIVER_URL" "$JP62_ROOTFS_URL"
else
  echo "Invalid selection"
  exit 1
fi

echo "Select target storage:"
echo "1) eMMC (internal)"
echo "2) NVMe (external)"
read -r TARGET_CHOICE

cd "$WORK_DIR/Linux_for_Tegra"

RC=1
if [ "$TARGET_CHOICE" = "1" ]; then
  echo "Flashing JetPack $JP_VERSION to eMMC"
  wait_for_recovery_device
  set +e
  sudo ./flash.sh "$BOARD" internal | tee "$WORK_DIR/flash_emmc_${JP_VERSION}.log"
  RC=${PIPESTATUS[0]}
  set -e
  if [ $RC -eq 0 ] && [ -f "bootloader/flashcmd.txt" ]; then
    echo "Installation completed successfully"
    echo "You can continue on the Jetson device"
    exit 0
  else
    echo "Installation failed"
    exit 1
  fi
elif [ "$TARGET_CHOICE" = "2" ]; then
  echo "Flashing JetPack $JP_VERSION to NVMe"
  wait_for_recovery_device
  set +e
  sudo ./tools/kernel_flash/l4t_initrd_flash.sh \
    --external-device nvme0n1p1 \
    -c ./tools/kernel_flash/flash_l4t_t234_nvme.xml \
    --showlogs --network usb0 "$BOARD" external \
    | tee "$WORK_DIR/flash_nvme_${JP_VERSION}.log"
  RC=${PIPESTATUS[0]}
  set -e
  if [ $RC -eq 0 ] && [ -d "initrdlog" ] && [ -n "$(ls -A initrdlog 2>/dev/null)" ]; then
    echo "Installation completed successfully"
    echo "You can continue on the Jetson device"
    exit 0
  else
    echo "Installation failed"
    exit 1
  fi
else
  echo "Invalid selection"
  exit 1
fi
