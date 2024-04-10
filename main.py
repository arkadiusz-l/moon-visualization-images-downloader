import json
from datetime import datetime, timedelta
import logging
import re
import os
import sys
import requests


class HoursOrderError(Exception):
    pass


class HoursError(Exception):
    pass


def get_hour_from_user(text: str) -> int:
    hour = int(input(f"The hour of the {text} Moon visualization image (0-23): "))
    if hour < 0 or hour > 23:
        raise HoursError
    return hour


def get_date_in_utc(date: str) -> str:
    if date == "t":
        return str(datetime.now().date())
    elif date == "tm":
        return str(datetime.now().date() + timedelta(days=1))
    elif bool(datetime.strptime(date, "%Y-%m-%d")):
        return date


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


def get_filepath(download_dir: str, date: str, time: str) -> str:
    filename = f"{date}T0{time}L.jpg" if len(time) < 2 else f"{date}T{time}L.jpg"
    filepath = os.path.join(download_dir, filename)
    logging.debug(f"{filepath=}")
    return filepath


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more details, INFO normally
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # disable standard DEBUG logs

    date = None
    start_hour = None
    end_hour = None
    error_message = "Please enter a value between 0 and 23."

    try:
        while True:
            try:
                date = input(
                    "Enter the date for which I should download images (YYYY-MM-DD or 't' for Today, 'tm' for Tommorow): "
                )
                date = get_date_in_utc(date)
            except ValueError:
                print("The date is not valid! Please enter a valid date.")
                continue
            break

        while True:
            try:
                start_hour = get_hour_from_user(text="first")
                end_hour = get_hour_from_user(text="last")
                if start_hour > end_hour:
                    raise HoursOrderError
            except ValueError:
                print(error_message)
                continue
            except HoursError:
                print(error_message)
                continue
            except HoursOrderError:
                print("The hour of the first Moon visualization image should be earlier then the last one.")
                continue

            try:
                for hour in range(start_hour, end_hour + 1):
                    hour = str(hour)
                    image_url = get_image_url_from_api(api="https://svs.gsfc.nasa.gov/api/dialamoon", date=date, time=hour)
                    filepath = get_filepath(
                        download_dir=os.path.abspath(os.path.join(os.environ.get("HOMEPATH"), "Downloads", "Moon Phases")),
                        date=date,
                        time=hour
                    )
                    download_image(url=image_url, path=filepath)
                print("Done.")
            except requests.exceptions.ConnectionError:
                sys.exit("API did not respond! Check API URL or network connection!")
            break
    except KeyboardInterrupt:
        sys.exit("The program has been stopped by user.")
