"""
샘플 로또 데이터 추가 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import date, timedelta
import random

def add_sample_data():
    """샘플 로또 데이터 추가"""
    db = SessionLocal()
    try:
        # 기존 데이터 확인
        existing_count = db.query(LottoDraw).count()
        if existing_count > 0:
            print(f"이미 {existing_count}개의 데이터가 있습니다.")
            return
        
        # 샘플 데이터 생성 (최근 100회차)
        base_date = date.today()
        sample_data = []
        
        for i in range(100, 0, -1):
            draw_no = 1000 + i
            draw_date = base_date - timedelta(days=(100 - i) * 7)  # 주 1회 추첨 가정
            
            # 랜덤 번호 생성 (중복 없이)
            numbers = sorted(random.sample(range(1, 46), 6))
            bonus = random.choice([n for n in range(1, 46) if n not in numbers])
            
            sample_data.append({
                "draw_no": draw_no,
                "draw_date": draw_date,
                "numbers": numbers,
                "bonus": bonus,
                "first_prize_winners": random.randint(0, 20),
                "first_prize_amount": random.randint(100000000, 500000000),  # 범위 축소
                "total_sales": random.randint(5000000000, 10000000000)  # 범위 축소
            })
        
        # 데이터베이스에 추가
        for data in sample_data:
            draw = LottoDraw(**data)
            db.add(draw)
        
        db.commit()
        print(f"✅ {len(sample_data)}개의 샘플 데이터가 추가되었습니다.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()

