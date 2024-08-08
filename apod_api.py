'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import sys
from pathlib import Path
import requests
from datetime import date
from sys import argv
import image_lib
import os
NASA_API_KEY = ''  
APOD_URL = "https://api.nasa.gov/planetary/apod"


def main():
    import sys
    num_params = len(sys.argv) - 1
    import sys
    sys.argv
    apod_date = date.fromisoformat(argv[1])

    

    apod_info_dict = get_apod_info(apod_date)
    if apod_info_dict:
        apod_url = get_apod_image_url(apod_info_dict)
        apod_image_data = image_lib.download_image(apod_url)
        image_lib.save_image_file(apod_image_data, r'C:\temp\image.jpg')
    return

def get_apod_info(apod_date):
    apod_params = {
        'api_key': NASA_API_KEY,
        'date': apod_date,
        'thumbs': True
    }

   
    print(f'Getting {apod_date} APOD information from NASA...', end='')
    resp_msg = requests.get(APOD_URL, params=apod_params)

    
    if resp_msg.status_code == requests.codes.ok:
        print('success')        
        apod_info_dict = resp_msg.json() 
        return apod_info_dict
    else:
        print('failure')
        print(f'Response code: {resp_msg.status_code} ({resp_msg.reason})')
        return 'failure'

def get_apod_image_url(apod_info_dict):
    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict['hdurl']
    elif apod_info_dict['media_type'] == 'video':        
        return apod_info_dict['thumbnail_url']

def get_apod_date():
    num_params = len(sys.argv) - 1
    if num_params >= 1:
        
        try:
            apod_date = date.fromisoformat(sys.argv[1])
            print(apod_date, "apod_date")
        except ValueError as err:
            print(f'Error: Invalid date format; {err}')
            sys.exit('Script execution aborted')

       

        MIN_APOD_DATE = date.fromisoformat("1995-06-16")  
        print(MIN_APOD_DATE, "MIN_APOD_DATE")
        if apod_date < MIN_APOD_DATE:
            print(f'Error: Date too far in past; First APOD was on {MIN_APOD_DATE.isoformat()}')
            sys.exit('Script execution aborted')
        elif apod_date > date.today():
            print('Error: APOD date cannot be in the future')
            sys.exit('Script execution aborted')
    else:
        
        apod_date = date.today()  

    return apod_date


if __name__ == '__main__':

    main()
