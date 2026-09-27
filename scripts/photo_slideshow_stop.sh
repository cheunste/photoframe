#!/bin/bash

# Check if feh is actually running before trying to kill it
if pgrep -x "feh" > /dev/null
then
    echo "Stopping the feh slideshow..."
    pkill -x "feh"
else
    echo "feh is not currently running."
fi
