"""
추천 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class RecommendationResponse(BaseModel):
    """추천 번호 응답 스키마"""
    numbers: List[int] = Field(..., description="추천 번호 6개")
    confidence: float = Field(..., ge=0.0, le=1.0, description="신뢰도 (0.0 ~ 1.0)")
    features: Dict[str, float] = Field(default_factory=dict, description="특성별 점수")
    explanation: Optional[str] = Field(None, description="추천 이유 설명")
    
    class Config:
        from_attributes = True

