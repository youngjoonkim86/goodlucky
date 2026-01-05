"""
최신 회차를 찾는 스크립트 (1205회차부터 시작)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from datetime import datetime
import time

def get_draw_data(draw_no: int) -> dict:
    """특정 회차 데이터 조회"""
    try:
        url = "https://www.dhlottery.co.kr/common.do"
        params = {
            "method": "getLottoNumber",
            "drwNo": draw_no
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            # Content-Type 확인
            content_type = response.headers.get("content-type", "")
            if "json" not in content_type.lower():
                return None
            
            try:
                data = response.json()
                if data.get("returnValue") == "success":
                    return data
            except:
                return None
    except Exception as e:
        return None

def find_latest():
    """최신 회차 찾기 (1205부터 시작)"""
    # 오늘 날짜 기준 추정 최대 회차
    start_date = datetime(2002, 12, 7)
    today = datetime.now()
    weeks = (today - start_date).days // 7
    max_estimated = weeks + 5  # 여유분 포함
    
    print(f"추정 최대 회차: {max_estimated}")
    print(f"1205회차부터 {max_estimated}회차까지 확인 중...\n")
    
    # 1205부터 시작해서 존재하는 최대 회차 찾기
    latest = 1205
    start = 1205
    end = min(max_estimated, 1250)  # 안전하게 1250까지만
    
    # 이진 탐색
    low = start
    high = end
    found_latest = start
    
    while low <= high:
        mid = (low + high) // 2
        print(f"회차 {mid} 확인 중...", end=" ")
        
        data = get_draw_data(mid)
        
        if data:
            found_latest = mid
            low = mid + 1
            print(f"✓ 존재 (당첨번호: {data.get('drwtNo1')}, {data.get('drwtNo2')}, {data.get('drwtNo3')}, {data.get('drwtNo4')}, {data.get('drwtNo5')}, {data.get('drwtNo6')})")
        else:
            high = mid - 1
            print("✗ 없음")
        
        time.sleep(0.5)  # API 부하 방지
    
    print(f"\n최신 회차: {found_latest}")
    return found_latest

if __name__ == "__main__":
    latest = find_latest()
    print(f"\n✅ 최신 회차: {latest}")

