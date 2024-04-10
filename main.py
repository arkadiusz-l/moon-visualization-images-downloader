import json
from datetime import datetime, timedelta
import logging
import re
import os
import sys
import requests


def get_date_in_utc(date: str) -> str:
    if date == "t":
        return str(datetime.now().date())
    elif date == "tm":
        return str(datetime.now().date() + timedelta(days=1))
    elif bool(datetime.strptime(date, "%Y-%m-%d")):
        return date
    else:
        raise DateError


def get_image_url_from_api(api: str, date: str, time: str) -> str:
    if len(time) < 2:
        time = "0" + time
    endpoint = f"{api}/{date}T{time}:00"
    logging.debug(f"{endpoint=}")
    response = requests.get(endpoint)
    url = json.loads(response.content)
    url = url["image"]["url"]
    # result = result["image_highres"]["url"]
    logging.debug(f"{url=}")
    return url


def download_image(url: str, path: str) -> None:
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as image:
            image.write(response.content)
    print(f"The image has been saved in {path}.")


class HoursError(Exception):
    pass


class DateError(Exception):
    pass


def get_filepath(download_dir: str, date: str, time: str) -> str:
    filename = f"{date}T0{time}L.jpg" if len(time) < 2 else f"{date}T{time}L.jpg"
    filepath = os.path.join(download_dir, filename)
    logging.debug(f"{filepath=}")
    return filepath


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more details, INFO normally
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # disable standard DEBUG logs
    while True:
        try:
            date = input("Enter the date for which I should download images (YYYY-MM-DD or 't' for Today, 'tm' for Tommorow): ")
            start_hour = int(input("The hour of the first Moon visualization image (00-23): "))
            end_hour = int(input("The hour of the last Moon visualization image (00-23): "))
            if start_hour > end_hour:
                raise HoursError

            date = get_date_in_utc(date)

            for hour in range(start_hour, end_hour + 1):
                hour = str(hour)
                image_url = get_image_url_from_api(api="https://svs.gsfc.nasa.gov/api/dialamoon", date=date, time=hour)
                filepath = get_filepath(
                    download_dir=os.path.abspath(os.path.join(os.environ.get("HOMEPATH"), "Downloads", "Moon Phases")),
                    date=date,
                    time=hour
                )
                download_image(url=image_url, path=filepath)
            break
        except ValueError:
            print("Please enter a value between 00 and 23.")
        except HoursError:
            print("The hour of the first Moon visualization image should be earlier then the last.")
        except DateError:
            print("The given date is not valid!")
        except KeyboardInterrupt:
            sys.exit("Program stopped by user.")
        except requests.exceptions.ConnectionError:
            sys.exit("API did not respond! Check API URL or network connection!")
    print("Done.")
