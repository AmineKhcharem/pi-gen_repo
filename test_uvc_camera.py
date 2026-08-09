#!/usr/bin/env python3
"""
UVC (USB Webcam) Verification & Diagnostics Script
Target Platform: Raspberry Pi OS (Bullseye / Buster)
Author: Internship Track 2 - Computer Vision & Embedded Linux

Usage:
    python3 test_uvc_camera.py [--device /dev/video0] [--output uvc_test_frame.jpg]
"""

import sys
import os
import argparse
import subprocess

def check_v4l2_devices():
    print("==================================================")
    print(" 1. Scanning V4L2 Video Devices (/dev/video*)")
    print("==================================================")
    
    video_devs = [f"/dev/{dev}" for dev in os.listdir('/dev') if dev.startswith('video')]
    video_devs.sort()
    
    if not video_devs:
        print("❌ No /dev/video* devices found!")
        print("   -> Make sure your USB webcam is plugged in.")
        print("   -> Check dmesg output: 'dmesg | grep uvcvideo'")
        return []
    
    print(f"Detected video device nodes: {video_devs}")
    
    # Try running v4l2-ctl --list-devices if available
    try:
        res = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True)
        if res.returncode == 0:
            print("\nv4l2-ctl Device Tree:")
            print(res.stdout)
    except FileNotFoundError:
        print("ℹ️  v4l2-ctl command not found (install with 'sudo apt install v4l-utils')")
        
    return video_devs

def print_device_caps(device_path):
    print(f"\nQuerying capabilities for device: {device_path}")
    try:
        res = subprocess.run(['v4l2-ctl', '-d', device_path, '--list-formats-ext'], capture_output=True, text=True)
        if res.returncode == 0:
            print("Supported Formats & Resolutions:")
            print(res.stdout)
    except Exception as e:
        print(f"Could not query formats via v4l2-ctl: {e}")

def test_opencv_capture(device_index=0, output_path="uvc_test_frame.jpg"):
    print("\n==================================================")
    print(f" 2. Testing Frame Capture via OpenCV (index {device_index})")
    print("==================================================")
    
    try:
        import cv2
    except ImportError:
        print("❌ OpenCV (cv2) is not installed in Python environment!")
        sys.exit(1)
        
    print(f"OpenCV Version: {cv2.__version__}")
    
    # Open VideoCapture using V4L2 backend
    cap = cv2.VideoCapture(device_index, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print(f"❌ Failed to open video device at index {device_index} (/dev/video{device_index})")
        return False
        
    # Request standard 640x480 resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Opened Device Index {device_index}: {int(width)}x{int(height)} @ {fps} FPS")
    
    # Read a few warm-up frames (auto-exposure settling)
    print("Capturing warm-up frames...")
    for i in range(5):
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ Warning: Failed to read warm-up frame {i+1}")
            
    # Read actual frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        print("❌ Failed to capture frame from UVC camera.")
        return False
        
    print(f"✅ Successfully captured frame! Frame shape: {frame.shape}, dtype: {frame.dtype}")
    
    # Save test frame
    cv2.imwrite(output_path, frame)
    if os.path.exists(output_path):
        size_kb = os.path.getsize(output_path) / 1024.0
        print(f"✅ Saved screenshot to: {output_path} ({size_kb:.1f} KB)")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Test UVC USB Webcam Capture on Raspberry Pi")
    parser.add_argument("--device-index", type=int, default=0, help="Video device index (default: 0 for /dev/video0)")
    parser.add_argument("--output", type=str, default="uvc_test_frame.jpg", help="Output frame path")
    args = parser.parse_args()
    
    print("==================================================")
    print(" UVC (USB Webcam) Support Verification Utility")
    print("==================================================")
    
    devs = check_v4l2_devices()
    if devs:
        target_dev = f"/dev/video{args.device_index}"
        if target_dev in devs:
            print_device_caps(target_dev)
            
    success = test_opencv_capture(device_index=args.device_index, output_path=args.output)
    
    print("\n==================================================")
    if success:
        print(" 🎉 RESULT: UVC CAMERA TEST PASSED!")
    else:
        print(" ❌ RESULT: UVC CAMERA TEST FAILED!")
    print("==================================================")

if __name__ == "__main__":
    main()
