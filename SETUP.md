# 설치 및 실행 가이드

## 사전 요구사항

1. **Docker Desktop** 설치 및 실행
   - Windows: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치
   - 설치 후 Docker Desktop을 실행해야 합니다.

2. **Python 3.11+** (로컬 실행 시)
3. **Node.js 18+** (로컬 실행 시)

## 방법 1: Docker Compose로 실행 (권장)

### 1. Docker Desktop 실행 확인
- Windows 작업 표시줄에서 Docker Desktop 아이콘 확인
- 실행되지 않았다면 Docker Desktop을 시작하세요.

### 2. 환경변수 설정
```bash
# env.example 파일을 .env로 복사
cp env.example .env

# .env 파일을 편집하여 필요한 값 설정
# 특히 API 키가 필요한 경우:
# - OPENWEATHER_API_KEY
# - LOTTO_API_KEY
```

### 3. Docker Compose 실행
```bash
docker-compose up -d
```

### 4. 서비스 확인
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. 접속
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 6. 중지
```bash
docker-compose down
```

## 방법 2: 로컬에서 직접 실행

Docker Desktop을 사용하지 않고 로컬에서 실행하는 방법입니다.

### 1. 데이터베이스 설정

PostgreSQL, MongoDB, Redis를 로컬에 설치하거나 Docker로만 실행:

```bash
# 데이터베이스만 Docker로 실행
docker-compose up -d postgres mongodb redis
```

또는 로컬에 직접 설치:
- PostgreSQL: https://www.postgresql.org/download/
- MongoDB: https://www.mongodb.com/try/download/community
- Redis: https://redis.io/download

### 2. Backend 실행

```bash
cd backend

# 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
# .env 파일을 backend 폴더에 복사하거나 환경변수 설정

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend 실행

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정
# .env 파일 생성 또는 환경변수 설정
# VITE_API_URL=http://localhost:8000

# 개발 서버 실행
npm run dev
```

### 4. Data Collector 실행 (선택사항)

```bash
cd data-collector

# 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 스케줄러 실행
python -m schedulers.main
```

## 문제 해결

### Docker Desktop 오류
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**해결 방법:**
1. Docker Desktop이 실행 중인지 확인
2. Docker Desktop 재시작
3. Windows 재시작 (필요 시)

### 포트 충돌
포트가 이미 사용 중인 경우:
- `docker-compose.yml`에서 포트 번호 변경
- 또는 사용 중인 프로세스 종료

### 데이터베이스 연결 오류
- 데이터베이스가 실행 중인지 확인
- `.env` 파일의 연결 정보 확인
- 방화벽 설정 확인

## 개발 팁

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 데이터베이스 접속
```bash
# PostgreSQL
docker-compose exec postgres psql -U lotto_user -d lotto_db

# MongoDB
docker-compose exec mongodb mongosh -u lotto_user -p lotto_password
```

### 컨테이너 재시작
```bash
# 특정 서비스만 재시작
docker-compose restart backend

# 모든 서비스 재시작
docker-compose restart
```

