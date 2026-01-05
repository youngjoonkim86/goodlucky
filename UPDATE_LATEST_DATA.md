# 최신 당첨번호 업데이트 가이드

## 문제
현재 데이터베이스에는 1100회차까지만 있고, 최신 회차 데이터가 없습니다.

## 해결 방법

### 방법 1: 수동으로 최신 회차 추가 (권장)

1. **동행복권 사이트에서 최신 회차 확인**
   - https://www.dhlottery.co.kr/gameResult.do?method=byWin
   - 최신 회차 번호와 당첨번호 확인

2. **스크립트 실행**
```bash
docker-compose -f docker-compose.minimal.yml exec backend python -m scripts.quick_add_latest
```

3. **정보 입력**
   - 회차 번호 입력
   - 당첨번호 6개 입력 (공백 구분)
   - 보너스 번호 입력

### 방법 2: 여러 회차 한번에 추가

Python 스크립트로 여러 회차를 한번에 추가할 수 있습니다:

```python
# backend/scripts/batch_add.py 생성 후 실행
```

### 방법 3: API를 통한 자동 수집 (향후 개선)

동행복권 API 접근이 제한되어 있어 현재는 수동 입력이 필요합니다.

향후 개선 사항:
- Selenium을 사용한 웹 스크래핑
- 공식 API 키 발급 (가능한 경우)
- 정기적인 자동 업데이트 스케줄러

## 현재 상태

- **최대 회차**: 1100회차
- **최신 회차**: 동행복권 사이트에서 확인 필요
- **업데이트 필요**: 1101회차 ~ 최신 회차

## 빠른 업데이트 예시

예를 들어 최신 회차가 1150회차라면:

```bash
# 스크립트 실행
docker-compose -f docker-compose.minimal.yml exec backend python -m scripts.quick_add_latest

# 입력 예시:
# 회차 번호: 1150
# 당첨번호: 1 2 3 4 5 6
# 보너스: 7
```

## 자동화 (향후)

데이터 수집기가 정상 작동하면:
- 매주 토요일 추첨 후 자동 수집
- 최신 회차 자동 감지 및 추가

