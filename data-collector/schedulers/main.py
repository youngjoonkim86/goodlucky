"""
데이터 수집 스케줄러 메인
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from datetime import datetime, date
import time

from scrapers.lotto_scraper import LottoScraper
from scrapers.weather_scraper import WeatherScraper
from scrapers.economic_scraper import EconomicScraper
from collectors.data_collector import DataCollector


def collect_lotto_data():
    """로또 데이터 수집 작업"""
    logger.info("로또 데이터 수집 시작")
    try:
        collector = DataCollector()
        collector.collect_lotto_data()
        logger.info("로또 데이터 수집 완료")
    except Exception as e:
        logger.error(f"로또 데이터 수집 실패: {e}")


def collect_weather_data():
    """기상 데이터 수집 작업"""
    logger.info("기상 데이터 수집 시작")
    try:
        collector = DataCollector()
        collector.collect_weather_data(date.today())
        logger.info("기상 데이터 수집 완료")
    except Exception as e:
        logger.error(f"기상 데이터 수집 실패: {e}")


def collect_economic_data():
    """경제 지표 데이터 수집 작업"""
    logger.info("경제 지표 데이터 수집 시작")
    try:
        collector = DataCollector()
        collector.collect_economic_data(date.today())
        logger.info("경제 지표 데이터 수집 완료")
    except Exception as e:
        logger.error(f"경제 지표 데이터 수집 실패: {e}")


def main():
    """스케줄러 메인 함수"""
    logger.info("데이터 수집 스케줄러 시작")
    
    scheduler = BlockingScheduler()
    
    # 로또 데이터: 매주 토요일 오후 9시 (추첨 후)
    scheduler.add_job(
        collect_lotto_data,
        trigger=CronTrigger(day_of_week="sat", hour=21, minute=0),
        id="collect_lotto",
        name="로또 데이터 수집",
        replace_existing=True
    )
    
    # 기상 데이터: 매일 오전 9시
    scheduler.add_job(
        collect_weather_data,
        trigger=CronTrigger(hour=9, minute=0),
        id="collect_weather",
        name="기상 데이터 수집",
        replace_existing=True
    )
    
    # 경제 지표: 매일 오전 10시
    scheduler.add_job(
        collect_economic_data,
        trigger=CronTrigger(hour=10, minute=0),
        id="collect_economic",
        name="경제 지표 데이터 수집",
        replace_existing=True
    )
    
    # 초기 데이터 수집 (즉시 실행)
    logger.info("초기 데이터 수집 시작")
    try:
        collect_lotto_data()
        collect_weather_data()
        collect_economic_data()
    except Exception as e:
        logger.error(f"초기 데이터 수집 실패: {e}")
    
    logger.info("스케줄러 실행 중...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("스케줄러 종료")
        scheduler.shutdown()


if __name__ == "__main__":
    main()

