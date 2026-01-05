"""
역대 번호 패턴 분석기
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime

from app.models.lotto import LottoDraw


class PatternAnalyzer:
    """역대 번호 패턴 분석"""
    
    def __init__(self, db: Session):
        self.db = db
        self.draws = None
        self._load_data()
    
    def _load_data(self):
        """데이터 로드"""
        self.draws = self.db.query(LottoDraw).order_by(LottoDraw.draw_no).all()
    
    def analyze_number_frequency(self) -> Dict[int, float]:
        """번호별 출현 빈도 분석"""
        if not self.draws:
            return {}
        
        all_numbers = []
        for draw in self.draws:
            if draw.numbers:
                all_numbers.extend(draw.numbers)
        
        frequency = Counter(all_numbers)
        total = len(self.draws)
        
        # 정규화된 빈도 (0~1)
        normalized = {}
        max_freq = max(frequency.values()) if frequency else 1
        for num in range(1, 46):
            normalized[num] = frequency.get(num, 0) / max_freq if max_freq > 0 else 0
        
        return normalized
    
    def analyze_number_pairs(self) -> Dict[Tuple[int, int], int]:
        """번호 쌍 출현 빈도 분석"""
        if not self.draws:
            return {}
        
        pairs = []
        for draw in self.draws:
            if draw.numbers and len(draw.numbers) == 6:
                numbers = sorted(draw.numbers)
                # 모든 쌍 생성
                for i in range(len(numbers)):
                    for j in range(i + 1, len(numbers)):
                        pairs.append((numbers[i], numbers[j]))
        
        return Counter(pairs)
    
    def analyze_number_triplets(self) -> Dict[Tuple[int, int, int], int]:
        """번호 3개 조합 출현 빈도 분석"""
        if not self.draws:
            return {}
        
        triplets = []
        for draw in self.draws:
            if draw.numbers and len(draw.numbers) == 6:
                numbers = sorted(draw.numbers)
                # 모든 3개 조합 생성
                for i in range(len(numbers)):
                    for j in range(i + 1, len(numbers)):
                        for k in range(j + 1, len(numbers)):
                            triplets.append((numbers[i], numbers[j], numbers[k]))
        
        return Counter(triplets)
    
    def analyze_sum_patterns(self) -> Dict[str, float]:
        """합계 패턴 분석"""
        if not self.draws:
            return {}
        
        sums = []
        for draw in self.draws:
            if draw.numbers:
                sums.append(sum(draw.numbers))
        
        if not sums:
            return {}
        
        return {
            "mean": np.mean(sums),
            "median": np.median(sums),
            "std": np.std(sums),
            "min": min(sums),
            "max": max(sums),
            "q1": np.percentile(sums, 25),
            "q3": np.percentile(sums, 75)
        }
    
    def analyze_odd_even_patterns(self) -> Dict[str, float]:
        """홀짝 패턴 분석"""
        if not self.draws:
            return {}
        
        odd_counts = []
        for draw in self.draws:
            if draw.numbers:
                odd_count = sum(1 for n in draw.numbers if n % 2 == 1)
                odd_counts.append(odd_count)
        
        if not odd_counts:
            return {}
        
        return {
            "mean_odd": np.mean(odd_counts),
            "most_common_odd": Counter(odd_counts).most_common(1)[0][0] if odd_counts else 3
        }
    
    def analyze_consecutive_patterns(self) -> Dict[str, float]:
        """연속 번호 패턴 분석"""
        if not self.draws:
            return {}
        
        consecutive_counts = []
        for draw in self.draws:
            if draw.numbers:
                numbers = sorted(draw.numbers)
                consecutive = 0
                for i in range(len(numbers) - 1):
                    if numbers[i+1] - numbers[i] == 1:
                        consecutive += 1
                consecutive_counts.append(consecutive)
        
        if not consecutive_counts:
            return {}
        
        return {
            "mean_consecutive": np.mean(consecutive_counts),
            "has_consecutive_ratio": sum(1 for c in consecutive_counts if c > 0) / len(consecutive_counts)
        }
    
    def analyze_high_low_patterns(self) -> Dict[str, float]:
        """고저 번호 패턴 분석 (1-22: 저, 23-45: 고)"""
        if not self.draws:
            return {}
        
        low_counts = []
        for draw in self.draws:
            if draw.numbers:
                low_count = sum(1 for n in draw.numbers if n <= 22)
                low_counts.append(low_count)
        
        if not low_counts:
            return {}
        
        return {
            "mean_low": np.mean(low_counts),
            "most_common_low": Counter(low_counts).most_common(1)[0][0] if low_counts else 3
        }
    
    def analyze_gap_patterns(self) -> Dict[str, float]:
        """번호 간격 패턴 분석"""
        if not self.draws:
            return {}
        
        all_gaps = []
        for draw in self.draws:
            if draw.numbers and len(draw.numbers) == 6:
                numbers = sorted(draw.numbers)
                gaps = [numbers[i+1] - numbers[i] for i in range(len(numbers) - 1)]
                all_gaps.extend(gaps)
        
        if not all_gaps:
            return {}
        
        return {
            "mean_gap": np.mean(all_gaps),
            "median_gap": np.median(all_gaps),
            "min_gap": min(all_gaps),
            "max_gap": max(all_gaps)
        }
    
    def analyze_recent_trends(self, window: int = 20) -> Dict[str, any]:
        """최근 추세 분석"""
        if not self.draws or len(self.draws) < window:
            return {}
        
        recent_draws = self.draws[-window:]
        
        recent_numbers = []
        for draw in recent_draws:
            if draw.numbers:
                recent_numbers.extend(draw.numbers)
        
        frequency = Counter(recent_numbers)
        
        return {
            "hot_numbers": [num for num, _ in frequency.most_common(10)],  # 최근 자주 나온 번호
            "cold_numbers": [num for num in range(1, 46) if num not in frequency or frequency[num] == 0]  # 최근 안 나온 번호
        }
    
    def get_optimal_combination_score(
        self,
        numbers: List[int],
        frequency: Dict[int, float],
        pairs: Dict[Tuple[int, int], int],
        sum_stats: Dict[str, float],
        odd_even_stats: Dict[str, float],
        consecutive_stats: Dict[str, float],
        high_low_stats: Dict[str, float]
    ) -> float:
        """번호 조합의 최적성 점수 계산"""
        if len(numbers) != 6:
            return 0.0
        
        score = 0.0
        numbers = sorted(numbers)
        
        # 1. 빈도 점수 (30%)
        freq_score = np.mean([frequency.get(num, 0.1) for num in numbers])
        score += freq_score * 0.3
        
        # 2. 쌍 점수 (20%)
        pair_score = 0.0
        pair_count = 0
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                pair = (numbers[i], numbers[j])
                pair_freq = pairs.get(pair, 0)
                max_pair_freq = max(pairs.values()) if pairs else 1
                pair_score += pair_freq / max_pair_freq if max_pair_freq > 0 else 0
                pair_count += 1
        if pair_count > 0:
            pair_score = pair_score / pair_count
        score += pair_score * 0.2
        
        # 3. 합계 점수 (15%)
        total_sum = sum(numbers)
        if sum_stats:
            mean_sum = sum_stats.get("mean", 150)
            std_sum = sum_stats.get("std", 20)
            # 평균에 가까울수록 높은 점수
            diff = abs(total_sum - mean_sum)
            sum_score = max(0, 1 - (diff / (std_sum * 2)))
            score += sum_score * 0.15
        
        # 4. 홀짝 비율 점수 (15%)
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        if odd_even_stats:
            ideal_odd = odd_even_stats.get("most_common_odd", 3)
            odd_score = 1 - abs(odd_count - ideal_odd) / 3
            score += max(0, odd_score) * 0.15
        
        # 5. 연속 번호 점수 (10%)
        consecutive = 0
        for i in range(len(numbers) - 1):
            if numbers[i+1] - numbers[i] == 1:
                consecutive += 1
        if consecutive_stats:
            ideal_consecutive = consecutive_stats.get("mean_consecutive", 1)
            consecutive_score = 1 - abs(consecutive - ideal_consecutive) / 2
            score += max(0, consecutive_score) * 0.1
        
        # 6. 고저 비율 점수 (10%)
        low_count = sum(1 for n in numbers if n <= 22)
        if high_low_stats:
            ideal_low = high_low_stats.get("most_common_low", 3)
            low_score = 1 - abs(low_count - ideal_low) / 3
            score += max(0, low_score) * 0.1
        
        return min(1.0, score)

