import asyncio
from pydantic import BaseModel, Field, ValidationError
from collector import collect_all_data


# --- 1. Open-Meteo 날씨 데이터 스키마 ---
class HourlyData(BaseModel):
    time: list[str]                            # 시간 목록
    temperature_2m: list[float]               # 시간대별 기온 목록
    precipitation_probability: list[int | None] # 강수확률 목록 (null 허용)


class WeatherData(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="위도 (-90~90)")
    longitude: float = Field(..., ge=-180, le=180, description="경도 (-180~180)")
    timezone: str
    hourly: HourlyData                         # 하위 중첩 모델 검증


# --- 2. Countries.dev 국가 정보 스키마 ---
class CountryData(BaseModel):
    name: str          # 국가명
    alpha2Code: str    # 2자리 국가 코드 (e.g. KR)
    alpha3Code: str    # 3자리 국가 코드 (e.g. KOR)


# --- 3. ip-api IP 정보 스키마 ---
class IPData(BaseModel):
    status: str        # 요청 상태 (success/fail)
    country: str       # 국가명
    regionName: str    # 지역/주 이름
    city: str          # 도시명
    query: str         # IP 주소


# --- 4. 데이터 통합 스키마 검증 함수 ---
def validate_collected_data(raw_data: dict) -> dict:
    """
    수집된 딕셔너리 데이터를 Pydantic 모델로 변환하여 타입 및 범위 검증
    """
    validated_results = {}

    # 날씨 데이터 검증
    if raw_data.get("weather"):
        try:
            validated_results["weather"] = WeatherData(**raw_data["weather"])
        except ValidationError as e:
            print(f"[ValidationError] Weather 데이터 스키마 오류:\n{e}")

    # 국가 정보 데이터 검증 (리스트 응답 시 첫 번째 요소 추출)
    if raw_data.get("country"):
        try:
            country_payload = raw_data["country"]
            if isinstance(country_payload, list):
                country_payload = country_payload[0]
            validated_results["country"] = CountryData(**country_payload)
        except ValidationError as e:
            print(f"[ValidationError] Country 데이터 스키마 오류:\n{e}")

    # IP 정보 데이터 검증
    if raw_data.get("ip"):
        try:
            validated_results["ip"] = IPData(**raw_data["ip"])
        except ValidationError as e:
            print(f"[ValidationError] IP 데이터 스키마 오류:\n{e}")

    return validated_results


if __name__ == "__main__":
    # 단독 실행 시 검증 로직 테스트
    raw = asyncio.run(collect_all_data())
    validated = validate_collected_data(raw)
    
    print("\n=== 스키마 검증 완료 결과 ===")
    for key, model_obj in validated.items():
        print(f"[{key}] 검증 성공 -> {type(model_obj).__name__} 객체 생성 완료")