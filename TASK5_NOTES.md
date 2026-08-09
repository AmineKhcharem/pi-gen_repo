# Task 5 Notes — Custom CV Application as a System Service

## 1. Executive Summary

Task 5 integrates a custom real-time Computer Vision processing application (`cv_app.py`) as an automated background service (`cv-app.service`) managed by `systemd`. 

### Key System Features
- **Automated Boot Start**: Enabled by default via `systemd` (`multi-user.target`) so processing begins immediately upon board power-on without any user login.
- **Configurable Runtime**: Camera source index (`/dev/videoX`) and frame dimensions are configured via `/etc/cv-app/cv_app.conf` without modifying code.
- **Headless Telemetry Logging**: Structured performance logs (FPS, frame count, processing latency, edge intensity, spectral FFT peak) are piped directly to `journalctl`.
- **Automatic Recovery**: Configured with `Restart=always` and `RestartSec=5s` so the service recovers automatically if a camera is temporarily unplugged or interrupted.

---

## 2. Service Management Commands (SSH Cheat Sheet)

Your supervisor or test engineer can interact with the background service over SSH using standard `systemctl` and `journalctl` commands:

### Check Service Status
```bash
sudo systemctl status cv-app
```
*Expected Output:* `Active: active (running) since ...`

### View Live Real-Time Logs
```bash
sudo journalctl -u cv-app -f -o cat
```
*Sample Log Stream:*
```text
2026-08-10 00:05:12 [INFO] [cv-app] Starting Embedded CV Application Service...
2026-08-10 00:05:12 [INFO] [cv-app] Loaded OpenCV version: 4.5.1
2026-08-10 00:05:12 [INFO] [cv-app] Loaded SciPy version: 1.6.0
2026-08-10 00:05:12 [INFO] [cv-app] Initializing camera device index /dev/video0 (640x480)...
2026-08-10 00:05:15 [INFO] [cv-app] Telemetry: Processed 100 frames | Average FPS: 29.84 | Last Frame Processing Time: 33.12 ms | Peak Edge Intensity: 184.2 | Peak Spectral Energy: 1420.5
2026-08-10 00:05:18 [INFO] [cv-app] Telemetry: Processed 200 frames | Average FPS: 29.91 | Last Frame Processing Time: 32.95 ms | Peak Edge Intensity: 191.0 | Peak Spectral Energy: 1488.2
```

### Restart Service (e.g., after changing camera in `config.txt`)
```bash
sudo systemctl restart cv-app
```

### Stop or Disable Service
```bash
# Stop running instance:
sudo systemctl stop cv-app

# Disable auto-start on boot:
sudo systemctl disable cv-app
```

---

## 3. Configuration Management

To change the camera input device index or resolution:

1. Edit `/etc/cv-app/cv_app.conf`:
   ```bash
   sudo nano /etc/cv-app/cv_app.conf
   ```
2. Modify key parameters (e.g. `CAMERA_INDEX=1` or `FRAME_WIDTH=1280`):
   ```ini
   CAMERA_INDEX=0
   FRAME_WIDTH=640
   FRAME_HEIGHT=480
   ```
3. Restart the service:
   ```bash
   sudo systemctl restart cv-app
   ```
