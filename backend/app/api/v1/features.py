"""
Feature Selection API 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.feature_selection_service import FeatureSelectionService

router = APIRouter()


@router.post("/select")
async def run_feature_selection(
    target: str = Query("sum_numbers", description="타겟 변수명"),
    season: Optional[str] = Query(None, description="시즌 (spring/summer/fall/winter)"),
    db: Session = Depends(get_db)
):
    """
    변수 선택 파이프라인 실행
    """
    service = FeatureSelectionService(db)
    result = service.run_feature_selection(target=target, season=season)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "변수 선택 실패"))
    
    return result


@router.get("/current")
async def get_current_features(
    db: Session = Depends(get_db)
):
    """
    현재 활성화된 특성 목록 조회
    """
    service = FeatureSelectionService(db)
    features = service.get_current_features()
    log = service.get_selection_log()
    
    return {
        "features": features,
        "count": len(features),
        "selection_log": log
    }


@router.get("/registry")
async def get_feature_registry():
    """
    Feature Registry 조회
    """
    from app.ml.feature_registry import FEATURE_REGISTRY
    
    return {
        "registry": FEATURE_REGISTRY,
        "total_features": len(FEATURE_REGISTRY)
    }

