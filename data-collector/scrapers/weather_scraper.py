"""
기상 데이터 수집기
"""
import requests
from typing import Dict, Optional
from datetime import date, datetime
from loguru import logger
import os


class WeatherScraper:
    """기상 데이터 수집기 (OpenWeather API 사용)"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "")
        if not self.api_key:
            logger.warning("OpenWeather API 키가 설정되지 않았습니다.")
    
    def get_weather_data(
        self,
        target_date: date,
        city: str = "Seoul",
        country: str = "KR"
    ) -> Optional[Dict]:
        """
        특정 날짜의 기상 데이터 조회
        
        Args:
            target_date: 조회할 날짜
            city: 도시명
            country: 국가 코드
            
        Returns:
            {
                "date": str (YYYY-MM-DD),
                "temp_max": float,
                "temp_min": float,
                "temp_avg": float,
                "humidity": float,
                "precipitation": float,
                "wind_speed": float,
                "weather_main": str,
                "weather_description": str
            }
        """
        if not self.api_key:
            logger.error("API 키가 없어 기상 데이터를 수집할 수 없습니다.")
            return None
        
        try:
            # OpenWeather API는 현재 날씨만 제공하므로
            # 과거 데이터는 다른 소스 필요 (예: 기상청 API)
            # 여기서는 현재 날씨 조회 예시
            
            url = f"{self.BASE_URL}/weather"
            params = {
                "q": f"{city},{country}",
                "appid": self.api_key,
                "units": "metric",
                "lang": "kr"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})
            
            return {
                "date": target_date.isoformat(),
                "temp_max": main.get("temp_max"),
                "temp_min": main.get("temp_min"),
                "temp_avg": main.get("temp"),
                "humidity": main.get("humidity"),
                "precipitation": data.get("rain", {}).get("1h", 0) if "rain" in data else 0,
                "wind_speed": wind.get("speed"),
                "weather_main": weather.get("main"),
                "weather_description": weather.get("description")
            }
        except Exception as e:
            logger.error(f"기상 데이터 수집 실패 ({target_date}): {e}")
            return None
    
    def get_historical_weather(self, target_date: date) -> Optional[Dict]:
        """
        과거 기상 데이터 조회
        OpenWeather의 One Call API 3.0 (유료) 또는 기상청 API 필요
        """
        # 실제 구현은 유료 API 또는 기상청 API 사용
        logger.warning("과거 기상 데이터는 유료 API 또는 기상청 API가 필요합니다.")
        return None

