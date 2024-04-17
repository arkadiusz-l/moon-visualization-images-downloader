from os import path, environ
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import pytest

from main import (get_hour_from_user, get_filepath, get_image_url_from_api, parse_user_date,
                  convert_user_date_and_hour_to_utc, get_image_url_from_api, HourValueError, DateOutOfRangeError)


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_requests_get:
        yield mock_requests_get


def test_get_image_url_from_api(mock_requests_get):
    mock_response = mock_requests_get.return_value
    mock_response.content = b'{"image_highres": {"url": "https://example.com/image.tif"}}'
    api = "https://api.example.com"
    date = "2024-02-01T04"
    expected_image_url = "https://example.com/image.tif"
    assert get_image_url_from_api(api, date) == expected_image_url
    mock_requests_get.assert_called_once_with("https://api.example.com/2024-02-01T04:00")


def test_get_hour_from_user_valid():
    with patch("builtins.input", return_value="15"):
        hour = get_hour_from_user("15")
        assert 0 <= hour <= 23


def test_get_hour_from_user_invalid():
    with patch("builtins.input", return_value="24"):
        with pytest.raises(HourValueError):
            get_hour_from_user("24")


def test_parse_user_date_today():
    assert parse_user_date("t") == str(datetime.now().date())


def test_parse_user_date_tomorrow():
    assert parse_user_date("tm") == str(datetime.now().date() + timedelta(days=1))


def test_parse_date_plus_one():
    assert parse_user_date("+1") == str(datetime.now().date() + timedelta(days=1))


def test_parse_date_plus_two():
    assert parse_user_date("+2") == str(datetime.now().date() + timedelta(days=2))


def test_parse_user_date_valid_date():
    assert parse_user_date("2024-01-31") == "2024-01-31"


def test_parse_user_date_invalid_date():
    with pytest.raises(ValueError):
        parse_user_date("31-01-2024")


def test_parse_user_date_invalid_value():
    with pytest.raises(ValueError):
        parse_user_date("something")


def test_get_filepath_one_digit_hour():
    homepath = environ.get("HOMEPATH")
    date = "2024-04-08"
    hour = "1"
    filepath = get_filepath(homepath, date, hour)
    assert filepath == f"{homepath}\\2024-04-08T01L.tif"


def test_get_filepath_two_digit_hour():
    homepath = environ.get("HOMEPATH")
    date = "2024-04-08"
    hour = "16"
    filepath = get_filepath(homepath, date, hour)
    assert filepath == f"{homepath}\\2024-04-08T16L.tif"


def test_convert_user_date_and_hour_to_utc_warsaw_winter_time():
    date = "2024-02-01"
    hour = "05"
    assert convert_user_date_and_hour_to_utc(date, hour) == "2024-02-01T04"


def test_convert_user_date_and_hour_to_utc_warsaw_summer_time():
    assert convert_user_date_and_hour_to_utc("2024-04-01", "05") == "2024-04-01T03"


def test_convert_user_date_and_hour_to_utc_one_digit_hour_warsaw_summer_time():
    assert convert_user_date_and_hour_to_utc("2024-04-01", "5") == "2024-04-01T03"


def test_convert_user_date_and_hour_to_utc_warsaw_winter_time_midnight():
    assert convert_user_date_and_hour_to_utc("2024-03-01", "00") == "2024-02-29T23"


def test_convert_user_date_and_hour_to_utc_invalid_date():
    with pytest.raises(ValueError):
        convert_user_date_and_hour_to_utc("2024-13-01", "05")


def test_convert_user_date_and_hour_date_lower_than_range():
    with pytest.raises(DateOutOfRangeError):
        convert_user_date_and_hour_to_utc("2010-12-31", "23")


def test_convert_user_date_and_hour_date_greater_than_range():
    with pytest.raises(DateOutOfRangeError):
        next_year = str(datetime.now().year + 1)
        convert_user_date_and_hour_to_utc(f"{next_year}-01-01", "01")
