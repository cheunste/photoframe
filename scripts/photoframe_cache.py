#!/usr/bin/python3

import os
import sqlite3
import logging
import random

DB_PATH = r"/home/photoframe/script/cache.db"
LOG_FILE = r"/home/photoframe/script/cache.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

def init_cache_db(db_path = DB_PATH)->None:
    db_exists = os.path.exists(db_path)
    if db_exists:
        return
    
    conn=sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   shown TEXT NOT NULL
                   )
                   """)

    conn.commit()
    conn.close()

def add_to_cache(photo_name:str)->None:

    conn= sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO cache(name,shown)VALUES(?,?)",(photo_name,"False"))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Issue adding {photo_name} to cache")

    finally:
        cursor.close()
        conn.close()

def remove_from_cache(path:str)->None:
    pass

def populate_cache(directory:str)->None:
    if not os.path.isdir(directory):
        return
    files_to_insert = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory,item)
        if os.path.isfile(full_path):
            files_to_insert.append((item,False))
    
    # If direcotry is empty
    if not files_to_insert:
        logging.debug(f"there are no files in {directory}")
        return
    
    conn= sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.executemany("INSERT INTO cache(name,shown)VALUES(?,?)",files_to_insert,"False")
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

def mark_shown_status(photos_list:list[str],status:bool)->None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for name in photos_list:
            cursor.execute("SELECT 1 from cache where name =?",(name,))
            exists = cursor.fetchone()
            if exists:
                cursor.execute(f"UPDATE cache SET shown = '{status}' WHERE name =?",(name,))
            else:
                cursor.execute(f"INSERT into cache (name,shown) VALUES (?,'{status}')")

        conn.commit()
    except:
        logging.error(f"An error occured whiel marking {photos_list} as shown")
        conn.rollback()
    finally:
        conn.close()

def get_photos_by_shown(is_shown: bool) -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Convert Python boolean to your schema's string format ('True' or 'False')
    status_str = "True" if is_shown else "False"

    try:
        cursor.execute("SELECT name FROM cache WHERE shown = ?", (status_str,))
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []
    finally:
        conn.close()

def mark_all_not_shown() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # A simple UPDATE without a WHERE clause applies to every row in the table
        cursor.execute("UPDATE cache SET shown = 'False'")
        conn.commit()
        print(f"Successfully reset all cache entries to False.")

    except sqlite3.Error as e:
        print(f"An error occurred while resetting cache: {e}")
        conn.rollback()

    finally:
        conn.close()

def select_photos(photos_to_show):
    photos_not_shown = get_photos_by_shown(False)
    number_of_not_shown_photos = len(photos_not_shown)
    logging.debug(f"photos not shown: {photos_not_shown}")
    logging.debug(f"Number of photos {number_of_not_shown_photos }")

    if number_of_not_shown_photos < photos_to_show:
        logging.warning(f"there are less than {photos_to_show}")
        remaining_photos = photos_not_shown
        shown_photos = get_photos_by_shown(True)
        need_photos = photos_to_show - number_of_not_shown_photos
        
        logging.debug(f"There are {need_photos} photos needed to get to the daily requirement of {photos_to_show}. Trying to get {need_photos} from already shown photos")
        logging.debug(f"already shown photos {shown_photos}")

        additional_photos = random.sample(shown_photos,need_photos)
        photos_to_show =  remaining_photos  + additional_photos
        mark_all_not_shown()
        mark_shown_status(photos_to_show,True)
        return photos_to_show

    random_sample= random.sample(photos_not_shown,photos_to_show)
    mark_shown_status(random_sample,True)
    return random_sample

if __name__  ==  "__main__":
    init_cache_db()
    populate_cache(r"/home/photoframe/album/")
    mark_all_not_shown()
