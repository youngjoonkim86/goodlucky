"""
로또 당첨 데이터 모델
"""
from sqlalchemy import Column, Integer, BigInteger, Date, ARRAY, String
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
from datetime import date


class LottoDraw(Base):
    """로또 추첨 결과"""
    __tablename__ = "lotto_draws"
    
    id = Column(Integer, primary_key=True, index=True)
    draw_no = Column(Integer, unique=True, nullable=False, index=True)  # 회차
    draw_date = Column(Date, nullable=False, index=True)  # 추첨일
    numbers = Column(ARRAY(Integer), nullable=False)  # 당첨 번호 6개
    bonus = Column(Integer, nullable=False)  # 보너스 번호
    first_prize_winners = Column(Integer, default=0)  # 1등 당첨자 수
    first_prize_amount = Column(BigInteger, default=0)  # 1등 당첨금
    total_sales = Column(BigInteger, default=0)  # 총 판매액
    extra_metadata = Column(JSONB, default={})  # 추가 메타데이터
    
    def __repr__(self):
        return f"<LottoDraw(draw_no={self.draw_no}, numbers={self.numbers}, bonus={self.bonus})>"

