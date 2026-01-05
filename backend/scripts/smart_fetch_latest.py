"""
스마트하게 최신 회차를 찾아서 DB에 추가하는 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import datetime
import json
import time

def get_draw_data_with_retry(draw_no: int, max_retries: int = 3) -> dict:
    """재시도 로직이 있는 회차 데이터 조회"""
    for attempt in range(max_retries):
        try:
            # 여러 엔드포인트 시도
            urls = [
                f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
                f"https://dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
            ]
            
            headers_list = [
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
                    "Accept-Language": "ko-KR,ko;q=0.9",
                    "Origin": "https://www.dhlottery.co.kr"
                },
                {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "*/*",
                }
            ]
            
            for url in urls:
                for headers in headers_list:
                    try:
                        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                            response = client.get(url, headers=headers)
                            
                            if response.status_code != 200:
                                continue
                            
                            # JSON 시도
                            try:
                                data = response.json()
                                if isinstance(data, dict) and data.get("returnValue") == "success":
                                    return data
                            except:
                                # HTML 응답일 수 있음, 다음 시도
                                pass
                    except:
                        continue
            
            # 실패 시 대기 후 재시도
            if attempt < max_retries - 1:
                time.sleep(1)
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            continue
    
    return None

def find_and_add_latest():
    """최신 회차를 찾아서 DB에 추가"""
    db: Session = SessionLocal()
    try:
        # 현재 DB 최대 회차
        max_draw = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        current_max = max_draw.draw_no if max_draw else 0
        print(f"현재 DB 최대 회차: {current_max}")
        
        # 오늘 날짜 기준 추정 최대 회차
        start_date = datetime(2002, 12, 7)
        today = datetime.now()
        weeks = (today - start_date).days // 7
        estimated_max = weeks + 3
        
        print(f"추정 최대 회차: {estimated_max}")
        print(f"\n{current_max + 1}회차부터 {estimated_max}회차까지 확인 중...\n")
        
        # 순차적으로 확인 (최신 회차부터 역순으로)
        found_latest = current_max
        added_count = 0
        
        # 최신 회차부터 역순으로 확인 (더 효율적)
        for draw_no in range(estimated_max, current_max, -1):
            print(f"회차 {draw_no} 확인 중...", end=" ")
            
            data = get_draw_data_with_retry(draw_no)
            
            if data:
                # 이미 존재하는지 확인
                existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
                if existing:
                    print("이미 존재")
                    found_latest = max(found_latest, draw_no)
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
                bonus = data.get("bnusNo")
                
                draw_date_str = data.get("drwNoDate", "")
                draw_date = None
                if draw_date_str:
                    try:
                        draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
                    except:
                        pass
                
                # DB에 추가
                lotto_draw = LottoDraw(
                    draw_no=draw_no,
                    draw_date=draw_date,
                    number1=numbers[0] if len(numbers) > 0 else None,
                    number2=numbers[1] if len(numbers) > 1 else None,
                    number3=numbers[2] if len(numbers) > 2 else None,
                    number4=numbers[3] if len(numbers) > 3 else None,
                    number5=numbers[4] if len(numbers) > 4 else None,
                    number6=numbers[5] if len(numbers) > 5 else None,
                    bonus_number=bonus,
                    first_prize_winners=data.get("firstPrzwnerCo", 0),
                    first_prize_amount=data.get("firstWinamnt", 0),
                    total_sales=data.get("totSellamnt", 0),
                    extra_metadata={"returnValue": data.get("returnValue")}
                )
                
                db.add(lotto_draw)
                found_latest = max(found_latest, draw_no)
                added_count += 1
                print(f"✓ 추가: {numbers} (보너스: {bonus})")
            else:
                print("✗ 없음")
            
            time.sleep(0.3)  # API 부하 방지
            
            # 연속으로 5개가 없으면 중단 (최신 회차를 찾았으므로)
            if draw_no <= found_latest + 5:
                break
        
        db.commit()
        print(f"\n✅ 완료!")
        print(f"   - 최신 회차: {found_latest}")
        print(f"   - 추가된 회차: {added_count}개")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    find_and_add_latest()

