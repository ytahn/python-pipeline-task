import asyncio
import os
import time

import pandas as pd

from collector import collect_all_data
from models import validate_collected_data


def prepare_dataframe(validated_data: dict) -> pd.DataFrame:
    """
    검증 완료된 Pydantic 모델 데이터를 Pandas DataFrame으로 변환
    (여기서는 Open-Meteo 시간대별 날씨 데이터를 대표 표 형태로 구조화)
    """
    weather_model = validated_data.get("weather")
    if not weather_model:
        raise ValueError("Weather 데이터가 정상적으로 검증되지 않았습니다.")

    # Pydantic 모델에서 hourly 데이터 추출
    hourly = weather_model.hourly
    
    df = pd.DataFrame({
        "time": hourly.time,
        "temperature_2m": hourly.temperature_2m,
        "precipitation_probability": hourly.precipitation_probability,
        "latitude": weather_model.latitude,
        "longitude": weather_model.longitude,
        "timezone": weather_model.timezone
    })
    return df


def benchmark_storage(df: pd.DataFrame, csv_path: str = "output.csv", parquet_path: str = "output.parquet"):
    """
    CSV와 Parquet 각각의 쓰기/읽기 소요 시간 및 파일 크기를 비교 측정
    """
    results = {}

    # 1. CSV 저장 및 읽기 성능 측정
    start_time = time.perf_counter()
    df.to_csv(csv_path, index=False)
    csv_write_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    _ = pd.read_csv(csv_path)
    csv_read_time = time.perf_counter() - start_time

    csv_size_kb = os.path.getsize(csv_path) / 1024

    # 2. Parquet 저장 및 읽기 성능 측정
    start_time = time.perf_counter()
    df.to_parquet(parquet_path, index=False)
    parquet_write_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    _ = pd.read_parquet(parquet_path)
    parquet_read_time = time.perf_counter() - start_time

    parquet_size_kb = os.path.getsize(parquet_path) / 1024

    # 결과 정리
    results["CSV"] = {
        "write_time_ms": csv_write_time * 1000,
        "read_time_ms": csv_read_time * 1000,
        "size_kb": csv_size_kb
    }
    results["Parquet"] = {
        "write_time_ms": parquet_write_time * 1000,
        "read_time_ms": parquet_read_time * 1000,
        "size_kb": parquet_size_kb
    }

    return results


def print_performance_summary(metrics: dict):
    """
    성능 측정 결과를 정리하여 터미널 표 형태로 출력
    """
    print("\n" + "=" * 55)
    print("📊 [성능 비교 측정 결과: CSV vs Parquet]")
    print("=" * 55)
    print(f"{'Format':<10} | {'Write Time (ms)':<16} | {'Read Time (ms)':<16} | {'File Size (KB)':<12}")
    print("-" * 55)
    for fmt, data in metrics.items():
        print(
            f"{fmt:<10} | "
            f"{data['write_time_ms']:>14.3f} ms | "
            f"{data['read_time_ms']:>14.3f} ms | "
            f"{data['size_kb']:>10.2f} KB"
        )
    print("=" * 55)


def main():
    print("1. 비동기 데이터 수집 진행 중...")
    raw_data = asyncio.run(collect_all_data())

    print("2. Pydantic v2 스키마 검증 진행 중...")
    validated_data = validate_collected_data(raw_data)

    print("3. DataFrame 변환 및 저장/성능 측정 시작...")
    df = prepare_dataframe(validated_data)
    metrics = benchmark_storage(df)

    print_performance_summary(metrics)


if __name__ == "__main__":
    main()