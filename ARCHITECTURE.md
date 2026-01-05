# 아키텍처 문서

## 시스템 개요

로또 번호 분석 및 추천 플랫폼은 환경변수를 고려한 데이터 기반 분석 및 추천 시스템입니다.

## 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (정형 데이터), MongoDB (비정형 데이터)
- **Cache**: Redis
- **ML Libraries**: scikit-learn, numpy, pandas

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **State Management**: Redux Toolkit
- **Charts**: Chart.js

### Data Collection
- **Scraping**: BeautifulSoup, Requests
- **Scheduler**: APScheduler
- **Database**: PostgreSQL

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Web Frontend │  │ Mobile App   │  │  API Gateway         │ │
│  │  (React)     │  │  (Future)    │  │  (FastAPI)           │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                      Backend Application                     │
│  ┌────────────────────────┐  ┌──────────────────────────────┐ │
│  │  Data Collection       │  │  Analytics & ML Engine       │ │
│  │  Scheduler/Workers     │  │  Model Serving                │ │
│  └────────────────────────┘  └──────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                 Data Layer / Storage / Message Queue          │
│  ┌────────────┐ ┌──────────────┐  ┌──────────────┐  ┌────────┐ │
│  │ PostgreSQL │ │ MongoDB      │  │ Redis Cache  │  │ Queue  │ │
│  └────────────┘ └──────────────┘  └──────────────┘  └────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 데이터 흐름

### 1. 데이터 수집
```
External APIs → Scrapers → Data Collector → PostgreSQL/MongoDB
```

### 2. 분석 및 추천
```
PostgreSQL → Analytics Service → ML Engine → Recommendation Service → API
```

### 3. 사용자 요청
```
Frontend → API Gateway → Backend Services → Database → Response
```

## 데이터베이스 스키마

### PostgreSQL (정형 데이터)

#### lotto_draws
- `id`: Primary Key
- `draw_no`: 회차 번호 (Unique)
- `draw_date`: 추첨일
- `numbers`: 당첨 번호 배열 (6개)
- `bonus`: 보너스 번호
- `first_prize_winners`: 1등 당첨자 수
- `first_prize_amount`: 1등 당첨금
- `total_sales`: 총 판매액
- `metadata`: 추가 메타데이터 (JSONB)

#### weather_features
- `id`: Primary Key
- `date`: 날짜 (Unique)
- `temp_max`, `temp_min`, `temp_avg`: 온도
- `humidity`: 습도
- `precipitation`: 강수량
- `wind_speed`: 풍속
- `weather_main`, `weather_description`: 날씨 상태

#### economic_features
- `id`: Primary Key
- `date`: 날짜 (Unique)
- `exchange_rate_usd`, `exchange_rate_eur`: 환율
- `kospi_index`, `kosdaq_index`: 주식 지수
- `interest_rate`: 기준금리
- `cpi`: 소비자물가지수
- `pmi`: 구매자지수
- `unemployment_rate`: 실업률

### MongoDB (비정형 데이터)
- 사용자 로그
- 세션 데이터
- 캐시 데이터

## API 엔드포인트

### 로또 API (`/api/v1/lotto`)
- `GET /history`: 당첨 이력 조회
- `GET /history/{draw_no}`: 특정 회차 조회
- `GET /latest`: 최신 당첨 정보
- `GET /statistics`: 통계 정보
- `POST /history`: 당첨 데이터 추가 (관리자)

### 분석 API (`/api/v1/analytics`)
- `GET /variables`: 환경변수별 영향도 분석
- `GET /frequency`: 번호별 출현 빈도
- `GET /patterns`: 패턴 분석
- `GET /correlation`: 상관관계 분석

### 추천 API (`/api/v1/recommendations`)
- `GET /numbers`: 추천 번호 생성
- `GET /numbers/confidence`: 번호 조합 신뢰도 계산

## ML 엔진

### 추천 알고리즘

1. **빈도 기반 가중치 샘플링**
   - 과거 출현 빈도를 가중치로 사용
   - 확률 분포 기반 샘플링

2. **패턴 분석**
   - 연속 번호 패턴
   - 홀짝 비율
   - 합계 범위

3. **환경변수 통합**
   - 기상 지수 계산
   - 경제 지수 계산
   - 가중치 합산

4. **신뢰도 계산**
   - 다중 특성 점수 가중 평균
   - 0.0 ~ 1.0 범위 정규화

## 보안

- JWT 인증 (향후 구현)
- API Rate Limiting
- CORS 설정
- 환경변수 기반 비밀번호 관리

## 배포

### Docker Compose
```bash
docker-compose up -d
```

### 개별 서비스
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm start`
- Data Collector: `python -m schedulers.main`

## 확장 계획

1. **Phase 2**: ML 모델 고도화 (TensorFlow/PyTorch)
2. **Phase 3**: 실시간 알림 시스템
3. **Phase 4**: 사용자 개인화 추천
4. **Phase 5**: 모바일 앱 (React Native)

