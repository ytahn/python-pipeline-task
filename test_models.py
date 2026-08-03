import pytest
from pydantic import ValidationError

from models import CountryData, WeatherData


def test_weather_data_validation_success():
    valid_payload = {
        "latitude": 37.56658,
        "longitude": 126.9780,
        "timezone": "Asia/Seoul",
        "hourly": {
            "time": ["2026-08-03T00:00", "2026-08-03T01:00"],
            "temperature_2m": [25.4, 24.8],
            "precipitation_probability": [0, 10]
        }
    }
    data = WeatherData(**valid_payload)
    assert data.latitude == 37.56658
    assert len(data.hourly.temperature_2m) == 2


def test_weather_data_validation_out_of_bounds():
    invalid_payload = {
        "latitude": 150.0,
        "longitude": 126.9780,
        "timezone": "Asia/Seoul",
        "hourly": {
            "time": [],
            "temperature_2m": [],
            "precipitation_probability": []
        }
    }
    with pytest.raises(ValidationError):
        WeatherData(**invalid_payload)


def test_country_data_validation():
    payload = {
        "name": "Korea (Republic of)",
        "alpha2Code": "KR",
        "alpha3Code": "KOR"
    }
    country = CountryData(**payload)
    assert country.alpha3Code == "KOR"