"""
실제 최신 회차를 확인하고 업데이트하는 종합 스크립트
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

def calculate_latest_draw_no(target_date: datetime = None) -> int:
    """날짜 기반으로 최신 회차 계산"""
    if target_date is None:
        target_date = datetime.now()
    
    # 2002년 12월 7일 1회차 (토요일)
    start_date = datetime(2002, 12, 7)
    
    # 목표 날짜의 이전 토요일 찾기
    days_since_start = (target_date - start_date).days
    weeks = days_since_start // 7
    
    # 최신 회차 (1회차부터 시작)
    latest = weeks + 1
    
    return latest

def try_get_draw_data(draw_no: int, max_attempts: int = 5) -> dict:
    """다양한 방법으로 회차 데이터 가져오기"""
    attempts = [
        # 시도 1: 기본 API
        {
            "url": "https://www.dhlottery.co.kr/common.do",
            "params": {"method": "getLottoNumber", "drwNo": draw_no},
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
                "Origin": "https://www.dhlottery.co.kr",
                "X-Requested-With": "XMLHttpRequest"
            }
        },
        # 시도 2: 다른 파라미터 형식
        {
            "url": f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
            "params": None,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*"
            }
        }
    ]
    
    for attempt_idx, attempt in enumerate(attempts):
        for retry in range(max_attempts):
            try:
                with httpx.Client(timeout=25.0, follow_redirects=True) as client:
                    if attempt["params"]:
                        response = client.get(attempt["url"], params=attempt["params"], headers=attempt["headers"])
                    else:
                        response = client.get(attempt["url"], headers=attempt["headers"])
                    
                    if response.status_code == 200:
                        text = response.text.strip()
                        
                        # JSON 파싱 시도
                        if text.startswith("{") or text.startswith("["):
                            try:
                                data = response.json()
                                if isinstance(data, dict):
                                    # returnValue 체크
                                    if data.get("returnValue") == "success":
                                        return data
                                    # returnValue가 없어도 drwtNo1이 있으면 성공
                                    if data.get("drwtNo1") is not None:
                                        # returnValue를 success로 설정
                                        data["returnValue"] = "success"
                                        return data
                            except json.JSONDecodeError:
                                pass
                        
                        # HTML 응답인 경우 건너뛰기
                        if "<html" in text.lower() or "<!doctype" in text.lower():
                            break
            except Exception:
                pass
            
            if retry < max_attempts - 1:
                time.sleep(0.5)
        
        if attempt_idx < len(attempts) - 1:
            time.sleep(1)
    
    return None

def main():
    """메인 실행"""
    db: Session = SessionLocal()
    try:
        # 현재 DB 최대 회차
        max_draw = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        current_max = max_draw.draw_no if max_draw else 0
        print(f"현재 DB 최대 회차: {current_max}")
        
        # 오늘 날짜 기준 계산
        today = datetime.now()
        calculated_latest = calculate_latest_draw_no(today)
        print(f"오늘({today.strftime('%Y-%m-%d')}) 기준 계산된 최신 회차: {calculated_latest}")
        
        # 어제 날짜 기준 계산 (토요일 추첨이므로)
        yesterday = today - timedelta(days=1)
        calculated_yesterday = calculate_latest_draw_no(yesterday)
        print(f"어제({yesterday.strftime('%Y-%m-%d')}) 기준 계산된 최신 회차: {calculated_yesterday}")
        
        # 확인할 범위 설정
        check_start = max(current_max + 1, calculated_yesterday - 5)
        check_end = calculated_latest + 3
        
        print(f"\n확인할 범위: {check_start} ~ {check_end}\n")
        
        # 실제 존재하는 최신 회차 찾기
        found_latest = current_max
        test_draws = list(range(check_start, check_end + 1))
        
        print("회차 존재 여부 확인 중...\n")
        for draw_no in test_draws:
            print(f"회차 {draw_no} 테스트...", end=" ", flush=True)
            data = try_get_draw_data(draw_no)
            
            if data:
                found_latest = draw_no
                numbers = [data.get(f"drwtNo{i}") for i in range(1, 7)]
                numbers = [n for n in numbers if n is not None]
                bonus = data.get("bnusNo")
                print(f"✓ 존재: {numbers} (보너스: {bonus})")
            else:
                print("✗ 없음")
                # 연속으로 2개가 없으면 중단
                if draw_no - found_latest > 2:
                    break
            
            time.sleep(0.6)
        
        print(f"\n발견된 최신 회차: {found_latest}")
        
        if found_latest <= current_max:
            print("✅ 이미 최신 데이터가 있습니다.")
            return
        
        # 누락된 회차 추가
        print(f"\n{current_max + 1}회차부터 {found_latest}회차까지 추가 중...\n")
        added_count = 0
        
        for draw_no in range(current_max + 1, found_latest + 1):
            # 이미 존재 확인
            existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
            if existing:
                print(f"회차 {draw_no}: 이미 존재")
                continue
            
            print(f"회차 {draw_no} 수집 중...", end=" ", flush=True)
            data = try_get_draw_data(draw_no)
            
            if not data:
                print("✗ 실패")
                continue
            
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
            print(f"✓ 추가: {numbers} (보너스: {bonus})")
            
            time.sleep(0.6)
        
        db.commit()
        print(f"\n✅ 완료! {added_count}개 회차 추가됨")
        print(f"   최신 회차: {found_latest}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

