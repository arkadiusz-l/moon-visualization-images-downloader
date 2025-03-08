import os
import sys
import json
import logging
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageOps
import urllib3
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
        logging.debug(f"{image_length=} bytes")
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


def create_filepath(download_dir: str, extension: str, date: str, hour: str) -> str:
    filename = f"{date}T0{hour}L.{extension}" if len(hour) < 2 else f"{date}T{hour}L.{extension}"
    filepath = os.path.join(download_dir, filename)
    logging.debug(f"{filepath=}")
    return filepath


def get_date_from_user() -> str:
    while True:
        try:
            date = input(
                "Enter the date for which I should download images.\n"
                "You can enter YYYY-MM-DD or 't' for today, 'tm' for tommorow.\n"
                "You can also enter '+1' for tommorow, '+2' for the day after tommorow, etc: "
            )
            date = parse_user_date(date)
        except ValueError:
            print("\nThe date is not valid! Please enter a valid date.\n")
            continue
        print(f"\nYou selected the date: {date}")
        return date


def get_hours_from_user() -> tuple[int, int]:
    hour_value_error_message = "\nPlease enter a value between 0 and 23.\n"
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
            print("\nThe hour of the first Moon visualization image should be earlier then the last one.\n")
            continue
        return user_start_hour, user_end_hour


def download_images() -> int:
    downloaded = 0
    try:
        for user_hour in range(user_start_hour, user_end_hour + 1):
            user_hour = str(user_hour)
            utc_date = convert_user_date_and_hour_to_utc(date=date, hour=user_hour)
            url = get_image_url_from_api(api="https://svs.gsfc.nasa.gov/api/dialamoon", date=utc_date)
            filepath = create_filepath(
                download_dir=os.path.abspath(
                    os.path.join(os.environ.get("HOMEPATH"), "Downloads", "Moon Visualizations")
                ),
                extension="tif",
                date=date,
                hour=user_hour
            )
            download_image(url=url, path=filepath)
            downloaded += 1
    except DateOutOfRangeError:
        print(f"The date and time must be between 2011-01-01 00:00 UTC and {datetime.now().year}-12-31 23:00 UTC.")
    except requests.exceptions.SSLError:
        sys.exit("SSL certificate verify failed!")
    except requests.exceptions.ConnectionError:
        sys.exit("API did not respond! Check API URL or network connection!")
    except (requests.exceptions.ChunkedEncodingError, urllib3.exceptions.ProtocolError):
        sys.exit("Connection aborted! Check your network connection!")
    finally:
        print(f"{downloaded} files downloaded!")
        return downloaded


def crop_image(filename: str, crop_size: tuple[int, int]) -> Image:
    try:
        image_path = os.path.join(download_dir, filename)
        img = Image.open(image_path)
        img_width, img_height = img.size
        crop_width, crop_height = crop_size
        if img_width < crop_width or img_height < crop_height:
            print(f"Image {filename} is too small! ({img_width}x{img_height})")
            return
        left = (img_width - crop_width) // 2
        top = (img_height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height
        cropped_img = img.crop((left, top, right, bottom))
        converted_image = cropped_img.convert("RGB")
        output_filename = os.path.splitext(filename)[0] + ".jpg"
        converted_image.save(os.path.join(download_dir, output_filename), "JPEG")
        print(f"Saved cropped image: {output_filename}")
        return converted_image
    except Exception as error:
        print(f"An error occurred during cropping image {filename}: {error}")


def mirror_image(cropped_image: Image, filename: str) -> None:
    try:
        mirrored_img = ImageOps.mirror(cropped_image)
        output_filename = os.path.splitext(filename)[0] + "-m.jpg"
        mirrored_img.save(os.path.join(download_dir, output_filename))
        print(f"Saved mirrored image: {output_filename}")
    except Exception as error:
        print(f"An error occurred during mirroring image {filename}: {error}")


def process_images() -> None:
    try:
        images = [file for file in os.listdir(download_dir) if file.lower().endswith((".tif", ".tiff"))]
        for filename in images:
            cropped_image = crop_image(filename=filename, crop_size=(2900, 2900))
            if cropped_image:
                mirror_image(cropped_image=cropped_image, filename=filename)
    except Exception as error:
        print(f"An error occurred during processing images: {error}")


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
    download_dir = os.path.abspath(os.path.join(os.environ.get("HOMEPATH"), "Downloads", "Moon Visualizations"))

    try:
        date = get_date_from_user()
        user_start_hour, user_end_hour = get_hours_from_user()
        number_of_images = user_end_hour - user_start_hour + 1
        choice = input(f"{number_of_images} image(s) will be downloaded. Enter 'y' if continue: ")
        if choice == "y":
            download_images()
            print("Done.")
            os.startfile(download_dir)
        crop_choice = input("Would you like to crop and mirror images? ")
        if crop_choice == "y":
            process_images()
    except KeyboardInterrupt:
        sys.exit("The program has been stopped by user.")
