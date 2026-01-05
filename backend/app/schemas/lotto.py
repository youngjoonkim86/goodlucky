"""
로또 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class LottoDrawBase(BaseModel):
    """로또 추첨 기본 스키마"""
    draw_no: int = Field(..., description="회차")
    draw_date: date = Field(..., description="추첨일")
    numbers: List[int] = Field(..., min_items=6, max_items=6, description="당첨 번호 6개")
    bonus: int = Field(..., ge=1, le=45, description="보너스 번호")
    first_prize_winners: Optional[int] = Field(0, description="1등 당첨자 수")
    first_prize_amount: Optional[int] = Field(0, description="1등 당첨금")
    total_sales: Optional[int] = Field(0, description="총 판매액")
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 메타데이터")


class LottoDrawCreate(LottoDrawBase):
    """로또 추첨 생성 스키마"""
    pass


class LottoDrawResponse(LottoDrawBase):
    """로또 추첨 응답 스키마"""
    id: int
    
    class Config:
        from_attributes = True

