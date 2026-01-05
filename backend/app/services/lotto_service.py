"""
로또 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import date

from app.models.lotto import LottoDraw
from app.schemas.lotto import LottoDrawCreate


class LottoService:
    """로또 데이터 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_draws(
        self,
        skip: int = 0,
        limit: int = 100,
        draw_no: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[LottoDraw]:
        """로또 추첨 이력 조회"""
        query = self.db.query(LottoDraw)
        
        if draw_no:
            query = query.filter(LottoDraw.draw_no == draw_no)
        
        if start_date:
            query = query.filter(LottoDraw.draw_date >= start_date)
        
        if end_date:
            query = query.filter(LottoDraw.draw_date <= end_date)
        
        return query.order_by(desc(LottoDraw.draw_no)).offset(skip).limit(limit).all()
    
    def get_draw_by_no(self, draw_no: int) -> Optional[LottoDraw]:
        """회차로 조회"""
        return self.db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
    
    def get_latest_draw(self) -> Optional[LottoDraw]:
        """최신 추첨 조회"""
        return self.db.query(LottoDraw).order_by(desc(LottoDraw.draw_no)).first()
    
    def create_draw(self, draw_data: LottoDrawCreate) -> LottoDraw:
        """로또 추첨 데이터 생성"""
        # 중복 확인
        existing = self.get_draw_by_no(draw_data.draw_no)
        if existing:
            raise ValueError(f"회차 {draw_data.draw_no}는 이미 존재합니다.")
        
        # 번호 유효성 검사
        if len(draw_data.numbers) != 6:
            raise ValueError("번호는 6개여야 합니다.")
        if not all(1 <= n <= 45 for n in draw_data.numbers):
            raise ValueError("번호는 1부터 45 사이여야 합니다.")
        if len(set(draw_data.numbers)) != 6:
            raise ValueError("중복된 번호가 있습니다.")
        if not (1 <= draw_data.bonus <= 45):
            raise ValueError("보너스 번호는 1부터 45 사이여야 합니다.")
        if draw_data.bonus in draw_data.numbers:
            raise ValueError("보너스 번호는 당첨 번호와 중복될 수 없습니다.")
        
        draw = LottoDraw(**draw_data.dict())
        self.db.add(draw)
        self.db.commit()
        self.db.refresh(draw)
        return draw
    
    def get_statistics(self) -> dict:
        """로또 통계 정보"""
        total_draws = self.db.query(func.count(LottoDraw.id)).scalar()
        latest_draw = self.get_latest_draw()
        
        # 번호별 출현 빈도
        all_numbers = []
        for draw in self.db.query(LottoDraw).all():
            all_numbers.extend(draw.numbers)
        
        number_frequency = {}
        for num in range(1, 46):
            number_frequency[num] = all_numbers.count(num)
        
        return {
            "total_draws": total_draws,
            "latest_draw_no": latest_draw.draw_no if latest_draw else None,
            "latest_draw_date": latest_draw.draw_date.isoformat() if latest_draw else None,
            "number_frequency": number_frequency,
            "most_frequent_numbers": sorted(
                number_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

