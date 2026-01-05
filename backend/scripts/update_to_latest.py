"""
최신 로또 당첨번호까지 업데이트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from datetime import datetime
import json
import time


def get_draw_data(draw_no):
    """특정 회차 당첨번호 가져오기"""
    try:
        url = "https://www.dhlottery.co.kr/common.do"
        params = {
            "method": "getLottoNumber",
            "drwNo": draw_no
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
        }
        
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        if data.get("returnValue") != "success":
            return None
        
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
        
        return {
            "draw_no": draw_no,
            "draw_date": draw_date,
            "numbers": numbers,
            "bonus": bonus,
            "first_prize_winners": data.get("firstPrzwnerCo", 0),
            "first_prize_amount": data.get("firstWinamnt", 0),
            "total_sales": data.get("totSellamnt", 0),
            "extra_metadata": json.dumps({"returnValue": data.get("returnValue")})
        }
    except Exception as e:
        print(f"회차 {draw_no} 오류: {e}")
        return None


def find_latest_draw_no():
    """최신 회차 찾기"""
    # 먼저 빈 drwNo로 최신 회차 시도
    try:
        url = "https://www.dhlottery.co.kr/common.do"
        params = {"method": "getLottoNumber", "drwNo": ""}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("returnValue") == "success":
                latest = data.get("drwNo")
                if latest:
                    print(f"최신 회차 (API): {latest}")
                    return latest
    except Exception as e:
        print(f"API 최신 회차 조회 실패: {e}")
    
    # API 실패 시 이진 탐색
    from datetime import datetime
    start_date = datetime(2002, 12, 7)
    today = datetime.now()
    weeks = (today - start_date).days // 7
    max_estimated = weeks + 10
    
    low = 1100
    high = max_estimated
    latest = low
    
    print(f"최신 회차 찾는 중... (범위: {low} ~ {high})")
    
    while low <= high:
        mid = (low + high) // 2
        data = get_draw_data(mid)
        
        if data:
            latest = mid
            low = mid + 1
            print(f"  ✓ 회차 {mid} 존재")
        else:
            high = mid - 1
            print(f"  ✗ 회차 {mid} 없음")
        
        time.sleep(0.3)
    
    return latest


def update_to_latest():
    """최신 회차까지 업데이트"""
    db = SessionLocal()
    try:
        # 현재 최대 회차
        result = db.execute(text("SELECT MAX(draw_no) FROM lotto_draws"))
        current_max = result.scalar() or 0
        print(f"현재 DB 최대 회차: {current_max}")
        
        # 최신 회차 찾기
        latest = find_latest_draw_no()
        print(f"\n최신 회차: {latest}")
        
        if latest <= current_max:
            print("✅ 이미 최신 데이터가 있습니다.")
            return
        
        # 누락된 회차 추가
        missing = latest - current_max
        print(f"\n{missing}개 회차 추가 중...")
        
        added = 0
        for draw_no in range(current_max + 1, latest + 1):
            draw_data = get_draw_data(draw_no)
            
            if not draw_data:
                print(f"⚠️ 회차 {draw_no} 건너뜀")
                continue
            
            # 중복 확인
            existing = db.execute(
                text("SELECT id FROM lotto_draws WHERE draw_no = :draw_no"),
                {"draw_no": draw_no}
            ).scalar()
            
            if existing:
                continue
            
            # 삽입
            db.execute(
                text("""
                    INSERT INTO lotto_draws 
                    (draw_no, draw_date, numbers, bonus, first_prize_winners, first_prize_amount, total_sales, extra_metadata)
                    VALUES (:draw_no, :draw_date, :numbers, :bonus, :first_prize_winners, :first_prize_amount, :total_sales, :extra_metadata)
                """),
                draw_data
            )
            added += 1
            print(f"✅ 회차 {draw_no}: {draw_data['numbers']}")
            
            time.sleep(0.5)  # API 부하 방지
        
        db.commit()
        print(f"\n✅ {added}개 회차 추가 완료!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    update_to_latest()

