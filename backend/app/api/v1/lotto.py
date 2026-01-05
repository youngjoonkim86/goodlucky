"""
로또 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.models.lotto import LottoDraw
from app.schemas.lotto import LottoDrawResponse, LottoDrawCreate
from app.services.lotto_service import LottoService

router = APIRouter()


@router.get("/history", response_model=List[LottoDrawResponse])
async def get_lotto_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    draw_no: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    로또 당첨 이력 조회
    """
    service = LottoService(db)
    draws = service.get_draws(
        skip=skip,
        limit=limit,
        draw_no=draw_no,
        start_date=start_date,
        end_date=end_date
    )
    return draws


@router.get("/history/{draw_no}", response_model=LottoDrawResponse)
async def get_lotto_by_draw_no(
    draw_no: int,
    db: Session = Depends(get_db)
):
    """
    특정 회차 로또 당첨 정보 조회
    """
    service = LottoService(db)
    draw = service.get_draw_by_no(draw_no)
    if not draw:
        raise HTTPException(status_code=404, detail=f"회차 {draw_no} 정보를 찾을 수 없습니다.")
    return draw


@router.post("/history", response_model=LottoDrawResponse)
async def create_lotto_draw(
    draw_data: LottoDrawCreate,
    db: Session = Depends(get_db)
):
    """
    로또 당첨 데이터 추가 (관리자용)
    """
    service = LottoService(db)
    draw = service.create_draw(draw_data)
    return draw


@router.get("/latest", response_model=LottoDrawResponse)
async def get_latest_lotto(
    db: Session = Depends(get_db)
):
    """
    최신 로또 당첨 정보 조회
    """
    service = LottoService(db)
    draw = service.get_latest_draw()
    if not draw:
        raise HTTPException(status_code=404, detail="당첨 정보를 찾을 수 없습니다.")
    return draw


@router.get("/statistics")
async def get_lotto_statistics(
    db: Session = Depends(get_db)
):
    """
    로또 통계 정보 조회
    """
    service = LottoService(db)
    stats = service.get_statistics()
    return stats

