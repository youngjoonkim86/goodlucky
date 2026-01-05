"""
API v1 라우터
"""
from fastapi import APIRouter
from app.api.v1 import lotto, analytics, recommendations, features

router = APIRouter()

router.include_router(lotto.router, prefix="/lotto", tags=["로또"])
router.include_router(analytics.router, prefix="/analytics", tags=["분석"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["추천"])
router.include_router(features.router, prefix="/features", tags=["특성 선택"])

