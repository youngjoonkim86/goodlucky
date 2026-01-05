"""
분석 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/variables")
async def get_variable_analysis(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    환경변수별 영향도 분석
    """
    service = AnalyticsService(db)
    analysis = service.analyze_variables(start_date, end_date)
    return analysis


@router.get("/frequency")
async def get_number_frequency(
    limit: int = Query(45, ge=1, le=45),
    db: Session = Depends(get_db)
):
    """
    번호별 출현 빈도 분석
    """
    service = AnalyticsService(db)
    frequency = service.get_number_frequency(limit)
    return frequency


@router.get("/patterns")
async def get_pattern_analysis(
    db: Session = Depends(get_db)
):
    """
    패턴 분석 (연속번호, 홀짝비율 등)
    """
    service = AnalyticsService(db)
    patterns = service.analyze_patterns()
    return patterns


@router.get("/correlation")
async def get_correlation_analysis(
    db: Session = Depends(get_db)
):
    """
    환경변수와 번호 간 상관관계 분석
    """
    service = AnalyticsService(db)
    correlation = service.analyze_correlation()
    return correlation

