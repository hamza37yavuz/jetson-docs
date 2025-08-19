# Comparative Analysis of NVIDIA Jetson Platforms

This report provides a comprehensive, hardware-based comparison of the NVIDIA Jetson family of edge AI computing devices, spanning from the earliest Jetson TK1 to the latest Jetson AGX Thor. The analysis focuses on key hardware components such as GPUs, CPUs, memory capacity, AI performance, and power consumption. In addition, it outlines the typical use cases of different Jetson modules, highlighting where each platform is most effectively applied in training, inference, and real-time applications.

The following abbreviations are used throughout the report:

**IoT:** Internet of Things

**TOPS:** Tera Operations per Second

**TFLOPS:** Tera Floating Point Operations per Second

**FP:** Floating Point
---

## 1. Jetson GPU Comparison

| Jetson Model             | GPU Architecture | CUDA Cores | Tensor Cores | Notes on GPU Features|
| ------------------------ | ---------------- | ---------- | ------------ | - |
| Jetson TK1 (2014)        | Kepler           | 192        | –            | Early CUDA support, no Tensor Cores      |
| Jetson TX1 (2015)        | Maxwell          | 256        | –            | Improved efficiency, FP16 supported      |
| Jetson TX2 (2017)        | Pascal           | 256        | –            | Higher FP16 throughput achieved          |
| Jetson Nano (2019)       | Maxwell          | 128        | –            | Entry-level GPU, no Tensor Cores         |
| Jetson Xavier NX (2020)  | Volta            | 384        | 48           | First Tensor Cores integrated, INT8 used |
| Jetson AGX Xavier (2018) | Volta            | 512        | 64           | Strong FP16/INT8 acceleration provided   |
| Jetson Orin Nano (2022)  | Ampere           | 1024       | 32           | Ampere-based, Tensor Cores optimized     |
| Jetson Orin NX (2022)    | Ampere           | 1024       | 32           | High bandwidth, improved INT8/FP16       |
| Jetson AGX Orin (2022)   | Ampere           | 2048       | 64           | 200+ TOPS enabled, BF16/TF32 supported   |
| Jetson AGX Thor (2025)   | Blackwell        | 2560       | Advanced Gen | FP8/FP4 supported, optimized for LLMs    |

### GPU Architecture Evolution

| Architecture  | Release Year | Features|
| ------------- | ------------ | --------------------- |
| **Kepler**    | 2012         | First CUDA unified shader architecture introduced. Energy efficiency was moderate, but no AI optimization was available. FP32 dominated, with very limited deep learning support.                          |
| **Maxwell**   | 2014         | Power consumption was reduced, making it suitable for mobile systems. FP16 support was added, but Tensor Cores were absent, resulting in limited deep learning acceleration.                               |
| **Pascal**    | 2016         | Efficiency was improved, FP16 throughput significantly enhanced, and inference speed increased. Tensor Cores were still not available.                                                                     |
| **Volta**     | 2017         | Tensor Cores were introduced for the first time, enabling substantial improvements in training and inference acceleration. Strong FP16 and INT8 performance was achieved.                                  |
| **Ampere**    | 2020         | Advanced Tensor Cores were implemented with sparsity support, allowing neural network optimizations by skipping zeros. TF32 was added, providing a major leap in AI performance and energy efficiency.     |
| **Blackwell** | 2024         |Tensor Cores were expanded significantly, with FP8/FP4 precision introduced. The design was optimized for LLMs and large-scale transformers. Performance per watt was increased several times over Ampere. |

---

## 2. Jetson CPU Comparison

| Jetson Model| CPU Type| Notes|
| ------------ | ------------------ | -------- |
| Jetson TK1 (2014)        | 4× ARM Cortex-A15          | Utilized early ARMv7 architecture; provided the foundation for Jetson platforms.                   |
| Jetson TX1 (2015)        | 4× ARM Cortex-A57          | Introduced ARMv8-A 64-bit architecture, enabling higher efficiency and performance.                |
| Jetson TX2 (2017)        | 2× Denver2 + 4× Cortex-A57 | Combined NVIDIA’s custom Denver2 cores with ARM Cortex-A57, offering a hybrid processing approach. |
| Jetson Nano (2019)       | 4× ARM Cortex-A57          | Based on the TX1 CPU architecture, optimized for lower power consumption.                          |
| Jetson AGX Xavier (2018) | 8× Carmel ARMv8.2          | Featured NVIDIA’s custom Carmel cores, designed for advanced AI workloads.                         |
| Jetson Xavier NX (2020)  | 6× Carmel ARMv8.2          | Delivered a smaller-scale implementation of Carmel cores for embedded systems.                     |
| Jetson Orin Nano (2022)  | 6× ARM Cortex-A78AE        | Integrated Automotive Enhanced (AE) cores with functional safety features.                         |
| Jetson Orin NX (2022)    | 8× ARM Cortex-A78AE        | Provided a more powerful automotive-grade ARM cluster, enhancing safety and performance.           |
| Jetson AGX Orin (2022)   | 12× ARM Cortex-A78AE       | High-performance multi-core cluster designed for large-scale AI inference.                         |
| Jetson AGX Thor (2025)   | 14× ARM Neoverse-V3AE      | Latest ARM server-grade cores with advanced efficiency and scalability.                            |


---

## 3. Jetson Usage Comparison

The evolution of the Jetson family demonstrates a clear progression from basic prototyping platforms to advanced AI accelerators capable of handling large-scale inference and training workloads. Early platforms such as the Jetson TK1 and TX1 were primarily suitable for robotics education and entry-level prototyping, with limited inference performance and no practical training capability. The Jetson TX2 introduced greater efficiency, enabling small-scale models to be trained and deployed on UAVs and embedded systems. The Jetson Nano further democratized AI development for makers and educational purposes by providing affordable yet capable CNN inference.

The introduction of the Xavier series, including the Xavier NX and AGX Xavier, marked a significant leap with NVIDIA’s Carmel cores and Volta GPUs, allowing medium-scale models to be trained and deployed on robotics and industrial platforms. With the transition to the Orin family, based on Ampere architecture, training and inference capabilities expanded considerably. The Orin Nano and Orin NX brought high-performance inference to edge robotics and drones, while the AGX Orin enabled medium-to-large model training and advanced inference suitable for autonomous vehicles. The upcoming Jetson AGX Thor, built on the Blackwell architecture with Neoverse-V3AE CPUs, is positioned to support next-generation applications such as humanoid robotics and large multimodal AI workloads, offering transformer-scale inference performance.

---

## 4. Chronological Jetson Comparison (2014–2025)

| Year | Jetson Model| CPU| GPU Architecture| Memory| AI Performance (FP32/FP16 TFLOPS) | AI Performance (INT8/AI TOPS)| Power Consumption (W)|
| ---- | -------------- | ---------------- | ------------ | --------- | -------- | ------------------ | ------ |
| 2014 | Jetson TK1        | 4× Cortex-A15       | Kepler (192 CUDA)                      | 2 GB      | \~0.3 TFLOPS FP32                 | –                             | \~5–10 W              |
| 2015 | Jetson TX1        | 4× Cortex-A57       | Maxwell (256 CUDA)                     | 4 GB      | \~1.0 TFLOPS FP32                 | –                             | \~10–15 W             |
| 2017 | Jetson TX2        | 2× Denver2 + 4× A57 | Pascal (256 CUDA)                      | 8 GB      | \~1.3 TFLOPS FP32 / \~2.6 FP16    | –                             | \~7.5–15 W (Max 20 W) |
| 2018 | Jetson AGX Xavier | 8× Carmel ARMv8.2   | Volta (512 CUDA, 64 Tensor)            | 16–32 GB  | \~11 TFLOPS FP16                  | \~30 TOPS INT8                | 10–30 W (Max 30 W)    |
| 2019 | Jetson Nano       | 4× Cortex-A57       | Maxwell (128 CUDA)                     | 2–4 GB    | \~0.5 TFLOPS FP16                 | –                             | 5–10 W                |
| 2020 | Jetson Xavier NX  | 6× Carmel ARMv8.2   | Volta (384 CUDA, 48 Tensor)            | 8–16 GB   | \~6 TFLOPS FP16                   | \~21 TOPS INT8                | 10–15 W               |
| 2022 | Jetson Orin Nano  | 6× Cortex-A78AE     | Ampere (1024 CUDA, 32 Tensor)          | 4–8 GB    | \~40 TFLOPS FP16                  | 20–40 TOPS INT8               | 10–15 W               |
| 2022 | Jetson Orin NX    | 8× Cortex-A78AE     | Ampere (1024 CUDA, 32 Tensor)          | 8–16 GB   | \~70 TFLOPS FP16                  | 117–157 TOPS INT8             | 10–25 W               |
| 2022 | Jetson AGX Orin   | 12× Cortex-A78AE    | Ampere (2048 CUDA, 64 Tensor)          | 32–64 GB  | \~275 TFLOPS FP16/BF16            | 200–275 TOPS INT8             | 15–60 W               |
| 2025 | Jetson AGX Thor   | 14× Neoverse-V3AE   | Blackwell (2560 CUDA, Advanced Tensor) | 64–128 GB | \~1000+ TFLOPS FP8/FP16           | \~1000+ TOPS (FP8/INT8 mixed) | \~60–80 W (Est.)      |

