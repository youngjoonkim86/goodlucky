"""
수동으로 최신 회차 추가
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import datetime
import json


def manual_add_draw():
    """수동으로 회차 추가"""
    db = SessionLocal()
    try:
        # 현재 최대 회차
        result = db.execute(text("SELECT MAX(draw_no) FROM lotto_draws"))
        current_max = result.scalar() or 0
        print(f"현재 최대 회차: {current_max}")
        
        print("\n동행복권 사이트에서 최신 회차 정보를 확인하세요:")
        print("https://www.dhlottery.co.kr/gameResult.do?method=byWin")
        
        draw_no = input("\n회차 번호를 입력하세요: ")
        try:
            draw_no = int(draw_no)
        except:
            print("❌ 잘못된 입력입니다.")
            return
        
        if draw_no <= current_max:
            print(f"⚠️ 회차 {draw_no}는 이미 존재합니다. (최대: {current_max})")
            return
        
        # 번호 입력
        print("\n당첨 번호 6개를 입력하세요 (예: 1 2 3 4 5 6):")
        numbers_input = input("번호: ").strip().split()
        try:
            numbers = [int(n) for n in numbers_input]
            if len(numbers) != 6:
                raise ValueError("6개가 아님")
            if not all(1 <= n <= 45 for n in numbers):
                raise ValueError("범위 초과")
            if len(set(numbers)) != 6:
                raise ValueError("중복")
        except Exception as e:
            print(f"❌ 번호 입력 오류: {e}")
            return
        
        # 보너스 번호
        bonus = input("보너스 번호: ")
        try:
            bonus = int(bonus)
            if not (1 <= bonus <= 45) or bonus in numbers:
                raise ValueError()
        except:
            print("❌ 보너스 번호 오류")
            return
        
        # 날짜
        date_str = input("추첨일 (YYYY-MM-DD, 엔터시 오늘): ").strip()
        if date_str:
            try:
                draw_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                print("❌ 날짜 형식 오류")
                return
        else:
            from datetime import date
            draw_date = date.today()
        
        # 데이터 삽입
        db.execute(
            text("""
                INSERT INTO lotto_draws 
                (draw_no, draw_date, numbers, bonus, first_prize_winners, first_prize_amount, total_sales, extra_metadata)
                VALUES (:draw_no, :draw_date, :numbers, :bonus, 0, 0, 0, '{}')
            """),
            {
                "draw_no": draw_no,
                "draw_date": draw_date,
                "numbers": sorted(numbers),
                "bonus": bonus
            }
        )
        
        db.commit()
        print(f"✅ 회차 {draw_no} 추가 완료: {sorted(numbers)} + {bonus}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    manual_add_draw()

