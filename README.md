# NVIDIA Jetson Guide and Resources

This repository provides a hardware-based comparative analysis of NVIDIA Jetson platforms, from the earliest Jetson TK1 to the latest Jetson AGX Thor. It includes detailed tables covering CPU, GPU, memory, and AI performance specifications.  

In addition, a step-by-step flashing guide for the Jetson AGX Orin (64 GB Developer Kit) is provided, demonstrating how to set up the device with the latest JetPack release and verify CUDA, TensorRT, and other components after installation.  

The repository is intended as both a technical reference and a practical manual for developers working with NVIDIA Jetson edge AI devices.

## Contents

- [Comparative Analysis](comparative_analysis.md)  
  Detailed comparison of all Jetson modules and developer kits, including CPU, GPU and memory.

- [Flashing Jetson AGX Orin](flashing_sdk_manager.md)  
  Step-by-step guide for flashing the Jetson AGX Orin (64 GB Developer Kit) with NVIDIA SDK Manager, including recovery mode, storage configuration, and software verification.

- [Flashing JetPack 6.1 via CLI](flashing_cli_jetpack6_1.md)  
  Instructions for flashing Jetson AGX Orin using the command-line workflow (L4T release packages, rootfs preparation, and `l4t_initrd_flash.sh`).

- [Model Deployment with Docker](model_deployment_docker.md)  
  Real-time object detection pipeline using YOLOv11m on Jetson AGX Orin, deployed via Docker with Streamlit web interface, UDP video streaming, and hardware monitoring.
