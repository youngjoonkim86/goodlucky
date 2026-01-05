# Feature Selection 자동화 가이드

## 개요

환경변수 포함 변수 선택 자동화 로직이 구현되었습니다. 이 시스템은:

- ✅ 변수 과적합 방지
- ✅ 설명 가능성 확보 (SHAP 기반)
- ✅ 시즌/환경 변화에 대한 자동 적응
- ✅ 운영 안정성 (Rollback 기능)

## 아키텍처

```
Raw Features (로또, 기상, 경제 데이터)
   ↓
Feature Quality Filter (결측/상수 제거)
   ↓
Correlation & Redundancy Filter (중복 제거)
   ↓
Baseline Model Training (LightGBM)
   ↓
SHAP Importance Evaluation (변수 기여도)
   ↓
Stability Test (시간 안정성)
   ↓
Season / Environment Switch (시즌별 활성화)
   ↓
Active Feature Set 확정
```

## 주요 컴포넌트

### 1. Feature Registry (`feature_registry.py`)

변수 메타데이터 관리:
- 그룹 (weather, economic, calendar, structure, statistics)
- 타입 (continuous, binary, discrete)
- 최소 히스토리 요구사항
- 시즌별 활성화 여부
- Critical 여부

### 2. Feature Selector (`feature_selector.py`)

변수 선택 파이프라인:
- Quality Filter: 결측치/상수 변수 제거
- Correlation Filter: 높은 상관관계 변수 제거
- Temporal Stability: 시간 안정성 테스트
- Seasonal Switch: 시즌별 활성화

### 3. SHAP Evaluator (`shap_evaluator.py`)

변수 중요도 평가:
- Baseline 모델 학습 (LightGBM)
- SHAP 값 계산
- 변수 기여도 평가

### 4. Feature Pipeline (`feature_pipeline.py`)

전체 파이프라인 통합:
- Raw Features 준비
- 모든 필터링 단계 실행
- 최종 특성 선택

### 5. Rollback Manager (`rollback_manager.py`)

운영 안정성 관리:
- 성능 검증
- 자동 Rollback 결정

## 사용 방법

### API를 통한 실행

```bash
# 변수 선택 파이프라인 실행
POST /api/v1/features/select?target=sum_numbers&season=summer

# 현재 활성화된 특성 조회
GET /api/v1/features/current

# Feature Registry 조회
GET /api/v1/features/registry
```

### Python 코드에서 사용

```python
from app.services.feature_selection_service import FeatureSelectionService
from app.core.database import SessionLocal

db = SessionLocal()
service = FeatureSelectionService(db)

# 변수 선택 실행
result = service.run_feature_selection(
    target="sum_numbers",
    season="summer"
)

print(f"선택된 특성: {result['selected_features']}")
print(f"선택 로그: {result['selection_log']}")
```

## 스케줄링

자동 스케줄링이 설정되어 있습니다:

| 주기 | 작업 | 시간 |
|------|------|------|
| 매 회차 | Quality/Correlation Filter | 토요일 22:00 |
| 월 1회 | SHAP 재계산 | 매월 1일 02:00 |
| 분기 | Feature 재선정 | 분기 첫날 03:00 |

## 설정 파라미터

### FeatureSelector

- `threshold_missing`: 결측치 허용 비율 (기본: 0.3 = 30%)
- `correlation_threshold`: 상관관계 임계값 (기본: 0.9)
- `shap_threshold`: SHAP 중요도 임계값 (기본: 0.01)
- `stability_threshold`: 안정성 임계값 (기본: 0.3)

### RollbackManager

- `tolerance`: 성능 저하 허용 범위 (기본: 0.02 = 2%)

## Feature Registry 확장

새로운 변수를 추가하려면 `feature_registry.py`에 추가:

```python
FEATURE_REGISTRY["new_feature"] = {
    "group": "weather",
    "type": "continuous",
    "min_history": 100,
    "seasonal": True,
    "critical": False,
    "description": "새로운 특성 설명"
}
```

## 로그 및 설명 가능성

선택 로그는 다음 정보를 포함합니다:

```json
{
  "timestamp": "2024-01-05T08:00:00",
  "total_features": 25,
  "target": "sum_numbers",
  "steps": {
    "quality_filter": {
      "count": 20,
      "removed": ["feature1", "feature2"]
    },
    "correlation_filter": {
      "count": 18
    },
    "final_selection": {
      "count": 12,
      "selected": ["feature3", "feature4", ...],
      "stability_scores": {...},
      "shap_scores": {...}
    }
  }
}
```

## 다음 확장 가능 항목

1. **SHAP + PSI 기반 Drift Detection**
   - 데이터 분포 변화 감지
   - 자동 재학습 트리거

2. **Feature Group 단위 Enable/Disable**
   - 그룹별 일괄 활성화/비활성화

3. **추천 결과 설명**
   - "이 변수는 왜 쓰였는지" 자동 설명

4. **MLOps 연계**
   - MLflow + Feature Store 통합

## 주의사항

1. **SHAP 라이브러리 설치 필요**
   ```bash
   pip install shap
   ```

2. **충분한 데이터 필요**
   - 각 특성별 최소 히스토리 요구사항 확인
   - 데이터가 부족하면 특성이 제외됨

3. **성능 고려**
   - SHAP 계산은 시간이 걸릴 수 있음
   - 대량 데이터는 샘플링 고려

## 문제 해결

### SHAP 오류
- `pip install shap` 실행
- TreeExplainer 대신 일반 Explainer 사용

### 데이터 부족
- `min_history` 요구사항 확인
- 더 많은 데이터 수집 필요

### 성능 저하
- `stability_threshold` 조정
- `shap_threshold` 조정

