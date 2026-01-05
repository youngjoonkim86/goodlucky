"""
일관된 추천 엔진 - 동일한 조건에서 같은 결과 반환
"""
from sqlalchemy.orm import Session
from typing import List, Tuple, Dict, Optional
import numpy as np
from collections import Counter
from datetime import datetime

from app.ml.advanced_recommendation_engine import AdvancedRecommendationEngine
from app.ml.pattern_analyzer import PatternAnalyzer


class ConsistentRecommendationEngine(AdvancedRecommendationEngine):
    """일관된 추천 엔진 - 시드 기반으로 동일한 결과 반환"""
    
    def __init__(self, db: Session, seed: Optional[int] = None):
        """
        Args:
            db: 데이터베이스 세션
            seed: 랜덤 시드 (None이면 현재 시간 기반)
        """
        super().__init__(db)
        self.seed = seed if seed is not None else int(datetime.now().timestamp())
        np.random.seed(self.seed)
    
    def generate_numbers(
        self,
        include_weather: bool = True,
        include_economic: bool = True,
        use_seed: bool = True
    ) -> Tuple[List[int], float, Dict[str, float]]:
        """
        추천 번호 생성
        
        Args:
            include_weather: 기상 데이터 포함 여부
            include_economic: 경제 지표 포함 여부
            use_seed: 시드 사용 여부 (True면 일관된 결과, False면 매번 다름)
        """
        if use_seed:
            np.random.seed(self.seed)
        
        return super().generate_numbers(include_weather, include_economic)
    
    def reset_seed(self, new_seed: Optional[int] = None):
        """시드 재설정"""
        if new_seed is None:
            self.seed = int(datetime.now().timestamp())
        else:
            self.seed = new_seed
        np.random.seed(self.seed)

