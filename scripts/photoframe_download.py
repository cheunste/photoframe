#!/usr/bin/python3

import requests
import zipfile
import os
import re
import logging
import random
import photoframe_cache
import shutil
from pathlib import Path

BASE_URL = "INSERT_PHOTOPRISM_URL_HERE"
AUTH_DATA = {"username": "PHOTOPRISM_ACCOUNT", "password": "PHOTOPRISM_PW"}
ALBUM_NAME = "photoprism.zip"

PHOTO_LOCATION = r"/home/photoframe/Desktop/photo/"
ALBUM_LOCATION = r"/home/photoframe/album/"
LOG_FILE ="/home/photoframe/script/logging.log"

PHOTOS_TO_SHOW = 30

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

def create_session():
    session = requests.Session()
    auth_resp = session.post(f"{BASE_URL}/session", json=AUTH_DATA).json()
    access_token = auth_resp.get("access_token")
    download_token = auth_resp.get("config").get("downloadToken")
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    return (session,download_token)

def get_photoframe_album_uid(session):
    albums = session.get(f"{BASE_URL}/albums?count=1&order=title&q=Photoframe").json()
    uid = albums[0]["UID"]
    return uid

def download_missing_photos_from_album():
    session,download_token = create_session()
    current_photos_set = set(os.listdir(ALBUM_LOCATION))

    album_photos = get_photos_and_hash_list_from_album()
    album_photo_name_list = [name for name,hash in album_photos]

    missing_photos = list(set(album_photo_name_list)-current_photos_set)
    logging.info(f"the following are missing: {missing_photos }")
    download_photo_hash_list = [photo for photo in album_photos if photo[0] in missing_photos]
    logging.info(f"the following will be downloaded {download_photo_hash_list} ")

    for photo in download_photo_hash_list:
        print(photo)
        _,photo_hash = photo
        download_picture(session,download_token,photo_hash)


def get_photos_and_hash_list_from_album()->list[tuple[str,str]]:
    session,t = create_session()
    uid = get_photoframe_album_uid(session)
    photos_list =[]

    photos_url = f"{BASE_URL}/photos?merged=true"
    search_params = {
        "album":uid,
        "count":1000,
        "order":"oldest"
    }
    res = session.get(photos_url, params=search_params)
    if res.status_code != 200:
        print(f"Failed to fetch photos: {res.text}")
        exit()
    photos = res.json()

    for photo in photos:
        # if a photo contains an extra '.', that means you fucked up converting HEIC to a png/jpeg
        if photo["Name"].__contains__("."):
            continue
        photos_list.append((photo["Name"],photo["Hash"]))
    return photos_list

def download_picture(session,token,hash):
    download_url = f"{BASE_URL}/dl/{hash}?t={token}"
    res = session.get(download_url, stream=True)
    if res.status_code == 200:
            content_disp = res.headers.get('Content-Disposition', '')
            filename_match = re.search(r'filename="([^"]+)"', content_disp)

            if filename_match:
                filename = filename_match.group(1)
            else:
                # Fallback if header is missing (uses the hash as the name)
                print(f"Header is missing for {filename}")
                filename = f"{hash}"

            file_path = os.path.join(ALBUM_LOCATION, filename)

            with open(file_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("Download completed successfully!")
            photoframe_cache.add_to_cache(filename)
            logging.info(f"Adding {filename} to cache")
    else:
        print(f"failed with status: {res.status_code}")
        print(res.text) # This might print a clearer error message from PhotoPrism

def chose_daily_photos():
    selected = photoframe_cache.select_photos(PHOTOS_TO_SHOW)
    photo_path = Path( PHOTO_LOCATION )
    album_dir = Path(ALBUM_LOCATION )
    logging.info(f"The following photos will be selected for the day: {selected}")

    for photo in selected:
        album_path = album_dir / photo
        if album_path.is_file():
            try:
                shutil.move(str(album_path),str(photo_path))
            except Exception as e:
                logging.error(f"Error moving {photo} from {album_path} to {photo_path}")

def clear_photo_directory():
    photo_path = Path(PHOTO_LOCATION)
    for photo in photo_path.iterdir():
        if photo.is_file:
            photo.unlink()

if __name__=="__main__":
    # selected=select_photos(30)
    # logging.info(f"Selected: {selected}")
    clear_photo_directory()
    download_missing_photos_from_album()
    chose_daily_photos()
