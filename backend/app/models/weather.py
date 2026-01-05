"""
기상 데이터 모델
"""
from sqlalchemy import Column, Integer, Float, Date, String
from app.core.database import Base
from datetime import date


class WeatherFeature(Base):
    """기상 특성 데이터"""
    __tablename__ = "weather_features"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    temp_max = Column(Float)  # 최고 기온
    temp_min = Column(Float)  # 최저 기온
    temp_avg = Column(Float)  # 평균 기온
    humidity = Column(Float)  # 습도
    precipitation = Column(Float)  # 강수량
    wind_speed = Column(Float)  # 풍속
    weather_main = Column(String(50))  # 날씨 상태 (Clear, Rain, etc.)
    weather_description = Column(String(200))  # 날씨 상세 설명
    
    def __repr__(self):
        return f"<WeatherFeature(date={self.date}, temp_avg={self.temp_avg})>"

