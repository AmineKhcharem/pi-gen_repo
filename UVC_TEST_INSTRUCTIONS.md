# UVC (USB Webcam) Hardware Testing Instructions

This document provides step-by-step instructions for testing standard UVC (USB Video Class) webcams on the custom headless Raspberry Pi OS image generated via `pi-gen`.

---

## 1. Requirements

- Raspberry Pi board (Pi 4B, Pi 3B+, or Pi Zero 2W) booted with the `cv-image-lite` image.
- Any standard USB webcam compliant with the **UVC (USB Video Class)** specification (e.g., Logitech C270, C920, generic USB camera module).
- Network access (SSH session into the Pi).

---

## 2. Step 1: Verify Hardware Detection

1. Plug your UVC USB webcam into any USB 2.0 or USB 3.0 port on the Raspberry Pi.
2. Check kernel log messages to confirm the camera USB interface was enumerated:
   ```bash
   dmesg | grep uvcvideo
   ```
   *Expected Output Example:*
   ```text
   [   12.345678] uvcvideo: Found UVC 1.00 device HD Webcam (046d:0825)
   [   12.350123] input: HD Webcam as /devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1:1.0/input/input0
   [   12.355987] usbcore: registered new interface driver uvcvideo
   ```

3. Confirm that video device nodes are created under `/dev/`:
   ```bash
   ls -l /dev/video*
   ```
   *Note:* A single UVC camera typically creates two nodes: `/dev/video0` (video capture stream) and `/dev/video1` (metadata/control stream).

---

## 3. Step 2: Query Camera Formats & Resolutions (`v4l-utils`)

Run `v4l2-ctl` to query supported pixel formats (MJPEG, YUYV), frame dimensions, and frame rates:

```bash
v4l2-ctl --list-devices
```

To view all supported resolutions for `/dev/video0`:

```bash
v4l2-ctl -d /dev/video0 --list-formats-ext
```

---

## 4. Step 3: Run the Automated Python Capture Test

1. Copy or download `test_uvc_camera.py` to the Raspberry Pi home directory (`/home/pi/` or `/home/amin/`).
2. Execute the verification script:
   ```bash
   python3 test_uvc_camera.py --device-index 0 --output uvc_test_frame.jpg
   ```

3. **Expected Terminal Output:**
   ```text
   ==================================================
    UVC (USB Webcam) Support Verification Utility
   ==================================================
   ==================================================
    1. Scanning V4L2 Video Devices (/dev/video*)
   ==================================================
   Detected video device nodes: ['/dev/video0', '/dev/video1']

   ==================================================
    2. Testing Frame Capture via OpenCV (index 0)
   ==================================================
   OpenCV Version: 4.5.1
   Opened Device Index 0: 640x480 @ 30.0 FPS
   Capturing warm-up frames...
   ✅ Successfully captured frame! Frame shape: (480, 640, 3), dtype: uint8
   ✅ Saved screenshot to: uvc_test_frame.jpg (45.2 KB)

   ==================================================
    🎉 RESULT: UVC CAMERA TEST PASSED!
   ==================================================
   ```

4. Verify the generated image file `uvc_test_frame.jpg` on your local host (using `scp` or `sftp`):
   ```bash
   scp pi@<pi-ip-address>:~/uvc_test_frame.jpg .
   ```

---

## 5. Troubleshooting Common Issues

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `No /dev/video* devices found` | USB power issue or faulty USB cable | Try a powered USB hub or different USB port; check `lsusb` to confirm vendor/product ID. |
| `Failed to open video device at index 0` | Permission issue or camera in use | Ensure user is in `video` group (`sudo usermod -aG video $USER`) or test with `sudo`. |
| `Failed to read frame` | Device node `/dev/video0` is control node | Try `--device-index 1` or test with `v4l2-ctl --list-devices` to identify the correct capture node. |
