import asyncio
import logging

import httpx

# 모듈 전용 로거 생성 (LOG015 해결)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# API URL 정의
WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.56658&longitude=126.9780"
    "&hourly=temperature_2m,precipitation_probability"
    "&forecast_days=3&timezone=Asia/Seoul"
)
COUNTRY_URL = "https://countries.dev/alpha/KOR"
IP_URL = "http://ip-api.com/json/8.8.8.8"


async def fetch_data(client: httpx.AsyncClient, url: str, name: str) -> dict | None:
    """개별 API 호출을 담당하는 비동기 함수"""
    try:
        logger.info(f"[{name}] 데이터 수집 시작...")
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        
        logger.info(f"[{name}] 데이터 수집 성공!")
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"[{name}] HTTP 에러 발생: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"[{name}] 요청 에러 발생: {e}")
    except httpx.HTTPError as e:  # BLE001 해결: Exception 대신 httpx 상위 에러 지정
        logger.error(f"[{name}] 알 수 없는 네트워크 에러 발생: {e}")
    
    return None


async def collect_all_data() -> dict:
    """asyncio.gather()를 활용하여 3개 API 동시 수집"""
    async with httpx.AsyncClient() as client:
        weather_task = fetch_data(client, WEATHER_URL, "Open-Meteo")
        country_task = fetch_data(client, COUNTRY_URL, "Countries.dev")
        ip_task = fetch_data(client, IP_URL, "ip-api")

        weather_res, country_res, ip_res = await asyncio.gather(
            weather_task,
            country_task,
            ip_task
        )

        return {
            "weather": weather_res,
            "country": country_res,
            "ip": ip_res
        }


if __name__ == "__main__":
    results = asyncio.run(collect_all_data())
    print("\n=== 수집 결과 요약 ===")
    print("1. Weather 수집 여부:", "성공" if results["weather"] else "실패")
    print("2. Country 수집 여부:", "성공" if results["country"] else "실패")
    print("3. IP 수집 여부:", "성공" if results["ip"] else "실패")