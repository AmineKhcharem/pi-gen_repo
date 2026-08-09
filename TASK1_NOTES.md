# Task 1 Notes

## Status
- [x] Buster variant built successfully
- [x] Buster variant verified (SSH confirmed via systemd symlink; image mounted and inspected)
- [x] Bullseye variant built successfully
- [x] Bullseye variant verified

## Build Environment
- Host OS: Ubuntu (VirtualBox)
- Tool: Docker & pi-gen

## Buster Variant
- **Branch/Tag used:** `buster` branch
- **Build status:** ✅ SUCCESS — image in `deploy/`
- **Build time:** ~11 minutes (build started ~17:52, completed ~18:03 on 2026-08-03)
- **Output image:** `deploy/cv-image-buster.zip` (or `image_2026-08-03-cv-image-lite.zip`)
- **Key fixes required to build Buster in 2026:**
  1. Must use `buster` branch (not `master`)
  2. Docker `Dockerfile` patched to use `archive.debian.org` (EOL repo)
  3. `stage0` scripts patched to use `legacy.raspbian.org` (Raspbian-specific EOL mirror)
  4. `DEBOOTSTRAP_OPTS="--no-check-gpg"` added to `config` (expired archive GPG keys)
  5. `sudo modprobe nbd` must be run on host before every build (ZSTD module incompatibility)
  6. `--no-check-gpg` injected directly into `stage0/prerun.sh` as pi-gen `buster` branch ignores the config variable
- **Errors/Resolutions:** 
  - `qemu-arm not found` -> Attempted to install `qemu-user-static`, but it's a virtual package on newer Ubuntu versions. Resolved by installing `qemu-user-binfmt` and `binfmt-support` on host.
  - `WARNING: RELEASE does not match...` and `Failed getting release file` -> Caused by using the `master` branch (which is configured for Bookworm) to build Buster. Resolved by cleaning the `work/` directory and checking out the `buster` branch.
  - `Container pigen_work already exists` -> Cleaned up the leftover Docker container from the failed build using `docker rm -v pigen_work`.
  - `404 Not Found` for `buster Release` in Dockerfile -> Debian Buster reached End of Life (EOL) so its repos moved to `archive.debian.org`. Fixed by patching the `Dockerfile` to point to the archive.
  - `Failed getting release file` from Raspbian debootstrap -> Raspbian Buster is EOL and moved to `legacy.raspbian.org` (not archive!). Fixed by pointing `stage0` to the legacy URL and adding `DEBOOTSTRAP_OPTS="--no-check-gpg"` to bypass expired GPG keys.
  - `modprobe: ERROR: could not insert 'nbd': Exec format error` -> Modern Ubuntu hosts compress kernel modules with ZSTD (`nbd.ko.zst`), but the old Debian Buster build container doesn't understand ZSTD. Resolved by manually loading the module on the host first (`sudo modprobe nbd`).

## Bullseye Variant
- **Branch/Tag used:** `bullseye` branch
- **Build status:** ✅ SUCCESS — image in `deploy/`
- **Output image:** `deploy/cv-image-bullseye.zip` (or `image_<date>-cv-image-lite.zip`)
- **Errors/Resolutions:** 
  - `qemu-arm-static not found` -> Installed `qemu-user-binfmt-hwe` on Ubuntu host.
  - `Invalid filesystem option set: ^64bit,^huge_file,^orphan_file` -> `mke2fs` 1.46.2 in Bullseye does not recognize `^orphan_file`. Fixed by removing `,^orphan_file` from `export-image/prerun.sh` and re-running with `CONTINUE=1`.
