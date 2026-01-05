"""
최신 로또 당첨번호 가져오기
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import requests
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import datetime
import json


def get_latest_draw_no():
    """동행복권 API에서 최신 회차 조회"""
    try:
        # 동행복권 API (실제 API 엔드포인트)
        url = "https://www.dhlottery.co.kr/common.do"
        params = {
            "method": "getLottoNumber",
            "drwNo": ""  # 빈 값이면 최신 회차
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("returnValue") == "success":
            return data.get("drwNo")
        else:
            # API 실패 시 웹에서 최신 회차 추정 (대략적인 방법)
            # 실제로는 웹 스크래핑이 필요할 수 있음
            print("⚠️ API에서 최신 회차를 가져올 수 없습니다.")
            return None
    except Exception as e:
        print(f"❌ 최신 회차 조회 실패: {e}")
        return None


def get_draw_data(draw_no):
    """특정 회차 당첨번호 가져오기"""
    try:
        url = "https://www.dhlottery.co.kr/common.do"
        params = {
            "method": "getLottoNumber",
            "drwNo": draw_no
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
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
            try:
                draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
            except:
                draw_date = None
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
        print(f"❌ 회차 {draw_no} 데이터 가져오기 실패: {e}")
        return None


def fetch_latest_draws():
    """최신 당첨번호 가져오기"""
    db = SessionLocal()
    try:
        # 현재 DB의 최대 회차 확인
        from sqlalchemy import text
        result = db.execute(text("SELECT MAX(draw_no) FROM lotto_draws"))
        max_draw_no = result.scalar() or 0
        
        print(f"현재 DB 최대 회차: {max_draw_no}")
        
        # 최신 회차 조회
        latest_draw_no = get_latest_draw_no()
        
        if not latest_draw_no:
            # API 실패 시 수동으로 최신 회차 입력 받기
            print("\n⚠️ 자동으로 최신 회차를 가져올 수 없습니다.")
            print("동행복권 사이트에서 최신 회차를 확인하여 입력해주세요.")
            latest_draw_no = input("최신 회차 번호를 입력하세요 (예: 1150): ")
            try:
                latest_draw_no = int(latest_draw_no)
            except:
                print("❌ 잘못된 입력입니다.")
                return
        
        print(f"최신 회차: {latest_draw_no}")
        
        if latest_draw_no <= max_draw_no:
            print(f"✅ 이미 최신 데이터가 있습니다. (최대 회차: {max_draw_no})")
            return
        
        # 누락된 회차 가져오기
        missing_count = latest_draw_no - max_draw_no
        print(f"\n{missing_count}개 회차의 데이터를 가져옵니다...")
        
        added_count = 0
        for draw_no in range(max_draw_no + 1, latest_draw_no + 1):
            draw_data = get_draw_data(draw_no)
            
            if not draw_data:
                print(f"⚠️ 회차 {draw_no} 데이터 없음 (건너뜀)")
                continue
            
            # 중복 확인
            existing = db.execute(
                text("SELECT id FROM lotto_draws WHERE draw_no = :draw_no"),
                {"draw_no": draw_no}
            ).scalar()
            
            if existing:
                print(f"⏭️ 회차 {draw_no} 이미 존재 (건너뜀)")
                continue
            
            # 데이터 삽입
            db.execute(
                text("""
                    INSERT INTO lotto_draws 
                    (draw_no, draw_date, numbers, bonus, first_prize_winners, first_prize_amount, total_sales, extra_metadata)
                    VALUES (:draw_no, :draw_date, :numbers, :bonus, :first_prize_winners, :first_prize_amount, :total_sales, :extra_metadata)
                """),
                {
                    "draw_no": draw_data["draw_no"],
                    "draw_date": draw_data["draw_date"],
                    "numbers": draw_data["numbers"],
                    "bonus": draw_data["bonus"],
                    "first_prize_winners": draw_data.get("first_prize_winners", 0),
                    "first_prize_amount": draw_data.get("first_prize_amount", 0),
                    "total_sales": draw_data.get("total_sales", 0),
                    "extra_metadata": json.dumps(draw_data.get("extra_metadata", {}))
                }
            )
            added_count += 1
            print(f"✅ 회차 {draw_no} 추가 완료: {draw_data['numbers']}")
        
        db.commit()
        print(f"\n✅ 총 {added_count}개 회차 데이터 추가 완료!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_latest_draws()

