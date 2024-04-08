import json
import urllib.request
from datetime import datetime
import logging


def get_actual_date_in_utc() -> str:
    date = datetime.now()
    date = date.strftime("%Y-%m-%d")
    logging.debug(f"{date=}")
    return date


def get_image_url_from_api(api: str, date: str, time: str) -> str:
    """od 14:00 do 14:29 pobiera zdjecie dla godziny 14, a od 14:30 do 14:59 pobiera dla godziny 15"""
    # if time == "0":
    #     time = "00"
    # if time == "1":
    #     time = "01"
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


def download_image(url: str, filename: str):
    urllib.request.urlretrieve(url, filename)
    print(f"The image has been saved as '{filename}'.")


class HoursError(Exception):
    pass


# hours = {
#     0: "00",
#     1: "01",
#     2: "02",
#     3: "03",
#     4: "04",
#     5: "05",
#     6: "06",
#     7: "07",
#     8: "08",
#     9: "09",
#     10: "10",
#     11: "11",
#     12: "12"
# }

def set_filename(date: str, time: str):
    return f"{today}T0{hour}L.jpg" if len(str(hour)) < 2 else f"{today}T{hour}L.jpg"  # T zeby odroznic date od czasu a L oznacza Local - czas lokalny (nie UTC)
    # return f"{today}T{hour}L.tif"  # T zeby odroznic date od czasu a L oznacza Local - czas lokalny (nie UTC)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    while True:
        try:
            start = int(input("The hour of the first Moon visualization image (00-23): "))
            end = int(input("The hour of the last Moon visualization image (00-23): "))
            if start > end:
                raise HoursError

            today = get_actual_date_in_utc()

            for hour in range(start, end + 1):
                image_url = get_image_url_from_api(api="https://svs.gsfc.nasa.gov/api/dialamoon", date=today, time=str(hour))
                filename = set_filename(date=today, time=str(hour))
                download_image(url=image_url, filename=filename)
            break
        except ValueError:
            print("Please enter a value between 00 and 23.")
        except HoursError:
            print("The hour of the first Moon visualization image should be earlier then the last.")
        except urllib.error.HTTPError:
            print("Endpoint not found!")
        except KeyboardInterrupt:
            print("Program stopped by user.")
            exit()
    print("Done.")
