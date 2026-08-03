import pytest
from pydantic import ValidationError
from models import CountryData, WeatherData


def test_weather_data_validation_success():
    """정상적인 입력 데이터 전달 시 WeatherData 스키마 검증을 통과하는지 테스트"""
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
    """위도 범위를 벗어난 잘못된 데이터(150.0) 입력 시 ValidationError 예외가 정상 발생 하는지 테스트"""
    invalid_payload = {
        "latitude": 150.0,  # 위도 허용 범위를 넘는 값
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
    """국가 정보 데이터(CountryData) 스키마 검증 테스트"""
    payload = {
        "name": "Korea (Republic of)",
        "alpha2Code": "KR",
        "alpha3Code": "KOR"
    }
    country = CountryData(**payload)
    assert country.alpha3Code == "KOR"