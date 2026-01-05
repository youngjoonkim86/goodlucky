# 데이터베이스 필요성 및 대안

## 데이터베이스가 필요한 이유

현재 플랫폼은 다음 데이터를 저장하고 분석합니다:

### 1. **로또 당첨 데이터** (PostgreSQL)
- 과거 모든 회차의 당첨 번호
- 통계 분석을 위한 히스토리 데이터
- 번호별 출현 빈도 계산

### 2. **기상 데이터** (PostgreSQL)
- 날짜별 기온, 습도, 강수량 등
- 환경변수 분석을 위한 데이터

### 3. **경제 지표** (PostgreSQL)
- 환율, 주식 지수, 금리 등
- 환경변수 분석을 위한 데이터

### 4. **캐시** (Redis)
- API 응답 캐싱
- 성능 최적화

## 최소 구성 옵션

### 옵션 1: PostgreSQL만 사용 (권장)

MongoDB와 Redis 없이도 기본 기능은 동작합니다:

```yaml
# docker-compose.minimal.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: lotto_user
      POSTGRES_PASSWORD: lotto_password
      POSTGRES_DB: lotto_db
    ports:
      - "5432:5432"
```

**필요한 작업:**
- MongoDB 관련 코드 제거 또는 옵셔널 처리
- Redis 관련 코드 제거 또는 옵셔널 처리

### 옵션 2: SQLite 사용 (가장 간단)

파일 기반 데이터베이스로 설정 없이 사용:

**장점:**
- 별도 서버 불필요
- 설정 간단
- 개발/테스트에 적합

**단점:**
- 동시 접속 제한
- 프로덕션에는 부적합

### 옵션 3: 메모리 기반 (데모용)

데이터베이스 없이 하드코딩된 샘플 데이터 사용:

**장점:**
- 설정 불필요
- 즉시 테스트 가능

**단점:**
- 데이터 저장 불가
- 실제 분석 불가능

## 추천: 최소 구성으로 시작

개발/테스트 단계에서는 **PostgreSQL만** 사용하는 것을 권장합니다.

MongoDB와 Redis는 나중에 추가할 수 있습니다.

