import asyncio
import logging
import httpx

# 로거 설정: 수집 진행 상황 및 에러 메시지 출력용
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 수집 대상 Open API URL 정의
WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.56658&longitude=126.9780"
    "&hourly=temperature_2m,precipitation_probability"
    "&forecast_days=3&timezone=Asia/Seoul"
)
COUNTRY_URL = "https://countries.dev/alpha/KOR"
IP_URL = "http://ip-api.com/json/8.8.8.8"


async def fetch_data(client: httpx.AsyncClient, url: str, name: str) -> dict | None:
    """
    단일 API URL에 비동기 GET 요청을 보내고 JSON 응답을 반환하는 함수
    """
    try:
        logger.info(f"[{name}] 데이터 수집 시작...")
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()  # 200 OK가 아닐 경우 HTTP 에러 발생
        
        logger.info(f"[{name}] 데이터 수집 성공!")
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"[{name}] HTTP 상태 에러 발생 (코드: {e.response.status_code})")
    except httpx.RequestError as e:
        logger.error(f"[{name}] 네트워크 요청 실패: {e}")
    except httpx.HTTPError as e:
        logger.error(f"[{name}] 기타 HTTP 관련 에러: {e}")
    
    return None


async def collect_all_data() -> dict:
    """
    asyncio.gather()를 사용하여 3개의 API를 동시에(병렬) 수집하는 메인 함수
    """
    async with httpx.AsyncClient() as client:
        # 비동기 수집 태스크 생성
        weather_task = fetch_data(client, WEATHER_URL, "Open-Meteo")
        country_task = fetch_data(client, COUNTRY_URL, "Countries.dev")
        ip_task = fetch_data(client, IP_URL, "ip-api")

        # 3개 API 요청을 동시에 병렬 처리 및 결과 동시 수령
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
    # 단독 실행 시 수집 테스트
    results = asyncio.run(collect_all_data())
    print("\n=== 수집 결과 요약 ===")
    print("1. Weather 수집 여부:", "성공" if results["weather"] else "실패")
    print("2. Country 수집 여부:", "성공" if results["country"] else "실패")
    print("3. IP 수집 여부:", "성공" if results["ip"] else "실패")