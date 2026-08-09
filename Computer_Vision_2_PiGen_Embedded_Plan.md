# Computer Vision 2 — Custom Raspberry Pi OS Image (pi-gen)

This is the follow-up program to your first Computer Vision internship track. Now that you've worked with the CV stack on a normal desktop/laptop environment, this track moves into embedded systems: building a custom, headless Raspberry Pi OS image using `pi-gen` (the official tool Raspberry Pi Foundation uses to build Raspberry Pi OS itself). The image will include the camera interfacing stack, the processing stack, and the computer vision stack (OpenCV, Python) from your first track.

**Prerequisites:** completion of the Computer Vision 1 tasks, comfort with Linux command line and basic shell scripting, comfort with `apt`/Debian package management

**Important — read this before you start:**
- **You will not touch or need any physical hardware at any point in this track.** Everything is built and validated on your Linux PC (the "host"). Once you produce a finished image, you'll share the image file with your supervisor, who has the physical Raspberry Pi boards and camera modules and will flash and test them. Your job is to make sure the image is built correctly, all the right drivers/packages/configuration are in place, and everything is clearly documented for the handoff.
- **You will build two image variants**: one based on Debian **Buster**, one based on Debian **Bullseye**. This matters because package versions (particularly OpenCV, Python, and libcamera-related tooling) differ meaningfully between these two bases, and camera vendor support/instructions sometimes differ between them too. Building both gives your supervisor flexibility to pick whichever works best with the actual hardware once tested.
- **The image must be headless.** No desktop environment, no X11/Wayland, no display manager — just the OS, SSH access, and your application stack (camera capture, processing, CV). This is a deliberate design choice, not a shortcut: less RAM/CPU overhead competing with the actual workload, faster boot, smaller image size, faster to transfer/reflash, and a smaller attack surface.
- **The image must support multiple cameras via switchable overlays.** Rather than hardcoding one sensor, the goal is to bake in overlay support for several common camera sensors (official Raspberry Pi camera sensors, plus third-party ones like IMX462) so the active camera can be changed with a single line in `config.txt` — no rebuild required.

---

## Why pi-gen (and not Yocto)

You may come across mentions of Yocto for embedded Linux image building — it's a legitimate and widely used tool, but it's a much heavier, general-purpose embedded Linux build system meant for arbitrary custom hardware (not just Raspberry Pi), with a steep learning curve and a lot of low-level driver/recipe work. `pi-gen` is Raspberry Pi Foundation's own tool, purpose-built to produce Raspberry Pi OS, is Debian-based, has excellent documentation and community support, and camera vendors (like Arducam) generally publish install scripts and overlays that target Raspberry Pi OS directly. For this track, pi-gen is the right tool for the job.

---

## Environment Setup (Day 0)

### 1. Host machine requirements
- A Linux machine (Ubuntu 22.04 or Debian-based recommended — pi-gen is designed around Debian tooling)
- At least 30–50GB free disk space
- Docker installed (pi-gen's recommended build method uses Docker to avoid polluting your host system with build dependencies)

### 2. Install Docker (if not already installed)
```bash
sudo apt update
sudo apt install -y docker.io
sudo usermod -aG docker $USER
# log out and back in for the group change to take effect
```

### 3. Clone pi-gen
```bash
git clone https://github.com/RPi-Distro/pi-gen.git
cd pi-gen
```

### 4. Understand the pi-gen structure
Read through the `stage0` through `stage5` directories before writing anything. Key concept: each "stage" builds on the previous one and adds more. For a headless image, you generally want to stop after `stage2` (base system + SSH), and explicitly **skip** `stage3` onward (which adds desktop-related packages) by creating a `SKIP` file in those stage directories, or by only building up to the stage you need via the `STAGE_LIST` config variable.

---

## Task 1 — Build a Baseline Headless Image (Both Variants)

**Goal:** Get a minimal, headless, SSH-accessible image building successfully for both Buster and Bullseye, before adding any camera or CV complexity.

### Steps
1. Create a `config` file at the root of `pi-gen` (copy from `config.example` as a starting point) with:
   - `IMG_NAME='cv-image'`
   - `ENABLE_SSH=1`
   - `STAGE_LIST="stage0 stage1 stage2"` (this stops before any desktop stage)
2. Build the Buster variant first. Check pi-gen's branches/tags for Buster-era support, and use Docker to build:
   ```bash
   ./build-docker.sh
   ```
3. Once the Buster build succeeds, repeat the process for Bullseye (this typically means checking out the appropriate pi-gen branch/tag that targets Bullseye, since pi-gen's stage contents are version-specific)
4. Confirm both resulting images boot in general terms by inspecting the build logs and image contents — you do not need real hardware for this; you can also mount the resulting `.img` file's partitions locally (via `losetup`/`kpartx`) to inspect the filesystem contents directly, which is a useful debugging technique you'll use throughout this track
5. Confirm SSH is enabled and would be reachable (correct service enabled, correct default config) by inspecting the image's filesystem

### Deliverable
- Two successfully built images: `cv-image-buster.img` and `cv-image-bullseye.img` (or equivalent naming)
- A `TASK1_NOTES.md` documenting: which pi-gen branch/tag you used for each variant, build time, and any errors you hit and how you resolved them

---

## Task 2 — Add the Processing, Computer Vision & Signal Processing Stack

**Goal:** Extend both baseline images with the C/C++ and Python libraries needed for computer vision and real-time signal processing, with performance as an explicit priority — not just "does it import," but "is it using the fast backend."

### Libraries to include

**C/C++ layer:**
- `libopencv-dev` — OpenCV core, imgproc, video, imgcodecs, videoio C++ headers and libraries
- `libopenblas-dev` — BLAS/LAPACK backend for linear algebra. Use this instead of `libatlas-base-dev`: OpenBLAS has ARM NEON-optimized kernels and is generally faster on Raspberry Pi hardware, and both OpenCV and NumPy will use it for matrix operations
- `libfftw3-dev` — FFT library, needed for fast frequency-domain signal processing (spectral analysis, frequency-domain filtering). Significantly faster than a naive DFT, especially for repeated real-time transforms on a fixed buffer size
- `libv4l-dev` — lower-level V4L2 camera capture headers, in case the application benefits from capturing frames directly via V4L2 instead of through OpenCV's higher-level camera abstraction (less overhead)
- `libjpeg-dev`, `libpng-dev` — image codec support (an OpenCV dependency, also needed if the application saves frames to disk)
- `libatomic1` — commonly needed at runtime for OpenCV on ARM

**Python layer:**
- `python3-numpy` — after installing, verify it's actually linked against OpenBLAS (`python3 -c "import numpy; numpy.show_config()"`), not a slower reference BLAS implementation — the distro package doesn't always default to the fast one
- `python3-opencv` — Python bindings. Check whether the distro-packaged version was built with NEON enabled. If not (common on Debian/Raspbian packages), building OpenCV from source with `-DENABLE_NEON=ON -DWITH_OPENMP=ON` is worth the extra build time, since it's a real, measurable speed difference on Pi hardware — flag this as a decision point rather than doing it automatically, since it adds significant build complexity and time
- `scipy` — needed for `scipy.signal` (bandpass filtering, as used in your first internship track) and `scipy.fft`
- `pyfftw` — Python bindings to FFTW directly. Include this specifically because `numpy.fft`/`scipy.fft` are noticeably slower than FFTW for repeated transforms of the same buffer size, which is exactly the real-time streaming FFT use case here
- `numba` (optional, worth including) — JIT-compiles hot Python loops to near-C speed, useful for any custom pixel-level loop that can't be cleanly vectorized with NumPy
- `v4l-utils` — camera debugging tool (already mentioned in Task 3, listing here too since it belongs in the same stage)

### Steps
1. Create a custom stage (e.g., `stage-cv/`) following pi-gen's stage folder conventions (a `00-packages`, `01-run.sh`, etc. structure — study an existing simple stage like `stage2` as a template)
2. Install the C/C++ libraries listed above via the stage's package list
3. Install the Python libraries listed above, either via `apt` (`python3-numpy`, `python3-opencv`, `python3-scipy`) or `pip` (`pyfftw`, `numba` — check if apt packages exist first for your target Debian version, prefer apt when available for better integration with the rest of the image)
4. Be careful that none of these packages pull in graphical/desktop dependencies transitively — check with `apt-cache depends` before installing, and verify after building that no X11/desktop packages ended up in the image unexpectedly
5. Rebuild both variants (Buster and Bullseye) with this new stage included
6. Validate everything is correctly linked by inspecting the built image's filesystem (mount the image, chroot into it if needed) and confirming:
   - `python3 -c "import cv2; print(cv2.__version__)"`
   - `python3 -c "import numpy; numpy.show_config()"` (confirm OpenBLAS is the backend, not reference BLAS)
   - `python3 -c "import pyfftw"`
   - `python3 -c "import scipy.signal"`
7. Document any version differences you find between what's available for Buster vs Bullseye (OpenCV version, Python version, whether NEON-enabled OpenCV builds are feasible/necessary for each) — this is genuinely useful information for your supervisor when deciding which variant to actually use going forward
8. If you do decide to build OpenCV from source for NEON support, document the exact build flags used and the resulting build time, since this will need to be repeated if the image is rebuilt later

### Deliverable
- Both images rebuilt with the full C/Python CV + signal processing stack included, still fully headless
- `TASK2_NOTES.md` documenting: package versions available in each variant, confirmation that NumPy is using OpenBLAS, whether OpenCV NEON builds were attempted/needed, and any issues you had to work around

---

## Task 3 — UVC (USB Webcam) Support

**Goal:** Make sure the image supports standard UVC (USB) webcams with zero per-camera driver work, and prepare everything your supervisor needs to validate this on real hardware later.

### Steps
1. Confirm the `uvcvideo` kernel module is present and set to load automatically in the image (inspect the kernel config / modules list in the built image — no real camera needed for this, it's about confirming the driver is there)
2. Make sure `v4l-utils` (installed in Task 2) is available for camera debugging on the actual device later
3. Prepare a simple test script (e.g., `test_uvc_camera.py`) using OpenCV or `v4l2-ctl` that your supervisor can run once a UVC webcam is plugged into the real board — you're writing this for someone else to run, not running it yourself
4. Write a clear `UVC_TEST_INSTRUCTIONS.md`: exactly what to plug in, what commands to run, and what output indicates success
5. Write up, in your own words, why UVC doesn't need a sensor-specific driver while MIPI CSI sensors (Task 4) do — this is the conceptual bridge into the next task

### Deliverable
- Confirmation (from image inspection) that `uvcvideo` is present and set to auto-load in both variants
- `test_uvc_camera.py` and `UVC_TEST_INSTRUCTIONS.md`, ready to hand off
- A short written explanation of UVC vs MIPI CSI driver architecture in `TASK3_NOTES.md`

---

## Task 4 — Multi-Camera Support via Device Tree Overlays

**Goal:** Bake in overlay support for multiple MIPI CSI camera sensors — official Raspberry Pi sensors plus IMX462 — so the active camera can be switched with a single `config.txt` line change, no rebuild required.

### Steps
1. Confirm which official sensors (imx219, imx477, imx708) already have overlays included by default in Raspberry Pi OS's `/boot/overlays/` — these typically just work already, confirm they're present in your built image
2. For IMX462 (and optionally other third-party sensors like ov5647, imx290): find the vendor's (e.g., Arducam's) published overlay (`.dtbo`) file and any associated kernel module or driver package they distribute for Raspberry Pi OS
3. Add a step in your custom stage that copies these additional overlay files into `/boot/overlays/` in the built image, and installs any additional driver packages/kernel modules the vendor requires
4. Add the sensor's libcamera tuning file(s) (color matrix, AWB/denoise calibration) into the correct location in the image (usually under `/usr/share/libcamera/ipa/` or similar — check the vendor's documentation for exact path) — without this, expect washed-out colors or poor auto-exposure even if the sensor technically produces frames
5. Do **not** enable any camera overlay by default in `config.txt` — leave it commented out or absent, since the correct choice depends on which physical camera is actually attached
6. Write a `CAMERA_SWITCHING.md` guide: for each supported sensor, the exact line to add/uncomment in `config.txt` (e.g., `dtoverlay=imx462`), any other required settings, and what output to expect once switched on and tested
7. Rebuild both variants (Buster and Bullseye) with this camera stage included, and confirm (via image/filesystem inspection) that all the overlay files, tuning files, and driver packages are correctly present

### Deliverable
- A custom stage containing overlay files, tuning files, and any required driver packages for IMX462 plus at least one official sensor
- `CAMERA_SWITCHING.md` — the single source of truth for how to activate each supported camera
- `TASK4_NOTES.md` documenting what's included, and space for your supervisor to log real-hardware results once they test

---

## Task 5 — Custom CV Application as a System Service

**Goal:** Package your own CV application (from your first internship track) into the image as a properly managed background service.

### Steps
1. In your custom stage, install your CV application code (Python script or package) into the image filesystem
2. Add a `systemd` unit file so the application starts automatically on boot, and enable it by default in the image build
3. Make the application's camera source configurable (e.g., via a simple config file or environment variable) rather than hardcoded, since which camera is attached will vary
4. Set up logging so the application's output goes to `journalctl` (standard systemd logging) — this is important since there's no display attached, ever, to debug visually
5. Document how your supervisor can check the service status and logs over SSH once the board is running: `systemctl status your-app`, `journalctl -u your-app -f`

### Deliverable
- Both images rebuilt with your CV application installed and enabled as a systemd service
- `TASK5_NOTES.md` with the SSH commands your supervisor will need to check status/logs on the real device

---

## Task 6 — Documentation, Versioning, and Handoff

**Goal:** Package everything clearly so your supervisor can flash, configure, and test both images without needing to ask you what anything means.

### Steps
1. Write a top-level `README.md` for the whole project covering:
   - What the image is, and the two variants (Buster/Bullseye) and why they exist
   - How to flash the image (Raspberry Pi Imager, `balenaEtcher`, or `dd`/`bmaptool`)
   - How to enable SSH and find the board's IP (or confirm it's already enabled by default)
   - How to select the active camera (pointing to `CAMERA_SWITCHING.md`)
   - How to check that your CV application/service is running (pointing to `TASK5_NOTES.md`)
2. Set up a clear file-sharing method for the built `.img` files themselves — these are large binary files and should **not** go into the git repository. Use a shared Drive/Dropbox link, and reference that link from the `README.md`
3. Write a short `KNOWN_LIMITATIONS.md` — anything you weren't able to verify without hardware, anything that might need adjustment once tested for real, and open questions for your supervisor
4. Do a final review pass: make sure the git repo contains all your *source* (stages, scripts, overlays, tuning files, configs, docs) and that it's possible to fully reproduce both images from the repo alone

### Deliverable
- A clear, complete `README.md` and supporting docs, ready for handoff
- Both final images uploaded and linked
- `KNOWN_LIMITATIONS.md` listing anything that needs real-hardware confirmation

---

## GitHub Repository Structure

```
cv-embedded-pigen/
├── README.md
├── pi-gen/                      # your fork/clone, or just your custom stage if you keep pi-gen separate
│   └── stage-cv/                # your custom stage: packages, camera overlays, tuning files, app, systemd unit
├── test_uvc_camera.py
├── UVC_TEST_INSTRUCTIONS.md
├── CAMERA_SWITCHING.md
├── KNOWN_LIMITATIONS.md
├── TASK1_NOTES.md
├── TASK2_NOTES.md
├── TASK3_NOTES.md
├── TASK4_NOTES.md
├── TASK5_NOTES.md
├── TASK6_NOTES.md
└── assistant_log.md
```

Commit and push after each task, same as your first track. Add your supervisor as a collaborator once the repo is set up. The built `.img` files themselves go in a shared Drive/Dropbox link referenced from the README, not in git.

---

## A Note on Using Your Coding Assistant Here

Embedded image building has a learning curve, and errors can be unfamiliar at first (chroot issues, apt dependency resolution, systemd unit syntax). Use your AI coding assistant (Claude Code, or similar) heavily for:
- Explaining pi-gen's stage structure and any unfamiliar build errors
- Reviewing your stage scripts and systemd unit files before you spend a long time debugging a small mistake
- Helping you find and understand vendor (Arducam, etc.) documentation for driver/overlay files

As before: use it to accelerate your understanding, not to skip understanding. You should be able to explain what every stage script, overlay, and config change actually does.

---

Good luck — this track asks you to build something real without ever seeing it run, which is a genuinely useful skill: writing clear, well-documented, testable deliverables for someone else to validate.
