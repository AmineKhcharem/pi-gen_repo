# Known Limitations & Hardware Verification Checklist

This document details known technical limitations, assumptions made during emulated image generation (`qemu-arm-static`), and open items requiring physical hardware testing.

---

## 1. Hardware Verification Requirements (Physical Raspberry Pi)

Because the image was generated and verified inside a headless `pi-gen` QEMU emulation environment, physical hardware verification is required for the following items:

1. **UVC USB Webcam Live Video Capture**:
   - *Status:* `uvcvideo.ko` kernel module verified in image rootfs. `v4l2-ctl` and OpenCV bindings verified.
   - *Hardware Check Needed:* Verify actual frame grab rates and USB power stability on physical Raspberry Pi 4B hardware with a physical USB webcam attached.

2. **MIPI CSI Camera Sensor Overlays**:
   - *Status:* Device Tree overlays (`imx219.dtbo`, `imx477.dtbo`, `imx708.dtbo`, `imx290.dtbo`, `ov5647.dtbo`) and kernel drivers present in `/boot/overlays/` and `/lib/modules/`.
   - *Hardware Check Needed:* Confirm I2C communication and `libcamera-still` frame capture after activating specific `dtoverlay=` lines in `/boot/config.txt`.

3. **OpenBLAS CPU Performance Benchmark**:
   - *Status:* `python3-numpy` verified linked against OpenBLAS (`libopenblas.so.0`).
   - *Hardware Check Needed:* Run real-time matrix multiplication and FFT benchmarks on physical ARM Cortex-A72 cores to measure CPU thermal throttling and sustained FPS performance.

---

## 2. Known Software & Build Limitations

1. **Bullseye vs. Buster Variant Target**:
   - The primary build generated is **Raspberry Pi OS Bullseye (32-bit ARMHF)**. Bullseye uses `libcamera` as its primary camera stack.
   - Legacy `raspistill` / `raspivid` tools are deprecated in Bullseye; applications should use OpenCV (`cv2.VideoCapture`), V4L2 API, or `libcamera`.

2. **Source Compilation vs. Distro Packages**:
   - Python packages (`opencv-python`, `scipy`) were installed via `apt` distro packages rather than compiled from source to prevent QEMU emulation memory exhaustion (OOM crashes) during the image build.
   - Distro OpenCV (`4.5.1`) provides standard NEON optimizations; however, compiling OpenCV from source with custom flags (`-DENABLE_NEON=ON -DWITH_OPENMP=ON`) could yield additional 5-10% FPS gains if needed in future iterations.

3. **No Display / Headless Operation**:
   - The image is strictly headless (`cv-image-lite`). Desktop GUI components (`X11`, `LXDE`, `Wayland`) are omitted to minimize image footprint (~699 MB compressed).
   - Displaying video streams visually via `cv2.imshow()` will fail without an X server. Frame output must be processed headlessly or saved to disk (`cv2.imwrite()`).
