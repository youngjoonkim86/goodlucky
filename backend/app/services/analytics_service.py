"""
분석 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date
import numpy as np
from collections import Counter

from app.models.lotto import LottoDraw
from app.models.weather import WeatherFeature
from app.models.economic import EconomicFeature


class AnalyticsService:
    """분석 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_number_frequency(self, limit: int = 45) -> dict:
        """번호별 출현 빈도 분석"""
        draws = self.db.query(LottoDraw).all()
        
        all_numbers = []
        for draw in draws:
            all_numbers.extend(draw.numbers)
        
        frequency = Counter(all_numbers)
        result = {}
        for num in range(1, 46):
            result[num] = {
                "number": num,
                "count": frequency.get(num, 0),
                "frequency": frequency.get(num, 0) / len(draws) if draws else 0
            }
        
        # 빈도순 정렬
        sorted_result = sorted(
            result.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]
        
        return {
            "total_draws": len(draws),
            "frequency": {str(k): v for k, v in sorted_result}
        }
    
    def analyze_patterns(self) -> dict:
        """패턴 분석"""
        draws = self.db.query(LottoDraw).order_by(LottoDraw.draw_no).all()
        
        if not draws:
            return {"error": "데이터가 없습니다."}
        
        patterns = {
            "consecutive_numbers": 0,  # 연속 번호
            "odd_even_ratio": [],  # 홀짝 비율
            "sum_range": [],  # 합계 범위
            "high_low_ratio": []  # 고저 비율
        }
        
        for draw in draws:
            numbers = sorted(draw.numbers)
            
            # 연속 번호 체크
            consecutive = False
            for i in range(len(numbers) - 1):
                if numbers[i+1] - numbers[i] == 1:
                    consecutive = True
                    break
            if consecutive:
                patterns["consecutive_numbers"] += 1
            
            # 홀짝 비율
            odd_count = sum(1 for n in numbers if n % 2 == 1)
            patterns["odd_even_ratio"].append({
                "draw_no": draw.draw_no,
                "odd": odd_count,
                "even": 6 - odd_count
            })
            
            # 합계 범위
            total_sum = sum(numbers)
            patterns["sum_range"].append({
                "draw_no": draw.draw_no,
                "sum": total_sum
            })
            
            # 고저 비율 (1-22: 저, 23-45: 고)
            low_count = sum(1 for n in numbers if n <= 22)
            patterns["high_low_ratio"].append({
                "draw_no": draw.draw_no,
                "low": low_count,
                "high": 6 - low_count
            })
        
        # 통계 계산
        return {
            "total_draws": len(draws),
            "consecutive_frequency": patterns["consecutive_numbers"] / len(draws),
            "avg_odd_count": np.mean([r["odd"] for r in patterns["odd_even_ratio"]]),
            "avg_sum": np.mean([r["sum"] for r in patterns["sum_range"]]),
            "sum_range": {
                "min": min(r["sum"] for r in patterns["sum_range"]),
                "max": max(r["sum"] for r in patterns["sum_range"])
            },
            "avg_low_count": np.mean([r["low"] for r in patterns["high_low_ratio"]]),
            "recent_patterns": {
                "odd_even": patterns["odd_even_ratio"][-10:],
                "sum": patterns["sum_range"][-10:],
                "high_low": patterns["high_low_ratio"][-10:]
            }
        }
    
    def analyze_variables(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """환경변수별 영향도 분석"""
        # 날짜 범위가 없으면 최근 1년 데이터 사용
        if not start_date or not end_date:
            from datetime import datetime, timedelta
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
        
        # 로또 데이터
        lotto_query = self.db.query(LottoDraw).filter(
            LottoDraw.draw_date >= start_date,
            LottoDraw.draw_date <= end_date
        )
        lotto_draws = lotto_query.all()
        
        # 기상 데이터
        weather_query = self.db.query(WeatherFeature).filter(
            WeatherFeature.date >= start_date,
            WeatherFeature.date <= end_date
        )
        weather_data = weather_query.all()
        
        # 경제 데이터
        economic_query = self.db.query(EconomicFeature).filter(
            EconomicFeature.date >= start_date,
            EconomicFeature.date <= end_date
        )
        economic_data = economic_query.all()
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data_counts": {
                "lotto_draws": len(lotto_draws),
                "weather_records": len(weather_data),
                "economic_records": len(economic_data)
            },
            "weather_analysis": {
                "avg_temp": np.mean([w.temp_avg for w in weather_data if w.temp_avg]) if weather_data else None,
                "avg_humidity": np.mean([w.humidity for w in weather_data if w.humidity]) if weather_data else None,
                "avg_precipitation": np.mean([w.precipitation for w in weather_data if w.precipitation]) if weather_data else None
            },
            "economic_analysis": {
                "avg_kospi": np.mean([e.kospi_index for e in economic_data if e.kospi_index]) if economic_data else None,
                "avg_exchange_rate": np.mean([e.exchange_rate_usd for e in economic_data if e.exchange_rate_usd]) if economic_data else None
            }
        }
    
    def analyze_correlation(self) -> dict:
        """환경변수와 번호 간 상관관계 분석"""
        # 간단한 상관관계 분석 예시
        # 실제로는 더 정교한 통계 분석이 필요
        draws = self.db.query(LottoDraw).all()
        
        if not draws:
            return {"error": "데이터가 없습니다."}
        
        # 번호별 평균 합계 계산
        number_sums = {}
        for draw in draws:
            for num in draw.numbers:
                if num not in number_sums:
                    number_sums[num] = []
                number_sums[num].append(sum(draw.numbers))
        
        avg_sums = {num: np.mean(sums) for num, sums in number_sums.items()}
        
        return {
            "number_avg_sum": avg_sums,
            "note": "환경변수와의 상관관계 분석은 더 많은 데이터와 정교한 통계 분석이 필요합니다."
        }

