#!/usr/bin/env python3
"""
Embedded Real-Time Computer Vision & Signal Processing Service
Target Platform: Headless Raspberry Pi OS (Bullseye / Buster)
Service Manager: systemd (cv-app.service)

Description:
    Reads video frames from configurable camera sources (UVC USB or CSI),
    applies real-time spatial (OpenCV) and spectral (SciPy FFT/Signal) processing,
    and logs performance metrics directly to stdout for journalctl.
"""

import sys
import os
import time
import logging
import signal

# Configure logging to stdout for systemd journalctl integration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [cv-app] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Global flag for graceful shutdown
running = True

def handle_signal(sig, frame):
    global running
    logging.info(f"Received termination signal ({sig}). Shutting down gracefully...")
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def load_config(config_path="/etc/cv-app/cv_app.conf"):
    config = {
        "CAMERA_INDEX": 0,
        "FRAME_WIDTH": 640,
        "FRAME_HEIGHT": 480,
        "FPS_TARGET": 30,
        "ENABLE_SOBEL_EDGES": "true",
        "ENABLE_SPECTRAL_FFT": "true"
    }
    
    if os.path.exists(config_path):
        logging.info(f"Loading configuration from: {config_path}")
        try:
            with open(config_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        config[k.strip()] = v.strip()
        except Exception as e:
            logging.error(f"Error reading config file {config_path}: {e}")
    else:
        logging.info(f"Config file {config_path} not found. Using default parameters.")
        
    return config

def main():
    logging.info("Starting Embedded CV Application Service...")
    
    config = load_config()
    cam_index = int(config.get("CAMERA_INDEX", 0))
    width = int(config.get("FRAME_WIDTH", 640))
    height = int(config.get("FRAME_HEIGHT", 480))
    
    try:
        import cv2
        import numpy as np
        import scipy.signal
        import scipy.fft
    except ImportError as e:
        logging.critical(f"Required Python module missing: {e}")
        sys.exit(1)
        
    logging.info(f"Loaded OpenCV version: {cv2.__version__}")
    logging.info(f"Loaded SciPy version: {scipy.__version__}")
    logging.info(f"Initializing camera device index /dev/video{cam_index} ({width}x{height})...")
    
    cap = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)
    if not cap.isOpened():
        logging.warning(f"Could not open camera /dev/video{cam_index}. Entering dummy emulation loop...")
        is_emulated = True
    else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        is_emulated = False
        logging.info("Camera device opened successfully.")

    frame_count = 0
    start_time = time.time()

    while running:
        t0 = time.time()
        
        if not is_emulated:
            ret, frame = cap.read()
            if not ret:
                logging.warning("Failed to grab frame. Retrying in 1 second...")
                time.sleep(1.0)
                continue
        else:
            # Generate synthetic test frame (moving pattern)
            frame = np.uint8(np.random.randint(0, 255, (height, width, 3)))
            time.sleep(0.033) # ~30 FPS emulation

        # 1. Spatial Processing (OpenCV Sobel Filter)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # 2. Spectral Signal Processing (SciPy 1D FFT on row mean profile)
        row_profile = np.mean(gray, axis=1)
        fft_spectrum = np.abs(scipy.fft.fft(row_profile))

        frame_count += 1
        elapsed = time.time() - start_time
        
        # Log telemetry metrics every 100 frames (~3 seconds)
        if frame_count % 100 == 0:
            fps = frame_count / elapsed
            dt_ms = (time.time() - t0) * 1000.0
            logging.info(
                f"Telemetry: Processed {frame_count} frames | "
                f"Average FPS: {fps:.2f} | Last Frame Processing Time: {dt_ms:.2f} ms | "
                f"Peak Edge Intensity: {np.max(edge_magnitude):.1f} | Peak Spectral Energy: {np.max(fft_spectrum):.1f}"
            )

    if not is_emulated:
        cap.release()
    logging.info("CV Application Service stopped cleanly.")

if __name__ == "__main__":
    main()
