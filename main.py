import os
import sys
import json
import logging
from datetime import datetime, timedelta
import requests


class HoursOrderError(Exception):
    pass


class HoursValueError(Exception):
    pass


def get_hour_from_user(text: str) -> int:
    hour = int(input(f"Enter the hour of the {text} Moon visualization image (0-23): "))
    if hour < 0 or hour > 23:
        raise HoursValueError
    return hour


def get_date_in_utc(date: str) -> str:
    if date == "t":
        return str(datetime.now().date())
    elif date == "tm":
        return str(datetime.now().date() + timedelta(days=1))
    elif len(date) <= 3 and date.startswith("+"):
        return str(datetime.now().date() + timedelta(days=int(date[1:])))
    elif bool(datetime.strptime(date, "%Y-%m-%d")):
        return date


def get_image_url_from_api(api: str, date: str, hour: str) -> str:
    hour = "0" + hour if len(hour) < 2 else hour
    endpoint = f"{api}/{date}T{hour}:00"
    logging.debug(f"{endpoint=}")
    response = requests.get(endpoint)
    image_url = json.loads(response.content)
    image_url = image_url["image"]["url"]
    logging.debug(f"{image_url=}")
    return image_url


def download_image(url: str, path: str) -> None:
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as image:
            image.write(response.content)
    print(f"The image has been saved in {path}.")


def get_filepath(download_dir: str, date: str, hour: str) -> str:
    filename = f"{date}T0{hour}L.jpg" if len(hour) < 2 else f"{date}T{hour}L.jpg"
    filepath = os.path.join(download_dir, filename)
    logging.debug(f"{filepath=}")
    return filepath


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more details, INFO normally
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # disable standard DEBUG logs from the 'requests' library

    date = None
    start_hour = None
    end_hour = None
    error_message = "Please enter a value between 0 and 23."

    try:
        while True:
            try:
                date = input(
                    "Enter the date for which I should download images.\n"
                    "You can enter YYYY-MM-DD or 't' for today, 'tm' for tommorow.\n"
                    "You can also enter '+1' for tommorow, '+2' for the day after tommorow, etc: "
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
            except HoursValueError:
                print(error_message)
                continue
            except HoursOrderError:
                print("The hour of the first Moon visualization image should be earlier then the last one.")
                continue

            try:
                for hour in range(start_hour, end_hour + 1):
                    hour = str(hour)
                    url = get_image_url_from_api(api="https://svs.gsfc.nasa.gov/api/dialamoon", date=date, hour=hour)
                    filepath = get_filepath(
                        download_dir=os.path.abspath(
                            os.path.join(os.environ.get("HOMEPATH"), "Downloads", "Moon Phases")
                        ),
                        date=date,
                        hour=hour
                    )
                    download_image(url=url, path=filepath)
                print("Done.")
            except requests.exceptions.ConnectionError:
                sys.exit("API did not respond! Check API URL or network connection!")
            break
    except KeyboardInterrupt:
        sys.exit("The program has been stopped by user.")
