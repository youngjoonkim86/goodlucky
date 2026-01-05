"""
추천 서비스
"""
from sqlalchemy.orm import Session
from typing import List
import random
import numpy as np
from collections import Counter

from app.models.lotto import LottoDraw
from app.models.weather import WeatherFeature
from app.models.economic import EconomicFeature
from app.schemas.recommendation import RecommendationResponse
from app.ml.advanced_recommendation_engine import AdvancedRecommendationEngine
from app.ml.consistent_recommendation_engine import ConsistentRecommendationEngine


class RecommendationService:
    """추천 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.engine = AdvancedRecommendationEngine(db)
        self.consistent_engine = None
    
    def generate_recommendations(
        self,
        count: int = 5,
        include_weather: bool = True,
        include_economic: bool = True,
        consistent: bool = False
    ) -> List[RecommendationResponse]:
        """
        추천 번호 생성
        
        Args:
            count: 추천 개수
            include_weather: 기상 데이터 포함 여부
            include_economic: 경제 지표 포함 여부
            consistent: 일관된 결과 반환 여부
        """
        # 일관된 결과가 필요하면 Consistent 엔진 사용
        if consistent:
            if self.consistent_engine is None:
                self.consistent_engine = ConsistentRecommendationEngine(self.db)
            engine = self.consistent_engine
        else:
            engine = self.engine
        
        recommendations = []
        
        for _ in range(count):
            if consistent and hasattr(engine, 'generate_numbers'):
                # Consistent 엔진인 경우 use_seed 파라미터 전달
                numbers, confidence, features = engine.generate_numbers(
                    include_weather=include_weather,
                    include_economic=include_economic,
                    use_seed=True
                )
            else:
                # 일반 엔진인 경우 use_seed 파라미터 없이 호출
                numbers, confidence, features = engine.generate_numbers(
                    include_weather=include_weather,
                    include_economic=include_economic
                )
            
            recommendations.append(RecommendationResponse(
                numbers=numbers,
                confidence=confidence,
                features=features,
                explanation=self._generate_explanation(features)
            ))
        
        # 신뢰도 순으로 정렬
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return recommendations
    
    def calculate_confidence(self, numbers: List[int]) -> dict:
        """특정 번호 조합의 신뢰도 계산"""
        confidence, features = self.engine.calculate_confidence(numbers)
        
        return {
            "numbers": numbers,
            "confidence": confidence,
            "features": features,
            "explanation": self._generate_explanation(features)
        }
    
    def _generate_explanation(self, features: dict) -> str:
        """추천 이유 설명 생성"""
        explanations = []
        
        if "frequency_score" in features:
            if features["frequency_score"] > 0.5:
                explanations.append("과거 출현 빈도가 높은 번호를 포함했습니다.")
            else:
                explanations.append("과거 출현 빈도가 낮은 번호를 포함했습니다.")
        
        if "pattern_score" in features:
            if features["pattern_score"] > 0.5:
                explanations.append("역대 패턴과 유사한 조합입니다.")
        
        if "weather_idx" in features:
            explanations.append(f"기상 조건을 고려했습니다 (점수: {features['weather_idx']:.2f}).")
        
        if "economic_idx" in features:
            explanations.append(f"경제 지표를 고려했습니다 (점수: {features['economic_idx']:.2f}).")
        
        return " ".join(explanations) if explanations else "통계적 분석을 기반으로 추천되었습니다."

