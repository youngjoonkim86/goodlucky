"""
경제 지표 데이터 모델
"""
from sqlalchemy import Column, Integer, Float, Date, String
from app.core.database import Base
from datetime import date


class EconomicFeature(Base):
    """경제 지표 특성 데이터"""
    __tablename__ = "economic_features"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    exchange_rate_usd = Column(Float)  # USD 환율
    exchange_rate_eur = Column(Float)  # EUR 환율
    kospi_index = Column(Float)  # KOSPI 지수
    kosdaq_index = Column(Float)  # KOSDAQ 지수
    interest_rate = Column(Float)  # 기준금리
    cpi = Column(Float)  # 소비자물가지수
    pmi = Column(Float)  # 구매자지수
    unemployment_rate = Column(Float)  # 실업률
    
    def __repr__(self):
        return f"<EconomicFeature(date={self.date}, kospi={self.kospi_index})>"

