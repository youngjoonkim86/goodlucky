# API 문서

## 기본 정보

- **Base URL**: `http://localhost:8000/api/v1`
- **API 버전**: v1
- **인증**: JWT (향후 구현)

## 응답 형식

모든 API는 JSON 형식으로 응답합니다.

### 성공 응답
```json
{
  "data": {...}
}
```

### 에러 응답
```json
{
  "detail": "에러 메시지"
}
```

## 엔드포인트

### 로또 API

#### 1. 당첨 이력 조회
```
GET /lotto/history
```

**Query Parameters:**
- `skip` (int, optional): 건너뛸 개수 (기본값: 0)
- `limit` (int, optional): 조회 개수 (기본값: 100, 최대: 1000)
- `draw_no` (int, optional): 특정 회차
- `start_date` (date, optional): 시작 날짜 (YYYY-MM-DD)
- `end_date` (date, optional): 종료 날짜 (YYYY-MM-DD)

**응답 예시:**
```json
[
  {
    "id": 1,
    "draw_no": 1000,
    "draw_date": "2024-01-06",
    "numbers": [1, 2, 3, 4, 5, 6],
    "bonus": 7,
    "first_prize_winners": 10,
    "first_prize_amount": 1000000000,
    "total_sales": 50000000000
  }
]
```

#### 2. 특정 회차 조회
```
GET /lotto/history/{draw_no}
```

**Path Parameters:**
- `draw_no` (int): 회차 번호

#### 3. 최신 당첨 정보
```
GET /lotto/latest
```

#### 4. 통계 정보
```
GET /lotto/statistics
```

**응답 예시:**
```json
{
  "total_draws": 1000,
  "latest_draw_no": 1000,
  "latest_draw_date": "2024-01-06",
  "number_frequency": {
    "1": 50,
    "2": 45,
    ...
  },
  "most_frequent_numbers": [
    [1, 50],
    [2, 45],
    ...
  ]
}
```

### 분석 API

#### 1. 환경변수 분석
```
GET /analytics/variables
```

**Query Parameters:**
- `start_date` (date, optional): 시작 날짜
- `end_date` (date, optional): 종료 날짜

#### 2. 번호별 출현 빈도
```
GET /analytics/frequency?limit=45
```

**Query Parameters:**
- `limit` (int, optional): 조회할 번호 개수 (기본값: 45)

#### 3. 패턴 분석
```
GET /analytics/patterns
```

**응답 예시:**
```json
{
  "total_draws": 1000,
  "consecutive_frequency": 0.3,
  "avg_odd_count": 3.2,
  "avg_sum": 150.5,
  "sum_range": {
    "min": 100,
    "max": 200
  }
}
```

#### 4. 상관관계 분석
```
GET /analytics/correlation
```

### 추천 API

#### 1. 추천 번호 생성
```
GET /recommendations/numbers
```

**Query Parameters:**
- `count` (int, optional): 추천 개수 (기본값: 5, 최대: 20)
- `include_weather` (bool, optional): 기상 데이터 포함 (기본값: true)
- `include_economic` (bool, optional): 경제 지표 포함 (기본값: true)

**응답 예시:**
```json
[
  {
    "numbers": [3, 11, 19, 27, 34, 42],
    "confidence": 0.73,
    "features": {
      "frequency_score": 0.65,
      "pattern_score": 0.70,
      "weather_idx": 0.24,
      "economic_idx": 0.15,
      "sum_score": 0.80,
      "odd_even_score": 0.90
    },
    "explanation": "과거 출현 빈도가 높은 번호를 포함했습니다. 역대 패턴과 유사한 조합입니다."
  }
]
```

#### 2. 번호 조합 신뢰도 계산
```
GET /recommendations/numbers/confidence?numbers=1,2,3,4,5,6
```

**Query Parameters:**
- `numbers` (string, required): 쉼표로 구분된 번호 (예: "1,2,3,4,5,6")

**응답 예시:**
```json
{
  "numbers": [1, 2, 3, 4, 5, 6],
  "confidence": 0.65,
  "features": {
    "frequency_score": 0.60,
    "pattern_score": 0.50,
    "weather_idx": 0.20,
    "economic_idx": 0.15
  },
  "explanation": "통계적 분석을 기반으로 추천되었습니다."
}
```

## 에러 코드

- `400`: Bad Request - 잘못된 요청
- `404`: Not Found - 리소스를 찾을 수 없음
- `500`: Internal Server Error - 서버 오류

## Rate Limiting

- 기본: 분당 60회 요청
- 향후 JWT 인증 기반으로 개별 제한 예정

## Swagger UI

API 문서는 다음 주소에서 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

