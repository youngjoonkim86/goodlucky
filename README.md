# 로또 번호 분석 및 추천 플랫폼 (GoodLucky)

[![Deploy](https://github.com/youngjoonkim86/goodlucky/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/youngjoonkim86/goodlucky/actions/workflows/deploy-pages.yml)

**라이브 데모**: [배포된 페이지](https://youngjoonkim86.github.io/goodlucky) (GitHub Pages)

환경변수까지 고려한 데이터 수집 → 저장 → 분석 → 추천 → UI/UX 제공까지 전주기(End-to-End)를 포괄하는 로또 번호 분석 및 추천 플랫폼입니다.

## 🌐 배포된 사이트

- **GitHub Pages**: https://youngjoonkim86.github.io/goodlucky
- **GitHub 저장소**: https://github.com/youngjoonkim86/goodlucky

배포 방법은 [DEPLOYMENT.md](DEPLOYMENT.md)를 참고하세요.

## 🏗️ 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Web Frontend │  │ Mobile App   │  │  API Gateway         │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                      Backend Application                     │
│  ┌────────────────────────┐  ┌──────────────────────────────┐ │
│  │  Data Collection       │  │  Analytics & ML Engine       │
│  │  Scheduler/Workers     │  │  Model Serving                │
│  └────────────────────────┘  └──────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                 Data Layer / Storage / Message Queue          │
│  ┌────────────┐ ┌──────────────┐  ┌──────────────┐  ┌────────┐ │
│  │ RDBMS      │ │ NoSQL        │  │ Data Warehouse│  │ Queue │ │
│  └────────────┘ └──────────────┘  └──────────────┘  └────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 📁 프로젝트 구조

```
lotto_dev/
├── backend/                 # Backend API 서버
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   ├── models/         # 데이터베이스 모델
│   │   ├── services/       # 비즈니스 로직
│   │   ├── ml/             # ML 엔진
│   │   └── core/           # 설정, 보안 등
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── store/
│   ├── package.json
│   └── Dockerfile
├── data-collector/         # 데이터 수집 레이어
│   ├── scrapers/
│   ├── schedulers/
│   └── requirements.txt
├── docker-compose.yml      # 전체 인프라 구성
├── .env.example           # 환경변수 예시
└── README.md
```

## 🚀 빠른 시작

### 사전 요구사항

- **Docker Desktop** (Docker Compose 사용 시 필수)
- Python 3.11+ (로컬 실행 시)
- Node.js 18+ (로컬 실행 시)

### 설치 및 실행

#### 방법 1: Docker Compose로 실행 (권장)

**⚠️ 중요: Docker Desktop이 실행 중이어야 합니다!**

1. **Docker Desktop 실행 확인**
   - Windows 작업 표시줄에서 Docker Desktop 아이콘 확인
   - 실행되지 않았다면 Docker Desktop을 시작하세요.

2. **환경변수 설정**
```bash
cp env.example .env
# .env 파일을 편집하여 필요한 API 키 등을 설정
```

3. **Docker Compose로 전체 스택 실행**
```bash
docker-compose up -d
```

4. **서비스 확인**
```bash
docker-compose ps
```

#### 방법 2: 최소 구성으로 실행 (PostgreSQL만)

MongoDB와 Redis 없이 기본 기능만 테스트:

```bash
docker-compose -f docker-compose.minimal.yml up -d
```

#### 방법 3: 로컬에서 직접 실행

Docker Desktop 없이 실행하려면 [SETUP.md](SETUP.md)를 참고하세요.

```bash
# 데이터베이스만 Docker로 실행
docker-compose -f docker-compose.db-only.yml up -d

# Backend 실행 (별도 터미널)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend 실행 (별도 터미널)
cd frontend
npm install
npm start
```

3. **개별 서비스 실행**

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm start
```

Data Collector:
```bash
cd data-collector
pip install -r requirements.txt
python -m schedulers.main
```

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (필수), MongoDB (선택), Redis (선택)
- **ML**: scikit-learn, numpy, pandas (통계/확률 기반)
- **LLM**: 불필요 (현재 구조는 통계 기반)

### Frontend
- **Framework**: React + TypeScript
- **State Management**: Redux
- **Charting**: Chart.js / D3.js

### Data Collection
- **Scraping**: BeautifulSoup, Selenium
- **Scheduler**: Apache Airflow / cron
- **Queue**: RabbitMQ / Kafka

### DevOps
- **Container**: Docker, Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## 📊 주요 기능

- ✅ 과거 로또 당첨 데이터 수집
- ✅ 환경변수(기상, 경제, 일정) 연동
- ✅ 다수 알고리즘 기반 분석/학습
- ✅ 추천 번호 생성 및 신뢰도 제공
- ✅ 웹 UI 제공
- ✅ 실시간/배치 분석

## 📝 API 문서

서버 실행 후 다음 주소에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 보안

- API Rate Limiting
- JWT 인증
- 데이터 암호화 (at rest/in transit)
- GDPR/Privacy 고려

## 📈 로드맵

- [x] Phase 1: 데이터 수집 + 기본 통계 분석
- [ ] Phase 2: ML 기반 예측 + 환경변수 통합
- [ ] Phase 3: 사용자 추천 인터페이스
- [ ] Phase 4: 실시간 알림/Push
- [ ] Phase 5: 사용자 개인화 추천

## 📄 라이선스

MIT License

