#!/bin/bash
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/1000
wlr-randr --output HDMI-A-1 --on
