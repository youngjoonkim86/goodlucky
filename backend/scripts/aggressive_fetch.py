"""
적극적으로 최신 회차를 찾아서 추가하는 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import datetime
import time
import json

def get_draw_data(draw_no: int) -> dict:
    """회차 데이터 가져오기 (다양한 방법 시도)"""
    methods = [
        # 방법 1: 기본 API
        {
            "url": f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
            }
        },
        # 방법 2: 다른 헤더
        {
            "url": f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "*/*"
            }
        },
        # 방법 3: www 없이
        {
            "url": f"https://dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json"
            }
        }
    ]
    
    for method in methods:
        try:
            with httpx.Client(timeout=20.0, follow_redirects=True) as client:
                response = client.get(method["url"], headers=method["headers"])
                
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "").lower()
                    
                    # JSON 응답인 경우
                    if "json" in content_type or response.text.strip().startswith("{"):
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                if data.get("returnValue") == "success":
                                    return data
                                # returnValue가 없어도 drwtNo1이 있으면 성공으로 간주
                                if data.get("drwtNo1") is not None:
                                    return data
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            continue
    
    return None

def find_latest_sequential(start: int, end: int) -> int:
    """순차적으로 최신 회차 찾기"""
    latest = start - 1
    
    print(f"{start}회차부터 {end}회차까지 순차 확인 중...\n")
    
    for draw_no in range(start, end + 1):
        print(f"회차 {draw_no} 확인 중...", end=" ", flush=True)
        
        data = get_draw_data(draw_no)
        
        if data:
            latest = draw_no
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
            print(f"✓ 존재: {numbers} (보너스: {bonus})")
        else:
            print("✗ 없음")
            # 연속으로 3개가 없으면 중단
            if draw_no - latest > 3:
                print(f"\n연속으로 데이터가 없어 {draw_no}회차에서 중단합니다.")
                break
        
        time.sleep(0.4)  # API 부하 방지
    
    return latest

def add_missing_draws(db: Session, start: int, end: int):
    """누락된 회차 추가"""
    added_count = 0
    
    for draw_no in range(start, end + 1):
        # 이미 존재하는지 확인
        existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
        if existing:
            continue
        
        print(f"회차 {draw_no} 수집 중...", end=" ", flush=True)
        
        data = get_draw_data(draw_no)
        
        if not data:
            print("✗ 실패")
            continue
        
        # 데이터 파싱
        numbers = [
            data.get("drwtNo1"),
            data.get("drwtNo2"),
            data.get("drwtNo3"),
            data.get("drwtNo4"),
            data.get("drwtNo5"),
            data.get("drwtNo6")
        ]
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
        
        time.sleep(0.4)
    
    return added_count

def main():
    """메인 실행 함수"""
    db: Session = SessionLocal()
    try:
        # 현재 DB 최대 회차
        max_draw = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        current_max = max_draw.draw_no if max_draw else 0
        print(f"현재 DB 최대 회차: {current_max}\n")
        
        # 넓은 범위로 최신 회차 찾기 (1205부터 1250까지)
        search_start = max(1205, current_max + 1)
        search_end = 1250
        
        print(f"최신 회차 찾기: {search_start} ~ {search_end}\n")
        latest_found = find_latest_sequential(search_start, search_end)
        
        print(f"\n발견된 최신 회차: {latest_found}")
        
        if latest_found <= current_max:
            print("✅ 이미 최신 데이터가 있습니다.")
            return
        
        # 누락된 회차 추가
        print(f"\n{current_max + 1}회차부터 {latest_found}회차까지 추가 중...\n")
        added_count = add_missing_draws(db, current_max + 1, latest_found)
        
        db.commit()
        print(f"\n✅ 완료! {added_count}개 회차 추가됨")
        print(f"   최신 회차: {latest_found}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

