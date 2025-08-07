#!/bin/bash
# Start Xvfb (X virtual framebuffer) in the background.
# -screen 0 1600x900x24: Creates a virtual screen 0 with 1600x900 resolution and 24-bit color.
# -ac: Disables access control, allowing any client to connect.
# +extension GLX +render -noreset: Enables OpenGL extension, rendering, and prevents server reset.
Xvfb :99 -screen 0 1600x900x24 -ac +extension GLX +render -noreset &

# Start the VNC server and noVNC proxy
# -display :99: Connects to the virtual display.
# -nopw: Disables password protection for easy access.
# -forever: Keeps the VNC server running.
x11vnc -display :99 -nopw -forever &
websockify -D --web=/usr/share/novnc/ 6080 localhost:5900 &

# Wait for 2 seconds to ensure Xvfb and services are fully initialized.
sleep 2

# Execute the main Python application.
exec python pyPSA_db.py
