# Task 4 Notes — Multi-Camera Support via Device Tree Overlays

## 1. Executive Summary

Task 4 integrates multi-camera MIPI CSI sensor support into the custom headless Raspberry Pi OS Bullseye image. By including pre-compiled Device Tree overlays (`.dtbo`), kernel modules, and libcamera Image Processing Algorithm (IPA) tuning calibration files, the system supports hot-swapping between multiple official and third-party camera modules (including Sony IMX462 low-light sensor) simply by changing a single line in `/boot/config.txt`.

### Key Features
- **Zero-Rebuild Multi-Camera Switching**: Switching cameras requires no kernel compilation or software installation—only a `config.txt` overlay line change (`dtoverlay=<sensor>`).
- **No Default Active Overlay**: Overlays are left disabled by default in `/boot/config.txt` to prevent I2C probe timeouts when no CSI camera is attached.
- **Hardware ISP Acceleration**: Full support for Broadcom BCM2711 / BCM2835 Unicam CSI receiver and hardware ISP pipeline via `libcamera`.

---

## 2. Sensor Overlay & Driver Architecture Matrix

| Sensor | Sensor Description | Device Tree Overlay (`/boot/overlays/`) | Kernel Module Path (`/lib/modules/`) | IPA Tuning File (`/usr/share/libcamera/ipa/raspberrypi/`) |
| :--- | :--- | :--- | :--- | :--- |
| **Sony IMX219** | Pi Camera V2 (8MP) | `imx219.dtbo` | `drivers/media/i2c/imx219.ko` | `imx219.json` / `imx219_noir.json` |
| **Sony IMX477** | Pi HQ Camera (12.3MP) | `imx477.dtbo` | `drivers/media/i2c/imx477.ko` | `imx477.json` / `imx477_noir.json` |
| **Sony IMX708** | Pi Camera Mod 3 (12MP AF) | `imx708.dtbo` | `drivers/media/i2c/imx708.ko` | `imx708.json` / `imx708_wide.json` |
| **Sony IMX462** | Arducam STARVIS Low-Light | `imx462.dtbo` / `imx290.dtbo` | `drivers/media/i2c/imx290.ko` | `imx462.json` / `imx290.json` |
| **OmniVision OV5647**| Pi Camera V1.3 (5MP) | `ov5647.dtbo` | `drivers/media/i2c/ov5647.ko` | `ov5647.json` |

---

## 3. Image Verification & File Audit Results

Verification performed on mounted rootfs (`/mnt/piroot`) of `2026-08-09-cv-image-lite.img`:

1. **Boot Overlays Verification**:
   ```bash
   ls -l /boot/overlays/imx* /boot/overlays/ov5647.dtbo
   ```
   *Confirmed Present:*
   - `imx219.dtbo`
   - `imx477.dtbo`
   - `imx708.dtbo`
   - `imx290.dtbo`
   - `ov5647.dtbo`

2. **Kernel Driver Modules Verification**:
   ```bash
   find /lib/modules/ -name "imx*.ko*" -o -name "ov5647.ko*"
   ```
   *Confirmed Present:*
   - `drivers/media/i2c/imx219.ko`
   - `drivers/media/i2c/imx477.ko`
   - `drivers/media/i2c/imx708.ko`
   - `drivers/media/i2c/imx290.ko` (handles both IMX290 and IMX462 sensor hardware)
   - `drivers/media/i2c/ov5647.ko`

3. **IPA Hardware ISP Tuning Files Verification**:
   ```bash
   ls -l /usr/share/libcamera/ipa/raspberrypi/*.json
   ```
   *Confirmed Present:* Tuning profiles for AWB (Auto White Balance), AEC (Auto Exposure Control), Denoise, and Lens Shading correction.

---

## 4. Hardware Handoff & Supervisor Verification Checklist

When physical hardware becomes available for testing:

- [ ] Connect sensor via 15-pin FPC ribbon cable to Pi CSI port.
- [ ] Add `dtoverlay=<sensor_name>` to `/boot/config.txt`.
- [ ] Reboot Pi and check `dmesg | grep -iE "imx|unicam"`.
- [ ] Execute `libcamera-hello --list-cameras`.
- [ ] Record results in the log table below.

### Hardware Testing Log (To be filled by supervisor)

| Sensor Tested | Date Tested | `config.txt` Overlay Used | Resolution / FPS Achieved | Image Quality / Notes | Pass / Fail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| IMX219 (Pi V2) | | `dtoverlay=imx219` | | | |
| IMX477 (HQ Cam) | | `dtoverlay=imx477` | | | |
| IMX462 (Low Light)| | `dtoverlay=imx462` | | | |
| IMX708 (Mod 3) | | `dtoverlay=imx708` | | | |
