# Flashing NVIDIA Jetson AGX Orin (64 GB Developer Kit) With CMD

## Introduction

This report documents how JetPack 6.1 was provisioned on a Jetson AGX Orin Devkit using the Linux for Tegra (L4T) R36.4.x release. The procedure was carried out from an Ubuntu host machine. Official release artifacts were retrieved, the root filesystem was prepared, device-specific binaries were applied, and the target was flashed to NVMe. After first boot, base packages were updated and optional components were installed. Commands are shown exactly as executed.

---

## Retrieval of Release Artifacts

The required L4T release package and the sample root filesystem were downloaded from NVIDIA’s distribution site. It was ensured that sufficient disk space was available before initiating the downloads.

```bash
wget https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v4.0/release/Jetson_Linux_R36.4.0_aarch64.tbz2
wget https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v4.0/release/Tegra_Linux_Sample-Root-Filesystem_R36.4.0_aarch64.tbz2
```

---

## Environment and Variables

To ensure reproducibility, environment variables were defined for the release packages and board configuration. These variables were used consistently across subsequent steps.

```bash
L4T_RELEASE_PACKAGE=Jetson_Linux_R36.4.0_aarch64.tbz2
SAMPLE_FS_PACKAGE=Tegra_Linux_Sample-Root-Filesystem_R36.4.0_aarch64.tbz2
BOARD=jetson-agx-orin-devkit
```

---

## Preparation of the L4T Tree and Root Filesystem

The L4T release archive was extracted to create the `Linux_for_Tegra` workspace. The sample root filesystem was then expanded into the `rootfs` directory. Prerequisites were applied to the host, followed by board-specific binary application.

```bash
tar xf ${L4T_RELEASE_PACKAGE}
sudo tar xpf ${SAMPLE_FS_PACKAGE} -C Linux_for_Tegra/rootfs/
cd Linux_for_Tegra/
sudo ./tools/l4t_flash_prerequisites.sh
sudo ./apply_binaries.sh
```

The above sequence ensured that the base Ubuntu root filesystem was populated and that proprietary drivers, firmware, and board support files were staged appropriately.

---

## Flashing to NVMe (Jetson AGX Orin Devkit)

The device was flashed to the NVMe drive using the initrd flash utility and the provided NVMe flashing configuration. USB device-mode networking (`usb0`) was used for transport, and verbose logs were enabled to facilitate troubleshooting.

```bash
sudo ./tools/kernel_flash/l4t_initrd_flash.sh --external-device nvme0n1p1 \
  -c tools/kernel_flash/flash_l4t_t234_nvme.xml \
  --showlogs --network usb0 jetson-agx-orin-devkit external
```

After completion, the board was allowed to boot normally from the newly provisioned NVMe root device.

---

## Post-Boot System Initialization

Once the Jetson system reached the desktop/console, the package index was refreshed to bring the system up to date.

```bash
sudo apt update
```

If a Chromium browser was not pulled during setup, it was installed via Snap. Python tooling and jetson-stats were also installed to assist with basic system monitoring. A system reboot was performed to finalize changes.

```bash
snap install chromium
sudo apt install python3-pip
sudo pip3 install -U jetson-stats
reboot
```

---

## Optional: JetPack Meta-Package Installation

Where a full JetPack meta-package was required (CUDA, cuDNN, TensorRT, multimedia, and related SDK components), the package index was searched and the meta-package was installed. This step was carried out only after confirming the desired component set.

```bash
apt search nvidia-jetpack
sudo apt install nvidia-jetpack
```

---

## Notes and Considerations

It was confirmed that the commands matched the specified board name (`jetson-agx-orin-devkit`) and that the NVMe partition (`nvme0n1p1`) was targeted intentionally. If a different storage layout or carrier board were to be used, the corresponding flash XML and board identifier would need to be adjusted accordingly. During flashing, the device was placed into recovery mode and appropriate cabling was verified to prevent transport errors.

---

## Reference

NVIDIA Jetson Linux (R36.4.x) Quick Start Guide: [https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/IN/QuickStart.html](https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/IN/QuickStart.html)
