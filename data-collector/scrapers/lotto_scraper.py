"""
로또 당첨 번호 스크래퍼
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import time
from loguru import logger


class LottoScraper:
    """로또 당첨 번호 스크래퍼"""
    
    BASE_URL = "https://www.dhlottery.co.kr/common.do"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_latest_draw_no(self) -> Optional[int]:
        """최신 회차 번호 조회"""
        try:
            # 동행복권 API: 빈 drwNo로 요청하면 최신 회차 반환
            url = f"{self.BASE_URL}?method=getLottoNumber&drwNo="
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("returnValue") == "success":
                return data.get("drwNo")
            else:
                # API 실패 시 대체 방법: 최근 회차를 시도해보기
                logger.warning("API에서 최신 회차를 가져올 수 없습니다. 대체 방법 시도...")
                # 최근 몇 회차를 시도해보기
                from datetime import datetime
                # 대략적인 최신 회차 추정 (매주 토요일 추첨, 2002년 12월 7일 1회차 시작)
                today = datetime.now()
                start_date = datetime(2002, 12, 7)
                weeks = (today - start_date).days // 7
                estimated = weeks + 1
                
                # 실제 존재하는 회차 찾기 (최근 10회차 시도)
                for i in range(10):
                    test_no = estimated - i
                    test_data = self.get_draw_data(test_no)
                    if test_data:
                        logger.info(f"최신 회차 추정: {test_no}")
                        return test_no
                
                return None
        except Exception as e:
            logger.error(f"최신 회차 조회 실패: {e}")
            return None
    
    def get_draw_data(self, draw_no: int) -> Optional[Dict]:
        """
        특정 회차 당첨 번호 조회
        
        Args:
            draw_no: 회차 번호
            
        Returns:
            {
                "draw_no": int,
                "draw_date": str (YYYY-MM-DD),
                "numbers": [int, ...],
                "bonus": int,
                "first_prize_winners": int,
                "first_prize_amount": int,
                "total_sales": int
            }
        """
        try:
            url = f"{self.BASE_URL}?method=getLottoNumber&drwNo={draw_no}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("returnValue") != "success":
                logger.warning(f"회차 {draw_no} 데이터 없음")
                return None
            
            # 번호 추출
            numbers = [
                data.get("drwtNo1"),
                data.get("drwtNo2"),
                data.get("drwtNo3"),
                data.get("drwtNo4"),
                data.get("drwtNo5"),
                data.get("drwtNo6")
            ]
            numbers = [n for n in numbers if n is not None]
            bonus = data.get("bnusNo")
            
            # 날짜 변환
            draw_date_str = data.get("drwNoDate", "")
            if draw_date_str:
                draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
            else:
                draw_date = None
            
            return {
                "draw_no": draw_no,
                "draw_date": draw_date.isoformat() if draw_date else None,
                "numbers": numbers,
                "bonus": bonus,
                "first_prize_winners": data.get("firstPrzwnerCo", 0),
                "first_prize_amount": data.get("firstWinamnt", 0),
                "total_sales": data.get("totSellamnt", 0),
                "metadata": {
                    "returnValue": data.get("returnValue"),
                    "raw_data": data
                }
            }
        except Exception as e:
            logger.error(f"회차 {draw_no} 데이터 수집 실패: {e}")
            return None
    
    def get_all_draws(self, start_draw_no: int = 1, end_draw_no: Optional[int] = None) -> List[Dict]:
        """
        여러 회차 데이터 수집
        
        Args:
            start_draw_no: 시작 회차
            end_draw_no: 종료 회차 (None이면 최신까지)
        """
        if end_draw_no is None:
            end_draw_no = self.get_latest_draw_no() or start_draw_no
        
        results = []
        for draw_no in range(start_draw_no, end_draw_no + 1):
            data = self.get_draw_data(draw_no)
            if data:
                results.append(data)
            time.sleep(0.5)  # API 부하 방지
        
        logger.info(f"{len(results)}개 회차 데이터 수집 완료")
        return results

