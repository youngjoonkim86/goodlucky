# 배포 가이드

이 프로젝트를 배포하는 방법을 안내합니다.

## 배포 옵션

### 옵션 1: Vercel 배포 (권장)

Vercel은 프론트엔드와 백엔드를 모두 무료로 호스팅할 수 있습니다.

#### 1. Vercel 계정 생성
- https://vercel.com 에서 GitHub 계정으로 로그인

#### 2. 프로젝트 가져오기
- Vercel 대시보드에서 "Add New Project" 클릭
- GitHub 저장소 `youngjoonkim86/goodlucky` 선택
- Import 클릭

#### 3. 환경 변수 설정
Vercel 대시보드의 Settings > Environment Variables에서 다음 변수 추가:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
MONGODB_URL=mongodb://host:port/dbname
REDIS_URL=redis://host:port
JWT_SECRET=your-secret-key
```

#### 4. 빌드 설정
- Root Directory: `/` (기본값)
- Build Command: `cd frontend && npm install && npm run build`
- Output Directory: `frontend/dist`

#### 5. 배포
- Deploy 버튼 클릭
- 배포 완료 후 제공되는 URL로 접근 가능

### 옵션 2: Railway 배포

Railway는 데이터베이스와 함께 전체 스택을 배포할 수 있습니다.

#### 1. Railway 계정 생성
- https://railway.app 에서 GitHub 계정으로 로그인

#### 2. 프로젝트 생성
- "New Project" > "Deploy from GitHub repo" 선택
- `youngjoonkim86/goodlucky` 선택

#### 3. 서비스 추가
- PostgreSQL 서비스 추가
- MongoDB 서비스 추가 (선택사항)
- Redis 서비스 추가 (선택사항)

#### 4. 환경 변수 설정
Railway 대시보드에서 환경 변수 설정

#### 5. 배포
- 자동으로 배포 시작
- 제공되는 URL로 접근 가능

### 옵션 3: Render 배포

#### 1. Render 계정 생성
- https://render.com 에서 GitHub 계정으로 로그인

#### 2. Web Service 생성
- "New" > "Web Service" 선택
- GitHub 저장소 연결
- Build Command: `cd frontend && npm install && npm run build`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 3. PostgreSQL 데이터베이스 추가
- "New" > "PostgreSQL" 선택

#### 4. 환경 변수 설정
Render 대시보드에서 환경 변수 설정

### 옵션 4: GitHub Pages (프론트엔드만)

프론트엔드만 정적 사이트로 배포할 수 있습니다.

#### 1. GitHub Actions 설정
`.github/workflows/deploy-pages.yml` 파일이 자동으로 생성됩니다.

#### 2. GitHub Pages 활성화
- 저장소 Settings > Pages
- Source: "GitHub Actions" 선택

#### 3. 백엔드 별도 배포 필요
- 백엔드는 별도 서버에 배포하고 프론트엔드 API URL 수정

## 빠른 배포 (Vercel CLI)

```bash
# Vercel CLI 설치
npm install -g vercel

# 로그인
vercel login

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

## 환경 변수 설정

배포 전 다음 환경 변수를 설정해야 합니다:

```bash
DATABASE_URL=postgresql://...
MONGODB_URL=mongodb://...
REDIS_URL=redis://...
JWT_SECRET=your-secret-key
OPENWEATHER_API_KEY=your-api-key (선택사항)
```

## 데이터베이스 마이그레이션

배포 후 데이터베이스 마이그레이션 실행:

```bash
# 로컬에서 실행
docker-compose -f docker-compose.minimal.yml exec backend alembic upgrade head

# 또는 배포된 서버에서
alembic upgrade head
```

## 접근 URL

배포 완료 후:
- **Vercel**: `https://goodlucky.vercel.app` (또는 커스텀 도메인)
- **Railway**: `https://your-app.railway.app`
- **Render**: `https://your-app.onrender.com`
- **GitHub Pages**: `https://youngjoonkim86.github.io/goodlucky`

## 문제 해결

### CORS 오류
- `backend/app/core/config.py`에서 `CORS_ORIGINS`에 배포된 프론트엔드 URL 추가

### 데이터베이스 연결 오류
- 환경 변수 `DATABASE_URL` 확인
- 데이터베이스 서비스가 실행 중인지 확인

### 빌드 실패
- Node.js 버전 확인 (18 이상 권장)
- Python 버전 확인 (3.11 이상 권장)
- 의존성 설치 오류 확인

