import json
import urllib.request
from datetime import datetime
import logging
from os import path, environ
import sys


def get_actual_date_in_utc() -> str:
    return str(datetime.now().date())


def get_image_url_from_api(api: str, date: str, time: str) -> str:
    if len(time) < 2:
        time = "0" + time
    endpoint = f"{api}/{date}T{time}:00"
    logging.debug(f"{endpoint=}")
    response = urllib.request.urlopen(endpoint)
    url = json.loads(response.read())
    url = url["image"]["url"]
    # result = result["image_highres"]["url"]
    logging.debug(f"{url=}")
    return url


def download_image(url: str, path: str) -> None:
    urllib.request.urlretrieve(url, path)
    print(f"The image has been saved in {path}.")


class HoursError(Exception):
    pass


def get_filepath(date: str, time: str) -> str:
    download_dir = path.abspath(path.join(environ.get('HOMEPATH'), 'Downloads'))
    filename = f"{date}T0{time}L.jpg" if len(str(time)) < 2 else f"{date}T{time}L.jpg"
    filepath = path.join(download_dir, filename)
    logging.debug(f"{filepath=}")
    return filepath


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more details, INFO normally
    while True:
        try:
            start = int(input("The hour of the first Moon visualization image (00-23): "))
            end = int(input("The hour of the last Moon visualization image (00-23): "))
            if start > end:
                raise HoursError

            today = get_actual_date_in_utc()

            for hour in range(start, end + 1):
                hour = str(hour)
                image_url = get_image_url_from_api(api="https://svs.gsfc.nasa.gov/api/dialamoon", date=today, time=hour)
                filepath = get_filepath(date=today, time=hour)
                download_image(url=image_url, path=filepath)
            break
        except ValueError:
            print("Please enter a value between 00 and 23.")
        except HoursError:
            print("The hour of the first Moon visualization image should be earlier then the last.")
        except urllib.error.HTTPError:
            print("Endpoint not found!")
        except KeyboardInterrupt:
            sys.exit("Program stopped by user.")
        except urllib.error.URLError:
            sys.exit("Connection timeout! API did not respond! Check API URL or network connection!")
    print("Done.")
