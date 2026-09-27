# photoframe

This is a raspberry pi Photoframe. Unlike other phtooframes where you load photos and run 24/7, this photoframe is designed to

- work with an on-prem instance of photoframe and will pull from a specific album (also called photoframe)
- only show a set amount of photos per day. This way you can enjoy looking at photos more often. This also means there's a feature that keeps track of photos that have been displayed.
- Is designed to turn off the display at night and turn on in the morning with cron scripts

# Installation and Requirements

## Hardware

- A raspberry pi. I used a Raspberry pi 3B, but any version 3B or above will do, even the Pi Zero 2W.
- A display for raspberry pi that **must** contain an HDMI adapter. This is to avoid using an HDMI cable. I cannot stress this enough, avoid a HDMI cable. Even a 1 foot HDMI cable is heavy and combersome.
- A power supply for your raspberry pi. you will need a power supply that can supply enough power to both the screen display and the Raspberry pi.
- A frame for your display. You're on your own for this one. 3D print it or make it out of wood (like what I did)

# Prereq Software Installation
- Create a user. For simplicity, the user here will be called "photoframe".
- Python 3 and sqlite3 is installed on this rapsberry pi
- feh. Do a *sudo apt-get install feh*

# Installation instructions
1. Create a 'script' folder. (ie /home/phtoframe/script/)
1. Clone/copy all the files in the script folder to the newlyh created script folder
1. open up the phtooframe_download.py file and update the BASE_URL, AUTH_DATA with your photoprism album link and credential. then update PHOTO_LOCATION and ALBUM_LOCATION
1. Update cron. Do a crontab -e and then copy/paste the content from the crontab.txt.

# Variables and Parameters

## photoframe_download.py
| Variables | what it does |
| PHOTOS_TO_SHOW | Number of photos to show for the day. Default 30| 
| PHOTO_LOCATION | this is the folder where the scripts will put the photo to|
| ALBUM_LOCATION | this is the folder where the photo album from photoprism will be downloaded to|
| BASE_URL | The photoprism URL. This can be anything you have access to and can perform GET requests  |
| AUTH_DATA | The photoprism account credential. Not really designed for encryption since it is an onprem photoframe|