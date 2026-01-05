"""
고급 추천 엔진 - 역대 번호 분석 기반
"""
from sqlalchemy.orm import Session
from typing import List, Tuple, Dict
import random
import numpy as np
from collections import Counter

from app.models.lotto import LottoDraw
from app.ml.pattern_analyzer import PatternAnalyzer


class AdvancedRecommendationEngine:
    """고급 추천 엔진 - 역대 패턴 분석 기반"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = PatternAnalyzer(db)
        self._load_patterns()
    
    def _load_patterns(self):
        """패턴 데이터 로드"""
        self.frequency = self.analyzer.analyze_number_frequency()
        self.pairs = self.analyzer.analyze_number_pairs()
        self.sum_stats = self.analyzer.analyze_sum_patterns()
        self.odd_even_stats = self.analyzer.analyze_odd_even_patterns()
        self.consecutive_stats = self.analyzer.analyze_consecutive_patterns()
        self.high_low_stats = self.analyzer.analyze_high_low_patterns()
        self.gap_stats = self.analyzer.analyze_gap_patterns()
        self.recent_trends = self.analyzer.analyze_recent_trends()
    
    def generate_numbers(
        self,
        include_weather: bool = True,
        include_economic: bool = True
    ) -> Tuple[List[int], float, Dict[str, float]]:
        """
        역대 패턴 분석 기반 추천 번호 생성
        
        Returns:
            (numbers, confidence, features)
        """
        if not self.frequency:
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
        
        # 여러 후보 생성 후 최적 조합 선택
        candidates = []
        
        for _ in range(50):  # 50개 후보 생성
            candidate = self._generate_candidate()
            if candidate:
                score = self.analyzer.get_optimal_combination_score(
                    candidate,
                    self.frequency,
                    self.pairs,
                    self.sum_stats,
                    self.odd_even_stats,
                    self.consecutive_stats,
                    self.high_low_stats
                )
                candidates.append((candidate, score))
        
        if not candidates:
            # 후보 생성 실패 시 랜덤
            numbers = sorted(random.sample(range(1, 46), 6))
            return numbers, 0.5, self._calculate_features(numbers)
        
        # 최고 점수 조합 선택
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_numbers, best_score = candidates[0]
        
        # 신뢰도 및 특성 계산
        confidence, features = self._calculate_confidence_and_features(
            best_numbers,
            include_weather,
            include_economic
        )
        
        return sorted(best_numbers), confidence, features
    
    def _generate_candidate(self) -> List[int]:
        """후보 번호 생성"""
        if not self.frequency:
            return sorted(random.sample(range(1, 46), 6))
        
        selected = []
        available = list(range(1, 46))
        
        # 전략 1: 최근 트렌드 반영 (Hot/Cold 번호)
        hot_numbers = self.recent_trends.get("hot_numbers", [])
        cold_numbers = self.recent_trends.get("cold_numbers", [])
        
        # Hot 번호 2-3개 포함
        if hot_numbers:
            hot_count = random.randint(2, 3)
            for _ in range(min(hot_count, len(hot_numbers))):
                if hot_numbers and available:
                    num = random.choice([n for n in hot_numbers if n in available])
                    selected.append(num)
                    available.remove(num)
        
        # Cold 번호 1-2개 포함 (반등 가능성)
        if cold_numbers and len(selected) < 5:
            cold_count = random.randint(1, 2)
            for _ in range(min(cold_count, len(cold_numbers), 6 - len(selected))):
                if cold_numbers and available:
                    num = random.choice([n for n in cold_numbers if n in available])
                    selected.append(num)
                    available.remove(num)
        
        # 나머지는 빈도 기반 가중치 샘플링
        while len(selected) < 6:
            if not available:
                break
            
            # 사용 가능한 번호에 대한 가중치
            weights = [self.frequency.get(num, 0.1) for num in available]
            weights = np.array(weights)
            
            if weights.sum() > 0:
                weights = weights / weights.sum()
            else:
                weights = np.ones(len(available)) / len(available)
            
            # 가중치 기반 선택
            idx = np.random.choice(len(available), p=weights)
            num = available.pop(idx)
            selected.append(num)
        
        return sorted(selected) if len(selected) == 6 else None
    
    def _calculate_confidence_and_features(
        self,
        numbers: List[int],
        include_weather: bool,
        include_economic: bool
    ) -> Tuple[float, Dict[str, float]]:
        """신뢰도 및 특성 계산"""
        features = {}
        
        # 1. 빈도 점수
        freq_scores = [self.frequency.get(num, 0.1) for num in numbers]
        features["frequency_score"] = np.mean(freq_scores)
        
        # 2. 패턴 점수 (최적 조합 점수)
        pattern_score = self.analyzer.get_optimal_combination_score(
            numbers,
            self.frequency,
            self.pairs,
            self.sum_stats,
            self.odd_even_stats,
            self.consecutive_stats,
            self.high_low_stats
        )
        features["pattern_score"] = pattern_score
        
        # 3. 쌍 점수
        pair_score = 0.0
        pair_count = 0
        numbers_sorted = sorted(numbers)
        for i in range(len(numbers_sorted)):
            for j in range(i + 1, len(numbers_sorted)):
                pair = (numbers_sorted[i], numbers_sorted[j])
                pair_freq = self.pairs.get(pair, 0)
                max_pair_freq = max(self.pairs.values()) if self.pairs else 1
                pair_score += pair_freq / max_pair_freq if max_pair_freq > 0 else 0
                pair_count += 1
        features["pair_score"] = pair_score / pair_count if pair_count > 0 else 0
        
        # 4. 합계 점수
        total_sum = sum(numbers)
        if self.sum_stats:
            mean_sum = self.sum_stats.get("mean", 150)
            std_sum = self.sum_stats.get("std", 20)
            diff = abs(total_sum - mean_sum)
            features["sum_score"] = max(0, 1 - (diff / (std_sum * 2)))
        else:
            features["sum_score"] = 0.5
        
        # 5. 홀짝 비율 점수
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        if self.odd_even_stats:
            ideal_odd = self.odd_even_stats.get("most_common_odd", 3)
            features["odd_even_score"] = max(0, 1 - abs(odd_count - ideal_odd) / 3)
        else:
            features["odd_even_score"] = 0.5
        
        # 6. 연속 번호 점수
        numbers_sorted = sorted(numbers)
        consecutive = sum(1 for i in range(len(numbers_sorted) - 1) 
                         if numbers_sorted[i+1] - numbers_sorted[i] == 1)
        if self.consecutive_stats:
            ideal_consecutive = self.consecutive_stats.get("mean_consecutive", 1)
            features["consecutive_score"] = max(0, 1 - abs(consecutive - ideal_consecutive) / 2)
        else:
            features["consecutive_score"] = 0.5
        
        # 7. 고저 비율 점수
        low_count = sum(1 for n in numbers if n <= 22)
        if self.high_low_stats:
            ideal_low = self.high_low_stats.get("most_common_low", 3)
            features["high_low_score"] = max(0, 1 - abs(low_count - ideal_low) / 3)
        else:
            features["high_low_score"] = 0.5
        
        # 8. 최근 트렌드 점수
        hot_numbers = self.recent_trends.get("hot_numbers", [])
        hot_count = sum(1 for n in numbers if n in hot_numbers)
        features["trend_score"] = hot_count / 6.0
        
        # 9. 기상/경제 지수 (기존 로직)
        if include_weather:
            features["weather_idx"] = self._calculate_weather_index()
        else:
            features["weather_idx"] = 0.0
        
        if include_economic:
            features["economic_idx"] = self._calculate_economic_index()
        else:
            features["economic_idx"] = 0.0
        
        # 최종 신뢰도 계산 (가중 평균)
        weights = {
            "frequency_score": 0.15,
            "pattern_score": 0.25,  # 패턴 점수에 더 높은 가중치
            "pair_score": 0.15,
            "sum_score": 0.10,
            "odd_even_score": 0.10,
            "consecutive_score": 0.05,
            "high_low_score": 0.05,
            "trend_score": 0.10,
            "weather_idx": 0.03,
            "economic_idx": 0.02
        }
        
        confidence = sum(
            features.get(key, 0) * weight
            for key, weight in weights.items()
        )
        
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence, features
    
    def _calculate_features(self, numbers: List[int]) -> Dict[str, float]:
        """특성만 계산 (신뢰도 없이)"""
        _, features = self._calculate_confidence_and_features(numbers, True, True)
        return features
    
    def _calculate_weather_index(self) -> float:
        """기상 지수 계산 (기존 로직)"""
        from datetime import datetime
        from app.models.weather import WeatherFeature
        
        today = datetime.now().date()
        weather = self.db.query(WeatherFeature).filter(
            WeatherFeature.date == today
        ).first()
        
        if not weather:
            return 0.5
        
        index = 0.5
        if weather.temp_avg:
            if 15 <= weather.temp_avg <= 25:
                index += 0.2
            else:
                index -= 0.1
        
        if weather.precipitation:
            if weather.precipitation < 5:
                index += 0.1
            else:
                index -= 0.1
        
        return max(0.0, min(1.0, index))
    
    def _calculate_economic_index(self) -> float:
        """경제 지수 계산 (기존 로직)"""
        from datetime import datetime
        from app.models.economic import EconomicFeature
        
        today = datetime.now().date()
        economic = self.db.query(EconomicFeature).filter(
            EconomicFeature.date == today
        ).first()
        
        if not economic:
            return 0.5
        
        index = 0.5
        if economic.kospi_index:
            index += 0.1
        
        return max(0.0, min(1.0, index))
    
    def calculate_confidence(self, numbers: List[int]) -> Tuple[float, Dict[str, float]]:
        """특정 번호 조합의 신뢰도 계산"""
        return self._calculate_confidence_and_features(numbers, True, True)

