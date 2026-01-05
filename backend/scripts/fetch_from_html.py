"""
HTML 파싱을 통해 최신 회차 정보를 가져오는 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lotto import LottoDraw
from datetime import datetime
import re
import time

def get_latest_from_html() -> dict:
    """HTML에서 최신 회차 정보 가져오기"""
    try:
        # 여러 URL 시도
        urls = [
            "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
            "https://dhlottery.co.kr/gameResult.do?method=byWin",
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.dhlottery.co.kr/"
        }
        
        for url in urls:
            try:
                with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                    response = client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # 최신 회차 번호 찾기
                        # 여러 패턴 시도
                        patterns = [
                            r'(\d+)회',
                            r'drwNo["\']?\s*[:=]\s*["\']?(\d+)',
                            r'회차["\']?\s*[:=]\s*["\']?(\d+)',
                        ]
                        
                        text = soup.get_text()
                        html = str(soup)
                        
                        # 최신 회차 번호 찾기
                        latest_draw_no = None
                        for pattern in patterns:
                            matches = re.findall(pattern, text + html)
                            if matches:
                                # 숫자만 추출하고 최대값 찾기
                                numbers = [int(m) for m in matches if m.isdigit() and 1000 <= int(m) <= 2000]
                                if numbers:
                                    latest_draw_no = max(numbers)
                                    break
                        
                        if latest_draw_no:
                            print(f"HTML에서 최신 회차 발견: {latest_draw_no}")
                            return latest_draw_no
                        
            except Exception as e:
                print(f"URL {url} 시도 실패: {e}")
                continue
        
        return None
    except Exception as e:
        print(f"HTML 파싱 실패: {e}")
        return None

def calculate_estimated_latest() -> int:
    """날짜 기반으로 추정 최신 회차 계산"""
    # 2002년 12월 7일 1회차 (토요일)
    start_date = datetime(2002, 12, 7)
    today = datetime.now()
    
    # 토요일까지의 일수 계산
    days_diff = (today - start_date).days
    
    # 주 수 계산 (매주 토요일)
    weeks = days_diff // 7
    
    # 추정 회차 (1회차부터 시작)
    estimated = weeks + 1
    
    return estimated

def get_draw_data_api(draw_no: int) -> dict:
    """API로 회차 데이터 가져오기 (재시도 포함)"""
    for attempt in range(3):
        try:
            url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
            }
            
            with httpx.Client(timeout=20.0, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and data.get("returnValue") == "success":
                            return data
                    except:
                        pass
        except:
            pass
        
        if attempt < 2:
            time.sleep(1)
    
    return None

def fetch_and_add_latest():
    """최신 회차를 찾아서 추가"""
    db: Session = SessionLocal()
    try:
        # 현재 DB 최대 회차
        max_draw = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        current_max = max_draw.draw_no if max_draw else 0
        print(f"현재 DB 최대 회차: {current_max}")
        
        # HTML에서 최신 회차 찾기 시도
        html_latest = get_latest_from_html()
        
        # 날짜 기반 추정
        estimated = calculate_estimated_latest()
        print(f"날짜 기반 추정 회차: {estimated}")
        
        # 최신 회차 결정
        if html_latest:
            target_max = html_latest
        else:
            target_max = estimated
        
        print(f"확인할 최대 회차: {target_max}\n")
        
        if target_max <= current_max:
            print("✅ 이미 최신 데이터가 있습니다.")
            return
        
        # 누락된 회차 추가
        added_count = 0
        for draw_no in range(current_max + 1, target_max + 1):
            print(f"회차 {draw_no} 수집 중...", end=" ")
            
            data = get_draw_data_api(draw_no)
            
            if data:
                # 이미 존재 확인
                existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
                if existing:
                    print("이미 존재")
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
                
                # DB 추가
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
                added_count += 1
                print(f"✓ 추가: {numbers} (보너스: {bonus})")
            else:
                print("✗ 실패")
            
            time.sleep(0.5)
        
        db.commit()
        print(f"\n✅ 완료! {added_count}개 회차 추가")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_add_latest()

