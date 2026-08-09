# MIPI CSI Camera Switching Guide

This document explains how to activate and switch between different **MIPI CSI camera sensors** on your built Raspberry Pi OS image. 

Because MIPI CSI sensors require sensor-specific kernel drivers, Device Tree overlays, and ISP tuning files, the camera overlay is **not enabled by default**. Switching cameras requires editing a single line in `/boot/config.txt`.

---

## 1. Supported Sensors & Quick Reference

| Camera Model | Sensor | Resolution | DT Overlay Line (`/boot/config.txt`) | Driver / Kernel Module | Tuning File Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raspberry Pi Camera V1.3** | OmniVision OV5647 | 5 MP | `dtoverlay=ov5647` | `ov5647.ko` | `/usr/share/libcamera/ipa/raspberrypi/ov5647.json` |
| **Raspberry Pi Camera V2** | Sony IMX219 | 8 MP | `dtoverlay=imx219` | `imx219.ko` | `/usr/share/libcamera/ipa/raspberrypi/imx219.json` |
| **Raspberry Pi HQ Camera** | Sony IMX477 | 12.3 MP | `dtoverlay=imx477` | `imx477.ko` | `/usr/share/libcamera/ipa/raspberrypi/imx477.json` |
| **Raspberry Pi Camera Mod 3**| Sony IMX708 | 12 MP (Autofocus)| `dtoverlay=imx708` | `imx708.ko` | `/usr/share/libcamera/ipa/raspberrypi/imx708.json` |
| **Arducam Low-Light / STARVIS** | Sony IMX462 | 2 MP (NIR/HDR) | `dtoverlay=imx462` *(or `imx290`)*| `imx290.ko` / `imx462.ko`| `/usr/share/libcamera/ipa/raspberrypi/imx462.json` |
| **Sony IMX290 / IMX327** | Sony IMX290 | 2 MP | `dtoverlay=imx290` | `imx290.ko` | `/usr/share/libcamera/ipa/raspberrypi/imx290.json` |

---

## 2. How to Activate a Camera

### Step 1: Connect the Hardware
1. Power off the Raspberry Pi completely.
2. Insert the 15-pin (or 22-pin on Pi Zero 2W) FPC ribbon cable into the **CAM / CSI port**.
   - *Metal contacts must face toward the HDMI / board center on Pi 4B.*
3. Ensure the ribbon cable is securely latched in place.

### Step 2: Edit `/boot/config.txt`
1. Boot the Pi or edit the SD card boot partition on your host machine.
2. Open `/boot/config.txt` with root privileges:
   ```bash
   sudo nano /boot/config.txt
   ```
3. Locate the `[all]` section at the bottom of the file.
4. Add **one** of the following lines matching your physical sensor:

   ```ini
   # --- Camera Hardware Activation ---
   # Uncomment ONLY ONE line corresponding to your attached camera:

   # Option A: Raspberry Pi Camera V2 (Sony IMX219)
   dtoverlay=imx219

   # Option B: Raspberry Pi HQ Camera (Sony IMX477)
   # dtoverlay=imx477

   # Option C: Arducam / Sony Ultra Low-Light (Sony IMX462)
   # dtoverlay=imx462

   # Option D: Raspberry Pi Camera Module 3 (Sony IMX708)
   # dtoverlay=imx708

   # Option E: Raspberry Pi Camera V1.3 (OmniVision OV5647)
   # dtoverlay=ov5647
   ```

5. Save the file (`Ctrl+O`, `Enter`) and exit (`Ctrl+X`).
6. Reboot the Raspberry Pi:
   ```bash
   sudo reboot
   ```

---

## 3. Verification & Testing

### 3.1 Kernel Message Check
After rebooting, check that the kernel successfully bound the sensor driver and registered the CSI receiver:

```bash
dmesg | grep -iE "imx219|imx477|imx462|imx708|ov5647|unicam"
```

*Expected Output Example (for IMX219):*
```text
[    3.123456] imx219 10-0010: Consider updating driver imx219 to use leds-gpio
[    3.125000] imx219 10-0010: Detected IMX219 sensor
[    3.130000] unicam 3f801000.csi: Sensor /soc/i2c0mux/i2c@1/imx219@10 registered
```

### 3.2 V4L2 Device Verification
List registered video devices:
```bash
v4l2-ctl --list-devices
```

You should see `unicam` (Broadcom BCM2835 / BCM2711 Unicam CSI receiver) listed as `/dev/video0`.

### 3.3 Capture Verification (`libcamera-hello` or `v4l2-ctl`)

On Bullseye, capture a test JPEG image using `libcamera-still`:

```bash
libcamera-still -o test_csi_frame.jpg --width 1920 --height 1080
```

Or using `v4l2-ctl`:

```bash
v4l2-ctl --set-fmt-video=width=1920,height=1080,pixelformat=RGB3 --stream-mmap --stream-count=1 --stream-to=test_csi.raw
```

---

## 4. Switching to a Different Sensor

To switch to a different physical camera (e.g., from IMX219 to IMX462):
1. Shut down the Pi: `sudo poweroff`
2. Swap the physical camera ribbon cable.
3. Edit `/boot/config.txt`: comment out `dtoverlay=imx219` and uncomment `dtoverlay=imx462`.
4. Reboot: `sudo reboot`.
