"""
최종 업데이트 스크립트 - 실제 날짜 기반으로 정확한 최신 회차 계산
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import datetime, timedelta
import time
import json

def get_weekday_saturday_count(start_date: datetime, end_date: datetime) -> int:
    """시작일부터 종료일까지의 토요일 개수 계산"""
    # 첫 번째 토요일 찾기
    days_until_saturday = (5 - start_date.weekday()) % 7
    if days_until_saturday == 0 and start_date.weekday() != 5:
        days_until_saturday = 7
    
    first_saturday = start_date + timedelta(days=days_until_saturday)
    
    if first_saturday > end_date:
        return 0
    
    # 토요일 간격으로 계산
    days_between = (end_date - first_saturday).days
    weeks = days_between // 7
    
    return weeks + 1

def calculate_exact_latest_draw(target_date: datetime = None) -> int:
    """정확한 최신 회차 계산 (2002-12-07 1회차부터)"""
    if target_date is None:
        target_date = datetime.now()
    
    # 2002년 12월 7일 1회차 (토요일)
    start_date = datetime(2002, 12, 7)
    
    # 목표 날짜의 이전 토요일까지 계산
    # 토요일은 weekday() = 5
    days_since_start = (target_date - start_date).days
    
    # 첫 토요일 이후의 토요일 개수
    if start_date.weekday() == 5:
        # 시작일이 토요일이면
        weeks = days_since_start // 7
    else:
        # 첫 토요일 찾기
        days_to_first_sat = (5 - start_date.weekday()) % 7
        if days_to_first_sat == 0:
            days_to_first_sat = 7
        first_saturday = start_date + timedelta(days=days_to_first_sat)
        
        if target_date < first_saturday:
            return 0
        
        days_after_first_sat = (target_date - first_saturday).days
        weeks = days_after_first_sat // 7
    
    # 1회차부터 시작
    return weeks + 1

def try_fetch_draw(draw_no: int) -> dict:
    """회차 데이터 가져오기"""
    url = "https://www.dhlottery.co.kr/common.do"
    params = {"method": "getLottoNumber", "drwNo": draw_no}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
        "Origin": "https://www.dhlottery.co.kr"
    }
    
    for attempt in range(3):
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    text = response.text.strip()
                    if text.startswith("{") or "drwtNo1" in text:
                        try:
                            data = response.json()
                            if isinstance(data, dict) and data.get("drwtNo1"):
                                return data
                        except:
                            pass
        except:
            pass
        
        if attempt < 2:
            time.sleep(1)
    
    return None

def main():
    """메인 실행"""
    db: Session = SessionLocal()
    try:
        # 현재 DB 최대 회차 및 날짜
        max_draw = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        current_max = max_draw.draw_no if max_draw else 0
        current_date = max_draw.draw_date if max_draw else None
        
        print(f"현재 DB 최대 회차: {current_max}")
        if current_date:
            print(f"최신 회차 날짜: {current_date}")
        
        # 오늘 날짜 기준 정확한 계산
        today = datetime.now()
        calculated_latest = calculate_exact_latest_draw(today)
        
        print(f"\n오늘({today.strftime('%Y-%m-%d %A')}) 기준 계산된 최신 회차: {calculated_latest}")
        
        # 어제 기준 계산
        yesterday = today - timedelta(days=1)
        calculated_yesterday = calculate_exact_latest_draw(yesterday)
        print(f"어제({yesterday.strftime('%Y-%m-%d %A')}) 기준 계산된 최신 회차: {calculated_yesterday}")
        
        # 확인할 범위 (현재 최대 + 1부터 계산된 최신 + 여유분까지)
        check_start = current_max + 1
        check_end = max(calculated_latest, calculated_yesterday) + 5
        
        print(f"\n확인할 범위: {check_start} ~ {check_end}")
        print(f"총 {check_end - check_start + 1}개 회차 확인 예정\n")
        
        if check_start > check_end:
            print("✅ 이미 최신 데이터가 있습니다.")
            return
        
        # 실제 존재하는 회차 찾기 및 추가
        added_count = 0
        found_any = False
        
        for draw_no in range(check_start, check_end + 1):
            # 이미 존재 확인
            existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
            if existing:
                print(f"회차 {draw_no}: 이미 존재")
                found_any = True
                continue
            
            print(f"회차 {draw_no} 수집 중...", end=" ", flush=True)
            data = try_fetch_draw(draw_no)
            
            if not data:
                print("✗ 실패")
                # 연속으로 3개 실패하면 중단
                if not found_any and draw_no - current_max > 3:
                    print(f"\n연속으로 데이터를 가져올 수 없어 중단합니다.")
                    break
                continue
            
            found_any = True
            
            # 데이터 파싱
            numbers = [data.get(f"drwtNo{i}") for i in range(1, 7)]
            numbers = [n for n in numbers if n is not None]
            
            if len(numbers) != 6:
                print("✗ 데이터 불완전")
                continue
            
            bonus = data.get("bnusNo")
            draw_date_str = data.get("drwNoDate", "")
            draw_date = None
            if draw_date_str:
                try:
                    draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
                except:
                    pass
            
            # DB 추가
            lotto_draw = LottoDraw(
                draw_no=draw_no,
                draw_date=draw_date,
                number1=numbers[0],
                number2=numbers[1],
                number3=numbers[2],
                number4=numbers[3],
                number5=numbers[4],
                number6=numbers[5],
                bonus_number=bonus,
                first_prize_winners=data.get("firstPrzwnerCo", 0),
                first_prize_amount=data.get("firstWinamnt", 0),
                total_sales=data.get("totSellamnt", 0),
                extra_metadata={"returnValue": data.get("returnValue")}
            )
            
            db.add(lotto_draw)
            added_count += 1
            print(f"✓ 추가: {numbers} (보너스: {bonus}, 날짜: {draw_date})")
            
            time.sleep(0.7)
        
        db.commit()
        
        if added_count > 0:
            new_max = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
            print(f"\n✅ 완료! {added_count}개 회차 추가됨")
            print(f"   최신 회차: {new_max.draw_no} (날짜: {new_max.draw_date})")
        else:
            print(f"\n✅ 확인 완료. 추가할 회차가 없습니다.")
            print(f"   현재 최신 회차: {current_max}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

