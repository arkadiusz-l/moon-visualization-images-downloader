from os import path, environ
from main import get_filepath, get_image_url_from_api, get_date_in_utc


def test_get_today_date_in_utc():
    date = "t"
    assert get_date_in_utc(date) == str(datetime.now().date())


def test_get_filepath_one_digit_hour():
    homepath = environ.get("HOMEPATH")
    date = "2024-04-08"
    hour = "1"
    filepath = get_filepath(homepath, date, hour)
    assert filepath == f"{homepath}\\2024-04-08T01L.jpg"


def test_get_filepath_two_digit_hour():
    homepath = environ.get("HOMEPATH")
    date = "2024-04-08"
    hour = "16"
    filepath = get_filepath(homepath, date, hour)
    assert filepath == f"{homepath}\\2024-04-08T16L.jpg"

# def test_get_image_url_from_api():
#     api = "https://svs.gsfc.nasa.gov/api/dialamoon"
#     today = "2024-04-08"
#     hour = "16"
#     image_url = get_image_url_from_api(api=api, date=today, time=hour)
#     assert image_url == "https://svs.gsfc.nasa.gov/api/dialamoon/2024-04-08T01:00"
