from __future__ import annotations

# Streamlit page config (call exactly once)
import streamlit as st
st.set_page_config(page_title="Jetson YOLO Demo", layout="wide")

# Standart / third-party imports
import os
import glob
import cv2
import time
import shutil
import queue
import re
import subprocess
import threading
from typing import Optional, Tuple, List

import numpy as np
from ultralytics import YOLO


# Configuration / Constants
APP_TITLE = "Jetson Orin – YOLO Streamlit Demo"
DEFAULT_MODEL_PATH = "yolo11m.pt"
DEFAULT_UDP_PORT = 5000

# FFmpeg UDP URL variants commonly supported by OpenCV builds
FFMPEG_URL_BIND_ANY = "udp://@:{port}"
FFMPEG_URL_BIND_ALL = (
    "udp://0.0.0.0:{port}"
    "?fifo_size=100000&overrun_nonfatal=1&buffer_size=0&timeout=500000"
)

# Tegrastats line pattern (tolerant to spacing differences for *_FREQ keys)
TEGRAPATTERN = re.compile(
    r"RAM\s+(?P<ram_used>\d+)\/(?P<ram_total>\d+)MB.*?"
    r"CPU\s+\[(?P<cpu>.+?)\].*?"
    r"EMC[_ ]FREQ\s+(?P<emc_pct>\d+)%@(?P<emc_mhz>\d+).*?"
    r"GR3D[_ ]FREQ\s+(?P<gr3d_pct>\d+)%@(?P<gr3d_mhz>\d+).*?"
    r".*?GPU@(?P<gpu_temp>[\d\.]+)C",
    re.IGNORECASE,
)


# Single-responsibility classes
class DeviceInfo:
    """Detect and cache device capability (CPU/GPU via PyTorch)."""

    def __init__(self) -> None:
        """Probe torch.cuda and cache basic properties."""
        try:
            import torch  # local import to avoid hard dependency elsewhere
            self.torch = torch
            self.is_gpu = torch.cuda.is_available()
            self.name = torch.cuda.get_device_name(0) if self.is_gpu else "CPU"
        except Exception:
            self.torch = None
            self.is_gpu = False
            self.name = "CPU"

    def render_sidebar(self) -> None:
        """Render a short CUDA availability summary in the sidebar."""
        st.sidebar.success(f"CUDA: {'ON' if self.is_gpu else 'OFF'} | Device: {self.name}")

    def cuda_memory_summary(self) -> Optional[str]:
        """Return a string summary of CUDA memory usage or None if not available."""
        if not self.is_gpu or self.torch is None:
            return None
        alloc = self.torch.cuda.memory_allocated(0) / (1024 ** 2)
        reserved = self.torch.cuda.memory_reserved(0) / (1024 ** 2)
        total = self.torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
        return f"CUDA Memory → Alloc: {alloc:.1f} MB | Reserved: {reserved:.1f} MB | Total: {total:.0f} MB"


class YoloPredictor:
    """Ultralytics YOLO model wrapper for annotated inference."""

    def __init__(self, model_path: str, device: DeviceInfo) -> None:
        """
        Load YOLO model.

        Args:
            model_path: Path to .pt model file inside the container.
            device: Device information (to choose device 0/CPU).
        """
        self.model = YOLO(model_path)
        self._use_gpu = device.is_gpu

    def predict_annotated(self, frame_bgr: np.ndarray, conf: float) -> np.ndarray:
        """
        Run YOLO inference on BGR frame and return annotated BGR.

        Args:
            frame_bgr: Input frame (OpenCV BGR).
            conf: Confidence threshold.

        Returns:
            Annotated frame in BGR.
        """
        res = self.model.predict(
            frame_bgr, conf=conf, device=0 if self._use_gpu else None, verbose=False
        )[0]
        return res.plot()


class MetricsMonitor:
    """Background tegrastats reader + parser using a thread."""

    def __init__(self, pattern: re.Pattern = TEGRAPATTERN) -> None:
        """
        Initialize a tegrastats monitor.

        Args:
            pattern: Compiled regex to parse tegrastats lines.
        """
        self._pattern = pattern
        self._queue: "queue.Queue[dict]" = queue.Queue(maxsize=1)
        self._proc: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._last_raw: str = ""

    def _reader(self) -> None:
        """Spawn tegrastats and push parsed results into a queue."""
        try:
            ts_path = shutil.which("tegrastats") or "/usr/bin/tegrastats"
            if not os.path.exists(ts_path):
                return
            self._proc = subprocess.Popen(
                [ts_path, "--interval", "1000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert self._proc.stdout is not None
            for line in self._proc.stdout:
                self._last_raw = line.strip()
                m = self._pattern.search(line)
                if m:
                    data = m.groupdict()
                    try:
                        self._queue.get_nowait()
                    except queue.Empty:
                        pass
                    self._queue.put_nowait(data)
        except Exception:
            # Never touch Streamlit API here; just exit quietly.
            pass

    def start(self) -> None:
        """Start reader thread (idempotent)."""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._reader, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Terminate tegrastats process if running (optional)."""
        try:
            if self._proc and self._proc.poll() is None:
                self._proc.terminate()
        except Exception:
            pass

    def latest(self) -> Tuple[Optional[dict], str]:
        """
        Get the latest parsed metrics and last raw line.

        Returns:
            (metrics_dict_or_None, last_raw_string)
        """
        try:
            data = self._queue.get_nowait()
        except queue.Empty:
            data = None
        return data, self._last_raw


# ----- Singleton factory for MetricsMonitor (prevents rerun restarts) -----
@st.cache_resource(show_spinner=False)
def get_metrics_monitor() -> MetricsMonitor:
    """
    Create/return a single MetricsMonitor for the whole app session.
    Prevents re-spawning tegrastats on every Streamlit rerun.
    """
    mon = MetricsMonitor()
    mon.start()
    return mon

class VideoReceiver:
    """Create OpenCV captures for different sources (FFmpeg-only for UDP)."""

    @staticmethod
    def open_file(path: str) -> Optional[cv2.VideoCapture]:
        """Open a local video file for reading."""
        cap = cv2.VideoCapture(path)
        return cap if cap.isOpened() else None

    @staticmethod
    def open_webcam(index: int = 0) -> Optional[cv2.VideoCapture]:
        """Open a V4L2 webcam device (requires --device /dev/video0)."""
        cap = cv2.VideoCapture(index)
        return cap if cap.isOpened() else None

    @staticmethod
    def _set_low_buffer(cap: cv2.VideoCapture) -> None:
        """Try to reduce internal buffering for lower latency."""
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

    def open_udp_ffmpeg(self, port: int) -> Tuple[Optional[cv2.VideoCapture], Optional[str]]:
        """
        Open a UDP source via OpenCV's FFmpeg backend, trying two URL variants.

        Returns:
            (cap, used_url) where cap is VideoCapture or None; used_url is the URL string.
        """
        url1 = FFMPEG_URL_BIND_ANY.format(port=port)      # udp://@:5000
        cap = cv2.VideoCapture(url1, cv2.CAP_FFMPEG)
        if cap.isOpened():
            self._set_low_buffer(cap)
            return cap, url1

        url2 = FFMPEG_URL_BIND_ALL.format(port=port)      # udp://0.0.0.0:5000?...
        cap = cv2.VideoCapture(url2, cv2.CAP_FFMPEG)
        if cap.isOpened():
            self._set_low_buffer(cap)
            return cap, url2

        return None, None


class InferenceLoop:
    """Drives capture → inference → display → metrics rendering."""

    def __init__(
        self,
        predictor: YoloPredictor,
        device: DeviceInfo,
        metrics: Optional[MetricsMonitor],
        fps_placeholder: "st.delta_generator.DeltaGenerator",
        mon_placeholder: "st.delta_generator.DeltaGenerator",
        cuda_placeholder: "st.delta_generator.DeltaGenerator",
    ) -> None:
        """Compose inference dependencies."""
        self.predictor = predictor
        self.device = device
        self.metrics = metrics
        self.fps_placeholder = fps_placeholder
        self.mon_placeholder = mon_placeholder
        self.cuda_placeholder = cuda_placeholder

    def _render_metrics(self, show_cuda_mem: bool) -> None:
        """Render tegrastats metrics and optional CUDA memory info."""
        data, last_raw = (None, "")
        if self.metrics is not None:
            data, last_raw = self.metrics.latest()

        with self.mon_placeholder.container():
            c1, c2, c3, c4, c5 = st.columns(5)
            if data:
                c1.metric("GPU Util", f"{data.get('gr3d_pct', '?')}%")
                c2.metric("GPU Clock", f"{data.get('gr3d_mhz', '?')} MHz")
                c3.metric("RAM Used", f"{data.get('ram_used', '?')}/{data.get('ram_total', '?')} MB")
                c4.metric("EMC", f"{data.get('emc_pct', '?')}% @ {data.get('emc_mhz', '?')} MHz")
                c5.metric("GPU Temp", f"{data.get('gpu_temp', '?')} °C")
            else:
                if last_raw:
                    st.write(f"tegrastats (raw): {last_raw}")
                else:
                    st.caption("Waiting for tegrastats...")

        if show_cuda_mem:
            summary = self.device.cuda_memory_summary()
            if summary:
                self.cuda_placeholder.info(summary)

    def run(self, cap: cv2.VideoCapture, conf: float, max_fps: int, show_cuda_mem: bool) -> None:
        """Main loop: read frames, infer, display, update metrics."""
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # low latency
        except Exception:
            pass

        stframe = st.empty()
        last_emit = 0.0
        frame_count = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            now = time.time()
            if now - last_emit < 1.0 / max(max_fps, 1):
                continue
            last_emit = now

            t0 = time.time()
            annotated = self.predictor.predict_annotated(frame, conf=conf)
            dt = time.time() - t0

            frame_count += 1
            if frame_count % 5 == 0:
                self.fps_placeholder.write(f"Pipeline FPS: {1.0 / max(dt, 1e-6):.1f}")

            stframe.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB")
            self._render_metrics(show_cuda_mem=show_cuda_mem)


# UI helpers
def list_videos_under(path: str = "/videos") -> List[str]:
    """List video files under a directory."""
    exts = (".mp4", ".mov", ".avi", ".mkv")
    files = [p for p in glob.glob(os.path.join(path, "*")) if p.lower().endswith(exts)]
    return sorted(files)


def sidebar_controls() -> tuple:
    """
    Render and read all Streamlit sidebar controls.

    Returns:
        mode, conf, max_fps, mon_on, show_cuda_mem, udp_port
    """
    st.sidebar.header("Source")
    mode = st.sidebar.radio(
        "Select",
        ["Mounted Video (/videos)", "Upload Video", "Webcam", "UDP Stream"],
        index=0,
    )
    conf = st.sidebar.slider("Confidence", 0.1, 0.9, 0.25, 0.05)
    max_fps = st.sidebar.slider("Max FPS", 5, 120, 60, 1)

    st.sidebar.header("Monitoring")

    # Keep the toggle stable across reruns
    if "mon_on" not in st.session_state:
        st.session_state["mon_on"] = True
    mon_on = st.sidebar.toggle("Enable tegrastats", value=st.session_state["mon_on"], key="mon_on")

    show_cuda_mem = st.sidebar.checkbox("Show CUDA Memory (PyTorch)", value=True)

    st.sidebar.header("UDP Settings")
    udp_port = int(st.sidebar.number_input("UDP Port", min_value=1024, max_value=65535, value=DEFAULT_UDP_PORT))

    return mode, conf, max_fps, mon_on, show_cuda_mem, udp_port


# Main (composition root)
def main() -> None:
    """Wire everything together and handle UI routing."""
    st.title(APP_TITLE)

    # Device & model
    device = DeviceInfo()
    device.render_sidebar()
    predictor = YoloPredictor(DEFAULT_MODEL_PATH, device)

    # Sidebar controls
    mode, conf, max_fps, mon_on, show_cuda_mem, udp_port = sidebar_controls()

    # Monitoring (singleton via cache_resource)
    metrics: Optional[MetricsMonitor] = None
    if mon_on:
        metrics = get_metrics_monitor()
        # Keep a reference if you want to stop later
        st.session_state["_mon_ref"] = metrics
    else:
        # Optional: stop if user toggles off
        mon_ref = st.session_state.get("_mon_ref")
        if mon_ref:
            mon_ref.stop()
            st.session_state["_mon_ref"] = None

    # Placeholders
    fps_ph = st.empty()
    mon_ph = st.empty()
    cuda_ph = st.empty()

    # Orchestrator
    loop = InferenceLoop(
        predictor=predictor,
        device=device,
        metrics=metrics,
        fps_placeholder=fps_ph,
        mon_placeholder=mon_ph,
        cuda_placeholder=cuda_ph,
    )

    # Receivers
    receiver = VideoReceiver()

    # Routes
    if mode == "Mounted Video (/videos)":
        files = list_videos_under("/videos")
        if not files:
            st.warning("No videos found under /videos.")
            return

        choice = st.selectbox("Select video", files, index=0)
        if st.button("Start"):
            cap = receiver.open_file(choice)
            if cap is None:
                st.error(f"Cannot open: {choice}")
                return
            loop.run(cap, conf=conf, max_fps=max_fps, show_cuda_mem=show_cuda_mem)
            cap.release()
            st.success("Finished.")

    elif mode == "Upload Video":
        up = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv"])
        if up and st.button("Start"):
            tfile = "input.mp4"
            with open(tfile, "wb") as f:
                f.write(up.read())
            cap = receiver.open_file(tfile)
            if cap is None:
                st.error("Uploaded video cannot be opened.")
                return
            loop.run(cap, conf=conf, max_fps=max_fps, show_cuda_mem=show_cuda_mem)
            cap.release()
            st.success("Finished.")

    elif mode == "Webcam":
        st.info("Start the container with --device /dev/video0")
        if st.button("Start Webcam"):
            cap = receiver.open_webcam(0)
            if cap is None:
                st.error("Webcam cannot be opened.")
                return
            loop.run(cap, conf=conf, max_fps=max_fps, show_cuda_mem=show_cuda_mem)
            cap.release()
            st.success("Finished.")

    else:  # UDP Stream (FFmpeg backend only)
        st.write(f"Listening on UDP port {udp_port}")
        st.caption(
            "Sender example (laptop):\n"
            "ffmpeg -f v4l2 -thread_queue_size 256 -framerate 30 -video_size 640x480 -i /dev/video0 "
            "-pix_fmt yuv420p -c:v libx264 -preset ultrafast -tune zerolatency "
            "-x264-params \"repeat-headers=1:keyint=30:min-keyint=30:scenecut=0\" "
            "-g 30 -keyint_min 30 -sc_threshold 0 -b:v 2M -maxrate 2M -bufsize 2M "
            "-muxpreload 0 -muxdelay 0 "
            f"-f mpegts udp://JETSON_IP:{udp_port}?pkt_size=1316"
        )

        if "udp_running" not in st.session_state:
            st.session_state["udp_running"] = False
            st.session_state["udp_cap"] = None

        c1, c2 = st.columns(2)
        with c1:
            start_clicked = st.button("Start UDP Stream")
        with c2:
            stop_clicked = st.button("Stop UDP Stream")

        if start_clicked and not st.session_state["udp_running"]:
            cap, used_url = receiver.open_udp_ffmpeg(udp_port)
            if cap is None:
                st.error("Cannot open UDP stream. Verify sender IP/port, host networking or port mapping, and try a different port.")
                return
            st.info(f"UDP opened via FFmpeg URL: {used_url}")
            st.session_state["udp_cap"] = cap
            st.session_state["udp_running"] = True
            loop.run(cap, conf=conf, max_fps=max_fps, show_cuda_mem=show_cuda_mem)
            cap.release()
            st.session_state["udp_running"] = False
            st.success("UDP stream finished.")

        if stop_clicked and st.session_state["udp_running"]:
            cap = st.session_state.get("udp_cap")
            if cap and cap.isOpened():
                cap.release()
            st.session_state["udp_running"] = False
            st.success("UDP stream stopped.")


# Entrypoint
if __name__ == "__main__":
    main()
