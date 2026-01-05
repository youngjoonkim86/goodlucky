"""
데이터 수집 및 저장 관리자
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from typing import List, Optional
from loguru import logger
import os

from scrapers.lotto_scraper import LottoScraper
from scrapers.weather_scraper import WeatherScraper
from scrapers.economic_scraper import EconomicScraper


class DataCollector:
    """데이터 수집 및 저장 관리자"""
    
    def __init__(self):
        # PostgreSQL 연결
        postgres_user = os.getenv("POSTGRES_USER", "lotto_user")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "lotto_password")
        postgres_db = os.getenv("POSTGRES_DB", "lotto_db")
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        
        database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # 스크래퍼 초기화
        self.lotto_scraper = LottoScraper()
        self.weather_scraper = WeatherScraper()
        self.economic_scraper = EconomicScraper()
    
    def collect_lotto_data(self, start_draw_no: Optional[int] = None, end_draw_no: Optional[int] = None):
        """로또 데이터 수집 및 저장"""
        db = self.SessionLocal()
        try:
            # 기존 최대 회차 조회
            from sqlalchemy import text
            result = db.execute(text("SELECT MAX(draw_no) FROM lotto_draws"))
            max_draw_no = result.scalar() or 0
            
            if start_draw_no is None:
                start_draw_no = max_draw_no + 1
            
            if end_draw_no is None:
                end_draw_no = self.lotto_scraper.get_latest_draw_no() or start_draw_no
            
            logger.info(f"로또 데이터 수집: 회차 {start_draw_no} ~ {end_draw_no}")
            
            draws = self.lotto_scraper.get_all_draws(start_draw_no, end_draw_no)
            
            for draw_data in draws:
                # 중복 확인
                from sqlalchemy import text
                result = db.execute(
                    text("SELECT id FROM lotto_draws WHERE draw_no = :draw_no"),
                    {"draw_no": draw_data["draw_no"]}
                )
                if result.scalar():
                    logger.debug(f"회차 {draw_data['draw_no']} 이미 존재, 건너뜀")
                    continue
                
                # 데이터 삽입
                db.execute(
                    text("""
                        INSERT INTO lotto_draws 
                        (draw_no, draw_date, numbers, bonus, first_prize_winners, first_prize_amount, total_sales, extra_metadata)
                        VALUES (:draw_no, :draw_date, :numbers, :bonus, :first_prize_winners, :first_prize_amount, :total_sales, :extra_metadata)
                    """),
                    {
                        "draw_no": draw_data["draw_no"],
                        "draw_date": draw_data["draw_date"],
                        "numbers": draw_data["numbers"],
                        "bonus": draw_data["bonus"],
                        "first_prize_winners": draw_data.get("first_prize_winners", 0),
                        "first_prize_amount": draw_data.get("first_prize_amount", 0),
                        "total_sales": draw_data.get("total_sales", 0),
                        "extra_metadata": str(draw_data.get("metadata", {}))
                    }
                )
                logger.info(f"회차 {draw_data['draw_no']} 데이터 저장 완료")
            
            db.commit()
            logger.info(f"{len(draws)}개 회차 데이터 수집 및 저장 완료")
        except Exception as e:
            db.rollback()
            logger.error(f"로또 데이터 수집 실패: {e}")
            raise
        finally:
            db.close()
    
    def collect_weather_data(self, target_date: date):
        """기상 데이터 수집 및 저장"""
        db = self.SessionLocal()
        try:
            weather_data = self.weather_scraper.get_weather_data(target_date)
            
            if not weather_data:
                logger.warning(f"{target_date} 기상 데이터 없음")
                return
            
            # 중복 확인
            from sqlalchemy import text
            result = db.execute(
                text("SELECT id FROM weather_features WHERE date = :date"),
                {"date": target_date}
            )
            if result.scalar():
                logger.debug(f"{target_date} 기상 데이터 이미 존재, 건너뜀")
                return
            
            # 데이터 삽입
            db.execute(
                text("""
                    INSERT INTO weather_features 
                    (date, temp_max, temp_min, temp_avg, humidity, precipitation, wind_speed, weather_main, weather_description)
                    VALUES (:date, :temp_max, :temp_min, :temp_avg, :humidity, :precipitation, :wind_speed, :weather_main, :weather_description)
                """),
                {
                    "date": target_date,
                    "temp_max": weather_data.get("temp_max"),
                    "temp_min": weather_data.get("temp_min"),
                    "temp_avg": weather_data.get("temp_avg"),
                    "humidity": weather_data.get("humidity"),
                    "precipitation": weather_data.get("precipitation"),
                    "wind_speed": weather_data.get("wind_speed"),
                    "weather_main": weather_data.get("weather_main"),
                    "weather_description": weather_data.get("weather_description")
                }
            )
            
            db.commit()
            logger.info(f"{target_date} 기상 데이터 저장 완료")
        except Exception as e:
            db.rollback()
            logger.error(f"기상 데이터 수집 실패: {e}")
            raise
        finally:
            db.close()
    
    def collect_economic_data(self, target_date: date):
        """경제 지표 데이터 수집 및 저장"""
        db = self.SessionLocal()
        try:
            economic_data = self.economic_scraper.get_economic_data(target_date)
            
            if not economic_data:
                logger.warning(f"{target_date} 경제 지표 데이터 없음")
                return
            
            # 중복 확인
            from sqlalchemy import text
            result = db.execute(
                text("SELECT id FROM economic_features WHERE date = :date"),
                {"date": target_date}
            )
            if result.scalar():
                logger.debug(f"{target_date} 경제 지표 데이터 이미 존재, 건너뜀")
                return
            
            # 데이터 삽입
            db.execute(
                text("""
                    INSERT INTO economic_features 
                    (date, exchange_rate_usd, exchange_rate_eur, kospi_index, kosdaq_index, interest_rate, cpi, pmi, unemployment_rate)
                    VALUES (:date, :exchange_rate_usd, :exchange_rate_eur, :kospi_index, :kosdaq_index, :interest_rate, :cpi, :pmi, :unemployment_rate)
                """),
                {
                    "date": target_date,
                    "exchange_rate_usd": economic_data.get("exchange_rate_usd"),
                    "exchange_rate_eur": economic_data.get("exchange_rate_eur"),
                    "kospi_index": economic_data.get("kospi_index"),
                    "kosdaq_index": economic_data.get("kosdaq_index"),
                    "interest_rate": economic_data.get("interest_rate"),
                    "cpi": economic_data.get("cpi"),
                    "pmi": economic_data.get("pmi"),
                    "unemployment_rate": economic_data.get("unemployment_rate")
                }
            )
            
            db.commit()
            logger.info(f"{target_date} 경제 지표 데이터 저장 완료")
        except Exception as e:
            db.rollback()
            logger.error(f"경제 지표 데이터 수집 실패: {e}")
            raise
        finally:
            db.close()

