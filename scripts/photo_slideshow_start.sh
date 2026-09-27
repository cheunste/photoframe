#!/bin/bash

# Tell feh which display screen to use
export DISPLAY=:0
export XAUTHORITY=/home/photoframe/.Xauthority
export XDG_RUNTIME_DIR=/run/photoframe/1000

# Path to your photos directory
PHOTO_DIR="/home/photoframe/Desktop/photo"

# Run feh with slideshow optimization flags
# -F: fullscreen
# -Z auto-zooms
# -z randomizes
# -D: Sets the delay to X seconds between phtoo
# -x: borderless
# -Y: hide cursor
# & Runs in the background. So terminal isn't locked up. Might not work in cron script
FEH_CMD="feh -Y -F -x -z -bg-fill -D 60 $PHOTO_DIR"

if [ -t 0 ]; then
	echo "Runnign manually"
	$FEH_CMD &
else
	echo "Runnign via cron"
	exec $FEH_CMD 
fi
