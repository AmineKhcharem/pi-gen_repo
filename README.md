# Embedded Computer Vision & Signal Processing Raspberry Pi OS Image

Custom headless Raspberry Pi OS image pre-configured with an optimized Computer Vision (OpenCV) and Signal Processing (SciPy/NumPy/OpenBLAS) stack, UVC USB webcam support, multi-camera MIPI CSI Device Tree overlays (IMX462, IMX219, IMX477, IMX708, OV5647), and an automated background application service (`systemd`).

---

## 🚀 Quick Start Guide

### 1. Image Overview
- **Target OS:** Raspberry Pi OS Bullseye (32-bit ARMHF Headless)
- **Base Image:** `pi-gen` stage2 lite build (`cv-image-lite`)
- **Compressed Size:** ~699 MB (`image_2026-08-09-cv-image-lite.zip`)
- **Uncompressed Image:** ~3.5 GB (`2026-08-09-cv-image-lite.img`)
- **Default User Credentials:** User `pi` (or `amin`), password set during image flashing.

### 2. Flashing the Image
You can write the generated image file (`.img` or `.zip`) to a MicroSD card using any standard flasher:
- **Raspberry Pi Imager** (Recommended): Select *Use Custom Image* -> choose `image_2026-08-09-cv-image-lite.zip`.
- **balenaEtcher**: Select zip file -> Select MicroSD drive -> Flash.
- **Command Line (`dd` / `bmaptool`)**:
  ```bash
  sudo bmaptool copy 2026-08-09-cv-image-lite.img /dev/sdX
  ```

---

## ⚙️ Core Technical Features

### 1. Pre-Installed & Optimized Computer Vision Stack
- **OpenCV 4.5.1** (`python3-opencv`, `libopencv-dev`)
- **SciPy 1.6.0** (`python3-scipy`) for signal filtering (`scipy.signal`) & spectral analysis (`scipy.fft`)
- **NumPy 1.19.5** (`python3-numpy`) hardware-accelerated with **OpenBLAS** (`libopenblas-dev`)
- **FFTW3** (`libfftw3-dev`) & **V4L2 Utilities** (`v4l-utils`, `libv4l-dev`)
- *Verification details:* See [`TASK2_NOTES.md`](TASK2_NOTES.md).

### 2. Plug-and-Play UVC USB Webcam Support
- Supports any standard UVC USB webcam out-of-the-box via the kernel `uvcvideo` driver.
- Includes automated diagnostic script [`test_uvc_camera.py`](test_uvc_camera.py).
- *Testing instructions:* See [`UVC_TEST_INSTRUCTIONS.md`](UVC_TEST_INSTRUCTIONS.md) & [`TASK3_NOTES.md`](TASK3_NOTES.md).

### 3. Multi-Camera MIPI CSI Sensor Support
- Pre-baked Device Tree overlays (`.dtbo`), kernel modules (`.ko`), and libcamera ISP tuning calibration files (`.json`).
- Switch active cameras with a single line change in `/boot/config.txt`:
  - `dtoverlay=imx219` (Pi Camera V2)
  - `dtoverlay=imx477` (Pi HQ Camera)
  - `dtoverlay=imx462` (Arducam Low-Light / STARVIS)
  - `dtoverlay=imx708` (Pi Camera Mod 3)
  - `dtoverlay=ov5647` (Pi Camera V1.3)
- *Camera switching guide:* See [`CAMERA_SWITCHING.md`](CAMERA_SWITCHING.md) & [`TASK4_NOTES.md`](TASK4_NOTES.md).

### 4. Background Application Service (`systemd`)
- Pre-installed processing service ([`cv_app.py`](cv_app.py)) managed by `systemd` ([`cv-app.service`](cv-app.service)).
- Auto-starts on boot, logs telemetry to `journalctl`, and recovers automatically if interrupted.
- Service management cheat sheet: See [`TASK5_NOTES.md`](TASK5_NOTES.md).

---

## 📂 Documentation Directory

| Document | Description |
| :--- | :--- |
| **[`CAMERA_SWITCHING.md`](CAMERA_SWITCHING.md)** | Guide for enabling and switching MIPI CSI camera overlays in `config.txt` |
| **[`UVC_TEST_INSTRUCTIONS.md`](UVC_TEST_INSTRUCTIONS.md)** | USB webcam testing & diagnostic instructions |
| **[`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md)** | Hardware verification requirements & technical constraints |
| **[`TASK1_NOTES.md`](TASK1_NOTES.md)** | Task 1: Baseline image setup & mirror fix notes |
| **[`TASK2_NOTES.md`](TASK2_NOTES.md)** | Task 2: CV stack verification & OpenBLAS notes |
| **[`TASK3_NOTES.md`](TASK3_NOTES.md)** | Task 3: UVC driver analysis & test script |
| **[`TASK4_NOTES.md`](TASK4_NOTES.md)** | Task 4: Multi-camera overlay matrix & ISP tuning |
| **[`TASK5_NOTES.md`](TASK5_NOTES.md)** | Task 5: systemd background service management guide |
| **[`TASK6_NOTES.md`](TASK6_NOTES.md)** | Task 6: Final handoff summary & repository audit |
