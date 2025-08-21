# Model Deployment With Docker

## Introduction

This report presents the design and deployment of a real-time object detection pipeline using the YOLOv11m model on the NVIDIA Jetson AGX Orin Developer Kit. The solution integrates a Streamlit-based web interface with hardware monitoring and supports multiple video input modes, including local video files, uploaded videos, and live UDP streams (from a remote laptop camera).

The workflow allows researchers and developers to run GPU-accelerated inference while observing Jetson system metric such as GPU utilization, CPU load, memory consumption, and temperature.

---

## 1. System Overview

The architecture of the application consists of the following components:

* **YOLOv11m Model** – Pre-trained Ultralytics model for real-time object detection.
* **Streamlit Web Application** – Provides a user interface for selecting input sources, adjusting inference parameters, and visualizing detection results.
* **FFmpeg-based UDP Streaming** – Enables external video input from a laptop webcam to the Jetson device.
* **Tegrastats Monitor** – Reports GPU, CPU, memory, and power usage directly from the Jetson hardware.

### Application Classes

DeviceInfo – Collects and reports Jetson hardware information such as GPU model, memory capacity, and software versions.

YoloPredictor – Handles YOLOv11m model loading, preprocessing, inference, and rendering of detection results on video frames.

MetricsMonitor – Runs tegrastats in a background thread, continuously parsing GPU/CPU/memory utilization and providing real-time metrics to Streamlit.

VideoReceiver – Manages input streams, including mounted videos, uploaded files, and UDP streams, ensuring frames are captured reliably.

InferenceLoop – Controls the end-to-end inference pipeline by fetching frames from the receiver, applying YOLO predictions, enforcing FPS limits, and sending results to the web interface.


The general workflow is:

1. Select input source (mounted video, uploaded file, or UDP stream).
2. Perform inference using YOLOv11m with configurable confidence threshold and FPS limit.
3. Render annotated frames inside Streamlit.
4. Continuously monitor Jetson hardware statistics in a dedicated panel.

---

## 2. Hardware and Software Requirements

### Jetson AGX Orin

### Host / Laptop (UDP sender)

### Software Stack

* **Docker base image**: `ultralytics/ultralytics:latest-jetson-jetpack6`
* **YOLO framework**: Ultralytics 8.3+
* **Frontend**: Streamlit 1.37+
* **Python packages**: OpenCV, Torch, NumPy

---

## 3. Input Modes

The application supports three types of input streams:

1. **Mounted Video Directory**

   * A host directory (e.g., `/videos`) is mounted into the container.
   * User selects a video file and runs inference directly.

2. **File Upload**

   * Users can upload `.mp4`, `.avi`, or `.mkv` files through the web interface.
   * Uploaded video is stored in a temporary directory and processed frame by frame.

3. **Live UDP Stream**

   * Laptop sends webcam frames to the Jetson device over the same network:

   ```bash
   ffmpeg -f v4l2 -i /dev/video0 -vf scale=640:480 -c:v libx264 -preset ultrafast -f mpegts udp://<JETSON_IP>:5000
   ```

   * Jetson receives and decodes using OpenCV with FFmpeg backend:

   ```python
   cv2.VideoCapture("udp://0.0.0.0:5000?overrun_nonfatal=1&fifo_size=5000000", cv2.CAP_FFMPEG)
   ```

---

## 4. Streamlit Application Structure

### Sidebar Controls

* **Input source** – Select between mounted video, file upload, or UDP stream
* **Confidence threshold** – Adjust YOLO detection confidence
* **FPS limit** – Throttle inference rate to balance speed and latency
* **Start/Stop buttons** – Control video streaming and inference execution

### Main Display

* **Annotated frames** – Display YOLO detection results in real time
* **Tegrastats panel** – Continuously updated system resource usage

---

## 5. Performance Considerations

Several measures were applied to reduce latency and ensure smooth inference:

* **FFmpeg backend** – More reliable than GStreamer for UDP input decoding.
* **Frame skipping (FPS limiter)** – Prevents backlog when the incoming stream is faster than processing speed.
* **Tegrastats thread isolation** – Runs system monitoring in a background thread without refreshing the entire Streamlit page.
* **Stop button** – Allows graceful termination of UDP capture without restarting the container.

---

## 6. Deployment with Docker

The following Dockerfile was used:

```dockerfile
FROM ultralytics/ultralytics:latest-jetson-jetpack6

RUN pip install --no-cache-dir streamlit==1.37.0

WORKDIR /app
COPY app.py /app/app.py
COPY test.mp4 /videos/test.mp4

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

Run the container with:

```bash
sudo docker run -it --rm \
  --runtime=nvidia --ipc=host \
  --network=host \
  -v /home/adasi/videos:/videos:ro \
  -v /usr/bin/tegrastats:/usr/bin/tegrastats:ro \
  --privileged \
  jetson-yolo-streamlit:jp6
```

---

## 7. Verification

After deployment, verify the following:

* **YOLO Model Load** – Confirm `yolo11m.pt` initializes successfully.
* **UDP Stream** – Ensure frames are received from laptop without packet loss.
* **Tegrastats** – Verify GPU utilization, CPU load, and temperatures update live.
* **Latency** – Test with FPS limiter (20–30 FPS) to minimize lag.

---

## Conclusion

This pipeline demonstrates a practical deployment of **real-time object detection** on the Jetson AGX Orin with YOLOv11m. By combining Streamlit, FFmpeg, and tegrastats, the system provides:

* A flexible interface for video input and inference.
* Real-time hardware monitoring during AI workloads.
* UDP-based external webcam integration for remote testing.

The setup enables researchers to experiment with optimized AI pipelines on embedded hardware, ensuring both inference performance and system stability.
