# Flashing NVIDIA Jetson AGX Orin (64 GB Developer Kit)

## Introduction

This document has been prepared to provide a structured overview of the NVIDIA Jetson AGX Orin (64 GB Developer Kit) flashing process. The report first presents the essential hardware interfaces of the device, then outlines the installation of **NVIDIA SDK Manager** on the host machine, and finally describes the procedure for placing the device into recovery mode. The subsequent steps regarding target device selection, storage configuration, and verification of the installation are also included. By following the workflow, the Jetson AGX Orin can be properly initialized for GPU-accelerated AI development.

---

## 1. Hardware Overview

The Jetson AGX Orin Developer Kit integrates the module with a carrier board and provides several input/output interfaces. Among the most relevant hardware features are:

* **USB-C port** (used for flashing in recovery mode)
* **USB 3.2 Type-A ports (×2)** for peripheral devices
* **HDMI 2.1 and DisplayPort 1.4a outputs** for display connection
* **Dual RJ-45 Gigabit Ethernet ports** with teaming support
* **M.2 Key-E and Key-M slots** for Wi-Fi/Bluetooth modules and SSDs
* **40-pin GPIO header** for general-purpose interfacing

A detailed layout of the board is shown in the official NVIDIA documentation:
[Jetson AGX Orin Developer Kit Layout](https://developer.nvidia.com/embedded/learn/jetson-agx-orin-devkit-user-guide/howto.html)

---

## 2. Host Machine Requirements and SDK Manager Installation

Flashing requires a host PC running Ubuntu 20.04 LTS or 22.04 LTS (x86\_64). A minimum of 4 CPU cores, 16 GB of RAM (32 GB recommended), and 100 GB of free disk space** should be available.

SDK Manager must be downloaded from the official NVIDIA Developer website and installed as follows:

```bash
sudo apt install ./sdkmanager_[version]_amd64.deb
```

Once installed, SDK Manager can be launched either from the applications menu or by executing:

```bash
sdkmanager
```

On first launch, the user will be prompted to log in with an NVIDIA Developer account.

---

## 3. Recovery Mode Procedure

![Jetson AGX Orin Developer Kit Layout](https://developer.download.nvidia.com/embedded/images/jetsonAgxOrin/getting_started/jaodk_labeled_01.png)


Before flashing, the Jetson AGX Orin must be placed into **Recovery Mode**. This is achieved using the hardware buttons on the carrier board:

1. **Power Button** – Turns the device on or off.
2. **Force Recovery Button** – Must be pressed and held when initiating recovery.
3. **Reset Button** – Used to reboot the device if required.

**Procedure:**

* Ensure the device is powered off.
* Hold down the **Force Recovery button**.
* While holding it, press the **Power button** once.
* After a few seconds, release the Recovery button.

On the host machine, correct detection can be verified with:

```bash
lsusb
```

If successful, the device will appear as **NVIDIA Corp. APX device**.

---

## 4. Device Selection and Storage Configuration

After the device is detected, SDK Manager allows selection of the target hardware (**Jetson AGX Orin**). If the developer kit includes an SSD, installation can be directed onto the SSD by choosing it as the primary storage target during the flashing process.

---

## 5. Verification of Installation

Once the flashing and JetPack installation are completed, the software versions on the Jetson AGX Orin should be verified. The following commands are typically used:

* Check JetPack release:

```bash
dpkg-query --show nvidia-l4t-core
```


* Verify CUDA installation:

```bash
nvcc --version
```

* Confirm device information:

```bash
tegrastats
```

* Check TensorRT version:

```bash
dpkg -l | grep nvinfer
```

---

## Conclusion

After flashing, it is recommended to verify the installed software stack. The following versions are typically provided with JetPack 6.2.1:

- CUDA: 12.6 (r12.6)

- Python: 3.10.12

- TensorRT: 10.3.0.30

- JetPack: 6.2.1

- cuDNN: 9.3.0.75-1

- Docker: 28.3.3

- L4T: 36.4.4

By following these procedures, the NVIDIA Jetson AGX Orin (64 GB Developer Kit) can be successfully flashed with the latest JetPack release. The system will then be fully prepared for accelerated AI workloads, supporting CUDA, cuDNN, TensorRT, and other components of the NVIDIA development ecosystem.

