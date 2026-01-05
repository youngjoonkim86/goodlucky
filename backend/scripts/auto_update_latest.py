"""
자동으로 최신 회차 데이터를 가져와서 데이터베이스에 추가하는 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import datetime
import httpx
from loguru import logger

def get_latest_draw_no() -> int:
    """최신 회차 번호 조회"""
    try:
        # 동행복권 API: 빈 drwNo로 요청하면 최신 회차 반환
        url = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo="
        
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            # JSON 파싱 시도
            try:
                data = response.json()
                if data.get("returnValue") == "success":
                    return data.get("drwNo")
            except:
                # JSON이 아닌 경우 HTML일 수 있음
                logger.warning("JSON 응답이 아닙니다. HTML 응답일 수 있습니다.")
                # HTML에서 회차 번호 추출 시도
                content = response.text
                # 최신 회차 추정 (매주 토요일 추첨, 2002년 12월 7일 1회차 시작)
                today = datetime.now()
                start_date = datetime(2002, 12, 7)
                weeks = (today - start_date).days // 7
                estimated = weeks + 1
                logger.info(f"추정 최신 회차: {estimated}")
                return estimated
    except Exception as e:
        logger.error(f"최신 회차 조회 실패: {e}")
        # 추정값 반환
        today = datetime.now()
        start_date = datetime(2002, 12, 7)
        weeks = (today - start_date).days // 7
        estimated = weeks + 1
        return estimated

def get_draw_data(draw_no: int) -> dict:
    """특정 회차 데이터 조회"""
    try:
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
        
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            try:
                data = response.json()
                if data.get("returnValue") != "success":
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
                    "draw_date": draw_date,
                    "numbers": numbers,
                    "bonus": bonus,
                    "first_prize_winners": data.get("firstPrzwnerCo", 0),
                    "first_prize_amount": data.get("firstWinamnt", 0),
                    "total_sales": data.get("totSellamnt", 0),
                    "extra_metadata": {
                        "returnValue": data.get("returnValue"),
                        "raw_data": data
                    }
                }
            except Exception as e:
                logger.error(f"JSON 파싱 실패 (회차 {draw_no}): {e}")
                return None
    except Exception as e:
        logger.error(f"회차 {draw_no} 데이터 수집 실패: {e}")
        return None

def update_to_latest():
    """데이터베이스의 최대 회차부터 최신 회차까지 업데이트"""
    db: Session = SessionLocal()
    try:
        # 현재 DB의 최대 회차 조회
        max_draw = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        current_max = max_draw.draw_no if max_draw else 0
        
        logger.info(f"현재 DB 최대 회차: {current_max}")
        
        # 최신 회차 조회
        latest_draw_no = get_latest_draw_no()
        logger.info(f"최신 회차: {latest_draw_no}")
        
        if latest_draw_no <= current_max:
            logger.info("이미 최신 데이터입니다.")
            return
        
        # 누락된 회차 추가
        added_count = 0
        for draw_no in range(current_max + 1, latest_draw_no + 1):
            logger.info(f"회차 {draw_no} 수집 중...")
            data = get_draw_data(draw_no)
            
            if data:
                # 이미 존재하는지 확인
                existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
                if existing:
                    logger.info(f"회차 {draw_no}는 이미 존재합니다.")
                    continue
                
                # 새 레코드 생성
                lotto_draw = LottoDraw(
                    draw_no=data["draw_no"],
                    draw_date=data["draw_date"],
                    number1=data["numbers"][0] if len(data["numbers"]) > 0 else None,
                    number2=data["numbers"][1] if len(data["numbers"]) > 1 else None,
                    number3=data["numbers"][2] if len(data["numbers"]) > 2 else None,
                    number4=data["numbers"][3] if len(data["numbers"]) > 3 else None,
                    number5=data["numbers"][4] if len(data["numbers"]) > 4 else None,
                    number6=data["numbers"][5] if len(data["numbers"]) > 5 else None,
                    bonus_number=data["bonus"],
                    first_prize_winners=data["first_prize_winners"],
                    first_prize_amount=data["first_prize_amount"],
                    total_sales=data["total_sales"],
                    extra_metadata=data.get("extra_metadata")
                )
                
                db.add(lotto_draw)
                added_count += 1
                logger.info(f"회차 {draw_no} 추가 완료")
            else:
                logger.warning(f"회차 {draw_no} 데이터를 가져올 수 없습니다.")
        
        db.commit()
        logger.info(f"총 {added_count}개 회차 추가 완료")
        
    except Exception as e:
        db.rollback()
        logger.error(f"업데이트 실패: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_to_latest()

