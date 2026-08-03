import asyncio

from pydantic import BaseModel, Field, ValidationError

from collector import collect_all_data


# 1. 날씨 데이터 모델 (Open-Meteo)
class HourlyData(BaseModel):
    time: list[str]
    temperature_2m: list[float]
    precipitation_probability: list[int | None]


class WeatherData(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="위도 (-90 ~ 90)")
    longitude: float = Field(..., ge=-180, le=180, description="경도 (-180 ~ 180)")
    timezone: str
    hourly: HourlyData


# 2. 국가 정보 모델
class CountryData(BaseModel):
    name: str
    alpha2Code: str
    alpha3Code: str


# 3. IP 정보 모델
class IPData(BaseModel):
    status: str
    country: str
    regionName: str
    city: str
    query: str


def validate_collected_data(raw_data: dict) -> dict:
    """수집된 raw dict 데이터를 Pydantic v2 모델로 검증 및 파싱"""
    validated_results = {}

    if raw_data.get("weather"):
        try:
            validated_results["weather"] = WeatherData(**raw_data["weather"])
        except ValidationError as e:
            print(f"[ValidationError] Weather 데이터 스키마 오류:\n{e}")

    if raw_data.get("country"):
        try:
            country_payload = raw_data["country"]
            if isinstance(country_payload, list):
                country_payload = country_payload[0]
            validated_results["country"] = CountryData(**country_payload)
        except ValidationError as e:
            print(f"[ValidationError] Country 데이터 스키마 오류:\n{e}")

    if raw_data.get("ip"):
        try:
            validated_results["ip"] = IPData(**raw_data["ip"])
        except ValidationError as e:
            print(f"[ValidationError] IP 데이터 스키마 오류:\n{e}")

    return validated_results


if __name__ == "__main__":
    raw = asyncio.run(collect_all_data())
    validated = validate_collected_data(raw)
    
    print("\n=== 스키마 검증 완료 결과 ===")
    for key, model_obj in validated.items():
        print(f"[{key}] 검증 성공 -> {type(model_obj).__name__} 객체 생성 완료")