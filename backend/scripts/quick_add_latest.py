"""
빠른 최신 회차 추가 (간단 버전)
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from datetime import date


def quick_add():
    """빠르게 최신 회차 추가"""
    db = SessionLocal()
    try:
        # 현재 최대 회차
        result = db.execute(text("SELECT MAX(draw_no) FROM lotto_draws"))
        current_max = result.scalar() or 0
        print(f"\n현재 최대 회차: {current_max}")
        print("동행복권: https://www.dhlottery.co.kr/gameResult.do?method=byWin")
        print("\n최신 회차 정보를 입력하세요:")
        
        draw_no = int(input("회차 번호: "))
        
        if draw_no <= current_max:
            print(f"⚠️ 이미 존재하는 회차입니다.")
            return
        
        numbers_str = input("당첨번호 6개 (공백 구분, 예: 1 2 3 4 5 6): ")
        numbers = sorted([int(n) for n in numbers_str.split()])
        
        bonus = int(input("보너스 번호: "))
        
        # 오늘 날짜 사용
        draw_date = date.today()
        
        # 삽입
        db.execute(
            text("""
                INSERT INTO lotto_draws 
                (draw_no, draw_date, numbers, bonus, first_prize_winners, first_prize_amount, total_sales, extra_metadata)
                VALUES (:draw_no, :draw_date, :numbers, :bonus, 0, 0, 0, '{}')
            """),
            {
                "draw_no": draw_no,
                "draw_date": draw_date,
                "numbers": numbers,
                "bonus": bonus
            }
        )
        
        db.commit()
        print(f"\n✅ 회차 {draw_no} 추가 완료!")
        print(f"   번호: {numbers} + {bonus}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    quick_add()

