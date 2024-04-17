import os
import sys
import json
import logging
from datetime import datetime, timedelta, timezone
import requests
from tqdm import tqdm


class HoursOrderError(Exception):
    pass


class HourValueError(Exception):
    pass


class DateOutOfRangeError(Exception):
    pass


def get_hour_from_user(text: str) -> int:
    hour = int(input(f"Enter the hour of the {text} Moon visualization image (0-23): "))
    if hour < 0 or hour > 23:
        raise HourValueError
    return hour


def parse_user_date(date: str) -> str:
    if date == "t":
        return str(datetime.now().date())
    elif date == "tm":
        return str(datetime.now().date() + timedelta(days=1))
    elif len(date) <= 3 and date.startswith("+"):
        return str(datetime.now().date() + timedelta(days=int(date[1:])))
    elif bool(datetime.strptime(date, "%Y-%m-%d")):
        return date


def convert_user_date_and_hour_to_utc(date: str, hour: str) -> str:
    hour = "0" + hour if 2 > len(hour) > 0 else hour
    user_datetime_str = f"{date} {hour}"
    user_datetime = datetime.strptime(user_datetime_str, "%Y-%m-%d %H")
    utc_datetime = user_datetime.astimezone(timezone.utc)
    logging.debug(f"{utc_datetime=}")
    if utc_datetime < datetime(2011, 1, 1, 0, 0, tzinfo=timezone.utc) or utc_datetime > datetime(datetime.now().year, 12, 31, 23, 0, tzinfo=timezone.utc):
        raise DateOutOfRangeError
    return utc_datetime.strftime("%Y-%m-%dT%H")


def get_image_url_from_api(api: str, date: str) -> str:
    endpoint = f"{api}/{date}:00"
    logging.debug(f"{endpoint=}")
    response = requests.get(endpoint)
    image_url = json.loads(response.content)
    image_url = image_url["image_highres"]["url"]
    logging.debug(f"{image_url=}")
    return image_url


def download_image(url: str, path: str) -> None:
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        image_length = int(response.headers.get("content-length", 0))
        logging.debug(f"{image_length=}")
        chunk_size = 1024
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as image, tqdm(
                desc=path.split("\\")[-1],
                total=image_length,
                unit='iB',
                unit_scale=True,
                unit_divisor=chunk_size,
        ) as bar:
            for data in response.iter_content(chunk_size=chunk_size):
                size = image.write(data)
                bar.update(size)
    print(f"The image has been saved in {path}.")


def get_filepath(download_dir: str, date: str, hour: str) -> str:
    filename = f"{date}T0{hour}L.tif" if len(hour) < 2 else f"{date}T{hour}L.tif"
    filepath = os.path.join(download_dir, filename)
    logging.debug(f"{filepath=}")
    return filepath


if __name__ == "__main__":
    logging_level = logging.INFO
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d":
            logging_level = logging.DEBUG
            print("/// The program is running in DEBUG mode ///")
        elif sys.argv[1] != "-d":
            print("An unsupported argument was entered.")
            sys.exit()
    logging.basicConfig(level=logging_level)
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # disable standard DEBUG logs from the 'requests' library

    date = None
    user_start_hour = None
    user_end_hour = None
    hour_value_error_message = "Please enter a value between 0 and 23."

    try:
        while True:
            try:
                date = input(
                    "Enter the date for which I should download images.\n"
                    "You can enter YYYY-MM-DD or 't' for today, 'tm' for tommorow.\n"
                    "You can also enter '+1' for tommorow, '+2' for the day after tommorow, etc: "
                )
                date = parse_user_date(date)
            except ValueError:
                print("The date is not valid! Please enter a valid date.")
                continue
            break

        while True:
            try:
                user_start_hour = get_hour_from_user(text="first")
                user_end_hour = get_hour_from_user(text="last")
                if user_start_hour > user_end_hour:
                    raise HoursOrderError
            except ValueError:
                print(hour_value_error_message)
                continue
            except HourValueError:
                print(hour_value_error_message)
                continue
            except HoursOrderError:
                print("The hour of the first Moon visualization image should be earlier then the last one.")
                continue

            choice = input(f"{user_end_hour - user_start_hour + 1} file(s) will be downloaded. Enter 'y' if continue: ")
            if choice == "y":
                downloaded = 0
                try:
                    for user_hour in range(user_start_hour, user_end_hour + 1):
                        user_hour = str(user_hour)
                        utc_date = convert_user_date_and_hour_to_utc(date=date, hour=user_hour)
                        url = get_image_url_from_api(api="https://svs.gsfc.nasa.gov/api/dialamoon", date=utc_date)
                        filepath = get_filepath(
                            download_dir=os.path.abspath(
                                os.path.join(os.environ.get("HOMEPATH"), "Downloads", "Moon Phases")
                            ),
                            date=date,
                            hour=user_hour
                        )
                        download_image(url=url, path=filepath)
                        downloaded += 1
                        print("Done.")
                except DateOutOfRangeError:
                    print(f"The date and time must be between 2011-01-01 00:00 UTC and {datetime.now().year}-12-31 23:00 UTC.")
                except requests.exceptions.SSLError:
                    sys.exit("SSL certificate verify failed!")
                except requests.exceptions.ConnectionError:
                    sys.exit("API did not respond! Check API URL or network connection!")
                except requests.exceptions.ChunkedEncodingError or urllib3.exceptions.ProtocolError:
                    sys.exit("Connection aborted! Check your network connection!")
                except Exception as error:
                    sys.exit(error)
                finally:
                    print(f"{downloaded} files downloaded!")
            break
    except KeyboardInterrupt:
        sys.exit("The program has been stopped by user.")
