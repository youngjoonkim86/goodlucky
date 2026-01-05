"""
추천 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationResponse

router = APIRouter()


@router.get("/numbers", response_model=List[RecommendationResponse])
async def get_recommended_numbers(
    count: int = Query(5, ge=1, le=20, description="추천 번호 조합 개수"),
    include_weather: bool = Query(True, description="기상 데이터 포함 여부"),
    include_economic: bool = Query(True, description="경제 지표 포함 여부"),
    consistent: bool = Query(False, description="일관된 결과 반환 여부 (True면 같은 조건에서 같은 결과)"),
    db: Session = Depends(get_db)
):
    """
    추천 번호 생성
    
    - consistent=False (기본값): 매번 다른 추천 번호 생성
    - consistent=True: 동일한 조건에서 같은 추천 번호 반환
    """
    service = RecommendationService(db)
    recommendations = service.generate_recommendations(
        count=count,
        include_weather=include_weather,
        include_economic=include_economic,
        consistent=consistent
    )
    return recommendations


@router.get("/numbers/confidence")
async def get_number_confidence(
    numbers: str = Query(..., description="쉼표로 구분된 번호 (예: 1,2,3,4,5,6)"),
    db: Session = Depends(get_db)
):
    """
    특정 번호 조합의 신뢰도 계산
    """
    try:
        number_list = [int(n.strip()) for n in numbers.split(",")]
        if len(number_list) != 6:
            raise ValueError("6개의 번호를 입력해주세요.")
        if not all(1 <= n <= 45 for n in number_list):
            raise ValueError("번호는 1부터 45 사이여야 합니다.")
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    
    service = RecommendationService(db)
    confidence = service.calculate_confidence(number_list)
    return confidence

