# 빠른 시작 가이드 (최소 구성)

## 데이터베이스가 필요한가요?

**짧은 답변:** 네, **PostgreSQL은 필수**입니다. 하지만 MongoDB와 Redis는 선택사항입니다.

## 최소 구성으로 시작하기

### 1. PostgreSQL만 실행 (가장 간단)

```bash
# 최소 구성으로 실행 (PostgreSQL만)
docker-compose -f docker-compose.minimal.yml up -d
```

이렇게 하면:
- ✅ PostgreSQL만 실행
- ✅ Backend와 Frontend 실행
- ❌ MongoDB 없음 (사용자 로그 등은 저장 안 됨)
- ❌ Redis 없음 (캐시 없음, 성능은 약간 느릴 수 있음)

### 2. 데이터베이스 없이 테스트하고 싶다면?

현재 구조상 **데이터베이스는 필수**입니다. 왜냐하면:

1. **로또 당첨 데이터 저장**: 과거 회차 데이터가 있어야 분석 가능
2. **통계 계산**: 번호별 출현 빈도 등 계산에 필요
3. **추천 알고리즘**: 과거 데이터 기반으로 추천 생성

**하지만**, 개발 초기에는:

### 옵션 A: 샘플 데이터로 시작

1. PostgreSQL 실행
2. 샘플 데이터 삽입 스크립트 실행
3. 기본 기능 테스트

### 옵션 B: SQLite로 변경 (고급)

PostgreSQL 대신 SQLite 사용 (파일 기반, 서버 불필요)

## 추천 방법

**개발/테스트 단계:**
```bash
# PostgreSQL만 실행 (최소 구성)
docker-compose -f docker-compose.minimal.yml up -d
```

**프로덕션 준비:**
```bash
# 전체 구성 (PostgreSQL + MongoDB + Redis)
docker-compose up -d
```

## 데이터베이스 없이도 동작하게 만들려면?

코드 수정이 필요합니다:
- 하드코딩된 샘플 데이터 사용
- 메모리 기반 저장소 사용
- 파일 기반 저장소 사용

하지만 이렇게 하면 **실제 분석 기능은 사용할 수 없습니다**.

## 결론

- **PostgreSQL은 필수**: 로또 데이터 저장 및 분석에 필요
- **MongoDB는 선택**: 사용자 로그 등 고급 기능용
- **Redis는 선택**: 캐싱으로 성능 향상용

**최소 구성으로 시작하려면:**
```bash
docker-compose -f docker-compose.minimal.yml up -d
```

