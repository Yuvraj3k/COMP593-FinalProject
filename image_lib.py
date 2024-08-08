import requests
import ctypes


def main():
    # TODO: Add code to test the functions in this module
    return

def download_image(image_url):
    print(f'Downloading image from {image_url}...', end='')
    resp_msg = requests.get(image_url)

    # Check if the image was retrieved successfully
    if resp_msg.status_code == requests.codes.ok:
        print('success')
        return resp_msg.content
    else:
        print('failure')
        print(f'Response code: {resp_msg.status_code} ({resp_msg.reason})')


def save_image_file(image_data, image_path):
    try:
        print(f"Saving image file as {image_path}...", end='')
        with open(image_path, 'wb') as file:
            file.write(image_data)
        print("success")
        return True
    except:
        print("failure")
        return False


def set_desktop_background_image(image_path):
    print(f"Setting desktop to {image_path}...", end='')
    SPI_SETDESKWALLPAPER = 20
    try:
        if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3):
            print("success")
            return True
        else:
            print("failure")
    except:
        print("failure")
    return False


def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width
    and/or height while maintaining the aspect ratio  

    Args:
        image_size (tuple[int, int]): Original image size in pixels (width, height) 
        max_size (tuple[int, int], optional): Maximum image size in pixels (width, height). Defaults to (800, 600).

    Returns:
        tuple[int, int]: Scaled image size in pixels (width, height)
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    # NOTE: This function is only needed to support the APOD viewer GUI
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()