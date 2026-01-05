"""
추천 엔진
"""
from sqlalchemy.orm import Session
from typing import List, Tuple, Dict
import random
import numpy as np
from collections import Counter
from datetime import datetime, timedelta

from app.models.lotto import LottoDraw
from app.models.weather import WeatherFeature
from app.models.economic import EconomicFeature


class RecommendationEngine:
    """추천 엔진"""
    
    def __init__(self, db: Session):
        self.db = db
        self._load_data()
    
    def _load_data(self):
        """데이터 로드 및 전처리"""
        self.draws = self.db.query(LottoDraw).order_by(LottoDraw.draw_no).all()
        
        # 번호별 출현 빈도 계산
        all_numbers = []
        for draw in self.draws:
            all_numbers.extend(draw.numbers)
        
        self.number_frequency = Counter(all_numbers)
        self.total_draws = len(self.draws)
        
        # 정규화된 빈도 (0~1)
        max_freq = max(self.number_frequency.values()) if self.number_frequency else 1
        self.normalized_frequency = {
            num: self.number_frequency.get(num, 0) / max_freq
            for num in range(1, 46)
        }
    
    def generate_numbers(
        self,
        include_weather: bool = True,
        include_economic: bool = True
    ) -> Tuple[List[int], float, Dict[str, float]]:
        """
        추천 번호 생성
        
        Returns:
            (numbers, confidence, features)
        """
        if not self.draws:
            # 데이터가 없으면 랜덤 생성
            numbers = sorted(random.sample(range(1, 46), 6))
            return numbers, 0.5, {
                "frequency_score": 0.5,
                "pattern_score": 0.5,
                "weather_idx": 0.5,
                "economic_idx": 0.5,
                "sum_score": 0.5,
                "odd_even_score": 0.5
            }
        
        # 전략 1: 빈도 기반 가중치 샘플링
        available = list(range(1, 46))
        selected = []
        
        for _ in range(6):
            if not available:
                break
            
            # 현재 사용 가능한 번호에 대한 가중치 계산
            available_weights = [self.normalized_frequency.get(num, 0.1) for num in available]
            available_weights = np.array(available_weights)
            
            # 가중치를 확률로 변환
            if available_weights.sum() > 0:
                available_weights = available_weights / available_weights.sum()
            else:
                available_weights = np.ones(len(available)) / len(available)
            
            # 가중치 기반으로 번호 선택
            idx = np.random.choice(len(available), p=available_weights)
            num = available.pop(idx)
            selected.append(num)
        
        numbers = sorted(selected)
        
        # 신뢰도 및 특성 계산
        confidence, features = self._calculate_confidence_and_features(
            numbers,
            include_weather,
            include_economic
        )
        
        return numbers, confidence, features
    
    def calculate_confidence(
        self,
        numbers: List[int]
    ) -> Tuple[float, Dict[str, float]]:
        """특정 번호 조합의 신뢰도 계산"""
        return self._calculate_confidence_and_features(numbers, True, True)
    
    def _calculate_confidence_and_features(
        self,
        numbers: List[int],
        include_weather: bool,
        include_economic: bool
    ) -> Tuple[float, Dict[str, float]]:
        """신뢰도 및 특성 계산"""
        features = {}
        
        # 1. 빈도 점수
        freq_scores = [self.normalized_frequency.get(num, 0.1) for num in numbers]
        features["frequency_score"] = np.mean(freq_scores)
        
        # 2. 패턴 점수
        features["pattern_score"] = self._calculate_pattern_score(numbers)
        
        # 3. 기상 지수
        if include_weather:
            features["weather_idx"] = self._calculate_weather_index()
        else:
            features["weather_idx"] = 0.0
        
        # 4. 경제 지수
        if include_economic:
            features["economic_idx"] = self._calculate_economic_index()
        else:
            features["economic_idx"] = 0.0
        
        # 5. 합계 점수 (역대 평균 합계와의 유사도)
        total_sum = sum(numbers)
        avg_sum = np.mean([sum(draw.numbers) for draw in self.draws]) if self.draws else 150
        sum_diff = abs(total_sum - avg_sum)
        features["sum_score"] = max(0, 1 - (sum_diff / 100))  # 차이가 작을수록 높은 점수
        
        # 6. 홀짝 비율 점수
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        ideal_odd = 3  # 이상적인 홀수 개수
        features["odd_even_score"] = 1 - abs(odd_count - ideal_odd) / 3
        
        # 최종 신뢰도 계산 (가중 평균)
        weights = {
            "frequency_score": 0.3,
            "pattern_score": 0.2,
            "weather_idx": 0.15,
            "economic_idx": 0.15,
            "sum_score": 0.1,
            "odd_even_score": 0.1
        }
        
        confidence = sum(
            features.get(key, 0) * weight
            for key, weight in weights.items()
        )
        
        # 신뢰도를 0~1 범위로 정규화
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence, features
    
    def _calculate_pattern_score(self, numbers: List[int]) -> float:
        """패턴 점수 계산"""
        if not self.draws:
            return 0.5
        
        # 연속 번호 체크
        sorted_nums = sorted(numbers)
        consecutive = any(sorted_nums[i+1] - sorted_nums[i] == 1 for i in range(len(sorted_nums)-1))
        
        # 역대 패턴과 비교
        pattern_matches = 0
        for draw in self.draws[-50:]:  # 최근 50회차만 확인
            draw_nums = set(draw.numbers)
            overlap = len(draw_nums.intersection(set(numbers)))
            if overlap >= 2:  # 2개 이상 겹치면 패턴 일치
                pattern_matches += 1
        
        pattern_score = pattern_matches / min(50, len(self.draws))
        
        # 연속 번호가 있으면 약간 감점
        if consecutive:
            pattern_score *= 0.9
        
        return min(1.0, pattern_score)
    
    def _calculate_weather_index(self) -> float:
        """기상 지수 계산"""
        today = datetime.now().date()
        weather = self.db.query(WeatherFeature).filter(
            WeatherFeature.date == today
        ).first()
        
        if not weather:
            return 0.5  # 데이터 없으면 중간값
        
        # 간단한 기상 지수 (실제로는 더 복잡한 로직 필요)
        index = 0.5
        
        if weather.temp_avg:
            # 온도가 적정 범위(15~25도)에 있으면 높은 점수
            if 15 <= weather.temp_avg <= 25:
                index += 0.2
            else:
                index -= 0.1
        
        if weather.precipitation:
            # 강수량이 적으면 높은 점수
            if weather.precipitation < 5:
                index += 0.1
            else:
                index -= 0.1
        
        return max(0.0, min(1.0, index))
    
    def _calculate_economic_index(self) -> float:
        """경제 지수 계산"""
        today = datetime.now().date()
        economic = self.db.query(EconomicFeature).filter(
            EconomicFeature.date == today
        ).first()
        
        if not economic:
            return 0.5  # 데이터 없으면 중간값
        
        # 간단한 경제 지수 (실제로는 더 복잡한 로직 필요)
        index = 0.5
        
        if economic.kospi_index:
            # KOSPI가 상승 추세면 높은 점수
            # 실제로는 전일 대비 비교 필요
            index += 0.1
        
        return max(0.0, min(1.0, index))

