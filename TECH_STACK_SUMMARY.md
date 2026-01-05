# 기술 스택 요약

## 필수 vs 선택사항

### ✅ **필수 구성 요소**

1. **PostgreSQL** (필수)
   - 로또 당첨 데이터 저장
   - 기상/경제 데이터 저장
   - 통계 분석에 필요

2. **Python Backend** (필수)
   - FastAPI 서버
   - 비즈니스 로직

3. **React Frontend** (필수)
   - 사용자 인터페이스

### ⚠️ **선택 구성 요소**

1. **MongoDB** (선택)
   - 사용자 로그 저장용
   - 없어도 기본 기능 동작

2. **Redis** (선택)
   - 캐싱으로 성능 향상
   - 없어도 동작 (단, 느릴 수 있음)

3. **RabbitMQ** (선택)
   - 메시지 큐
   - 현재 미사용

### ❌ **불필요한 구성 요소**

1. **LLM (Large Language Model)**
   - 현재 구조에서는 **불필요**
   - 통계/확률 기반 알고리즘 사용
   - LLM 추가 시 자연어 설명 등 고급 기능 가능하지만 필수 아님

2. **TensorFlow/PyTorch**
   - 현재는 사용하지 않음
   - 전통적인 ML (scikit-learn) 사용
   - 딥러닝 모델이 필요할 때만 추가

## 최소 구성

```bash
# PostgreSQL만으로도 동작 가능
docker-compose -f docker-compose.minimal.yml up -d
```

**포함:**
- ✅ PostgreSQL
- ✅ Backend
- ✅ Frontend

**제외:**
- ❌ MongoDB
- ❌ Redis
- ❌ RabbitMQ
- ❌ LLM

## 요약

| 구성 요소 | 필수 여부 | 이유 |
|----------|----------|------|
| PostgreSQL | ✅ 필수 | 데이터 저장 및 분석에 필요 |
| MongoDB | ⚠️ 선택 | 사용자 로그 등 고급 기능용 |
| Redis | ⚠️ 선택 | 캐싱으로 성능 향상 |
| LLM | ❌ 불필요 | 통계 기반으로 충분 |
| TensorFlow/PyTorch | ❌ 불필요 | 현재 미사용 |

**결론:** PostgreSQL만 있으면 기본 기능은 모두 동작합니다!

