""" 
COMP 593 - FinalProject

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""

from datetime import date
import sqlite3
import hashlib
import os
import re
from pathlib import Path

import image_lib
import apod_api
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

def main():
    apod_date = get_apod_date()
    init_apod_cache()
    apod_id = add_apod_to_cache(apod_date)
    apod_info = get_apod_info(apod_id)
    image_lib.set_desktop_background_image(apod_info['file_path'])
    
def get_apod_date():
    num_params = len(sys.argv) - 1
    if num_params >= 1:
        
        try:
            apod_date = date.fromisoformat(sys.argv[1])
        except ValueError as err:
            print(f'Error: Invalid date format; {err}')
            sys.exit('Script execution aborted')

        
        MIN_APOD_DATE = date.fromisoformat("1995-06-16")
        if apod_date < MIN_APOD_DATE:
            print(f'Error: Date too far in past; First APOD was on {MIN_APOD_DATE.isoformat()}')
            sys.exit('Script execution aborted')
        elif apod_date > date.today():
            print('Error: APOD date cannot be in the future')
            sys.exit('Script execution aborted')
    else:
        
        apod_date = date.today()
    return apod_date



def init_apod_cache(script_dir=None):
    image_cache_dir = os.path.join(script_dir, 'images') if script_dir else 'images'
    image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

    print(f"Image cache directory: {image_cache_dir}")
    
    try:
        os.mkdir(image_cache_dir)
        print("Image cache directory created.")
    except FileExistsError as err_info:
        print("Image cache directory already exists.")

    print(f"Image cache DB: {image_cache_db}")

    if os.path.exists(image_cache_db): 
        print("Image cache DB already exists.")
    else:
        db_cxn = sqlite3.connect(image_cache_db)
        db_cursor = db_cxn.cursor()

        table_create_query = """
                    CREATE TABLE IF NOT EXISTS image_data
                    (id INTEGER PRIMARY KEY, title TEXT, explanation TEXT, file_path TEXT, sha256 TEXT);
                    """
        db_cursor.execute(table_create_query)
        print("Image cache DB created.")

def add_apod_to_cache(apod_date):
    
    print("APOD date:", apod_date.isoformat())
    apod_info = apod_api.get_apod_info(apod_date.isoformat())
    if not apod_info:
        return 0
    apod_title = apod_info['title']
    print("APOD title:", apod_title)
    # Download the APOD image
    apod_url = apod_api.get_apod_image_url(apod_info_dict=apod_info)
    # Check whether the APOD already exists in the image cache
    apod_image_data = image_lib.download_image(apod_url)
    apod_sha256 = hashlib.sha256(apod_image_data).hexdigest()
    print("APOD SHA-256:", apod_sha256)
    apod_id = get_apod_id_from_db(apod_sha256)
    if apod_id != 0:
        return apod_id
    apod_path = determine_apod_file_path(apod_title, apod_url)
    print("APOD file path:", apod_path)
    if not image_lib.save_image_file(apod_image_data, apod_path): return 0
    # Add the APOD information to the DB
    apod_id = add_apod_to_db(apod_title, apod_info['explanation'], apod_path, apod_sha256)

    return apod_id

def add_apod_to_db(title, explanation, file_path, sha256):
    print("Adding APOD to image cache DB...", end='')
    try:

        db_cxn = sqlite3.connect(image_cache_db)
        db_cursor = db_cxn.cursor()
        db_cursor.execute("""
                INSERT INTO image_data (title, explanation, file_path, sha256)
                VALUES (?, ?, ?, ?);
            """, (title, explanation, file_path, sha256.upper()))
        db_cxn.commit()
        print("success")
        db_cxn.close()
        return db_cursor.lastrowid
    except Exception as e:
        print(f"Failed to add APOD to DB: {e}")
        return 0

def get_apod_id_from_db(image_sha256):
    db_cxn = sqlite3.connect(image_cache_db)
    db_cursor = db_cxn.cursor()
    db_cursor.execute("SELECT id FROM image_data WHERE sha256=?;", (image_sha256.upper(),))
    query_results = db_cursor.fetchone()
    db_cxn.close()
    
    if query_results is not None:
        print("APOD image is already in cache.")
        return query_results[0]
    else:
        print("APOD image is not already in cache.")
        return 0

def determine_apod_file_path(image_title, image_url):
    
    file_ext = image_url.split(".")[-1]

    file_name = image_title.strip()
    file_name = file_name.replace(' ', '_')
    file_name = re.sub(r'[^a-z]', '', file_name)
    file_name = '.'.join((file_name, file_ext))

    file_path = os.path.join(image_cache_dir, file_name)

    return file_path

def get_apod_info(image_id):
    db_cxn = sqlite3.connect(image_cache_db)
    db_cursor = db_cxn.cursor()
    
    # add appropriate query_result
    image_path_query = f"SELECT * FROM image_data WHERE id={image_id};" 
    db_cursor.execute(image_path_query)
    
    query_result = db_cursor.fetchone()
    db_cxn.close()

    keys = ("id","title", "explanation", "file_path", "sha256")
    apod_info = dict(zip(keys,query_result))
    return apod_info

def get_apod_info_by_title(title):
    db_cxn = sqlite3.connect(image_cache_db)
    db_cursor = db_cxn.cursor()

    # Query DB for APOD information based on the title
    db_cursor.execute("SELECT * FROM image_data WHERE title=?", (title,))
    apod_info = db_cursor.fetchone()
    db_cxn.close()

    if apod_info:
        keys = ("id", "title", "explanation", "file_path", "sha256")
        return dict(zip(keys, apod_info))
    
    else:
        return None


def get_all_apod_titles():
    db_cxn = sqlite3.connect(image_cache_db)  
    table_create_query = """
                    CREATE TABLE IF NOT EXISTS image_data
                    (id INTEGER PRIMARY KEY, title TEXT, explanation TEXT, file_path TEXT, sha256 TEXT);
                    """
    db_cursor = db_cxn.cursor()
    db_cursor.execute(table_create_query)

    image_titles_query = "SELECT title FROM image_data;"
    db_cursor.execute(image_titles_query)
    
    image_titles = db_cursor.fetchall()
    db_cxn.close()

    return tuple([t[0] for t in image_titles])

if __name__ == '__main__':
    main()