"""
Feature Registry - 변수 메타 관리
"""
from typing import Dict, Any

# Feature Registry 정의
FEATURE_REGISTRY: Dict[str, Dict[str, Any]] = {
    # 기상 변수
    "avg_temp": {
        "group": "weather",
        "type": "continuous",
        "min_history": 100,
        "seasonal": True,
        "critical": False,
        "description": "평균 기온"
    },
    "temp_max": {
        "group": "weather",
        "type": "continuous",
        "min_history": 100,
        "seasonal": True,
        "critical": False,
        "description": "최고 기온"
    },
    "temp_min": {
        "group": "weather",
        "type": "continuous",
        "min_history": 100,
        "seasonal": True,
        "critical": False,
        "description": "최저 기온"
    },
    "humidity": {
        "group": "weather",
        "type": "continuous",
        "min_history": 100,
        "seasonal": True,
        "critical": False,
        "description": "습도"
    },
    "precipitation": {
        "group": "weather",
        "type": "continuous",
        "min_history": 100,
        "seasonal": True,
        "critical": False,
        "description": "강수량"
    },
    "wind_speed": {
        "group": "weather",
        "type": "continuous",
        "min_history": 100,
        "seasonal": True,
        "critical": False,
        "description": "풍속"
    },
    
    # 경제 변수
    "exchange_rate_usd": {
        "group": "economic",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "USD 환율"
    },
    "exchange_rate_eur": {
        "group": "economic",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "EUR 환율"
    },
    "kospi_index": {
        "group": "economic",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "KOSPI 지수"
    },
    "kosdaq_index": {
        "group": "economic",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "KOSDAQ 지수"
    },
    "interest_rate": {
        "group": "economic",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "기준금리"
    },
    "cpi": {
        "group": "economic",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "소비자물가지수"
    },
    
    # 캘린더 변수
    "holiday_flag": {
        "group": "calendar",
        "type": "binary",
        "min_history": 50,
        "seasonal": False,
        "critical": True,
        "description": "공휴일 여부"
    },
    "day_of_week": {
        "group": "calendar",
        "type": "discrete",
        "min_history": 200,
        "seasonal": False,
        "critical": True,
        "description": "요일 (0=월요일)"
    },
    "month": {
        "group": "calendar",
        "type": "discrete",
        "min_history": 200,
        "seasonal": True,
        "critical": False,
        "description": "월 (1-12)"
    },
    "season": {
        "group": "calendar",
        "type": "discrete",
        "min_history": 200,
        "seasonal": True,
        "critical": False,
        "description": "계절 (spring/summer/fall/winter)"
    },
    
    # 구조 변수 (로또 번호 특성)
    "odd_count": {
        "group": "structure",
        "type": "discrete",
        "min_history": 200,
        "seasonal": False,
        "critical": True,
        "description": "홀수 개수"
    },
    "even_count": {
        "group": "structure",
        "type": "discrete",
        "min_history": 200,
        "seasonal": False,
        "critical": True,
        "description": "짝수 개수"
    },
    "sum_numbers": {
        "group": "structure",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": True,
        "description": "번호 합계"
    },
    "consecutive_count": {
        "group": "structure",
        "type": "discrete",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "연속 번호 개수"
    },
    "low_count": {
        "group": "structure",
        "type": "discrete",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "저번호 개수 (1-22)"
    },
    "high_count": {
        "group": "structure",
        "type": "discrete",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "고번호 개수 (23-45)"
    },
    
    # 통계 변수
    "number_frequency_avg": {
        "group": "statistics",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": True,
        "description": "번호별 평균 출현 빈도"
    },
    "number_frequency_max": {
        "group": "statistics",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "번호별 최대 출현 빈도"
    },
    "number_frequency_min": {
        "group": "statistics",
        "type": "continuous",
        "min_history": 200,
        "seasonal": False,
        "critical": False,
        "description": "번호별 최소 출현 빈도"
    },
}


def get_feature_meta(feature_name: str) -> Dict[str, Any]:
    """특성 메타데이터 조회"""
    return FEATURE_REGISTRY.get(feature_name, {})


def get_features_by_group(group: str) -> list:
    """그룹별 특성 목록 조회"""
    return [
        name for name, meta in FEATURE_REGISTRY.items()
        if meta.get("group") == group
    ]


def get_critical_features() -> list:
    """Critical 특성 목록 조회"""
    return [
        name for name, meta in FEATURE_REGISTRY.items()
        if meta.get("critical", False)
    ]


def get_seasonal_features() -> list:
    """Seasonal 특성 목록 조회"""
    return [
        name for name, meta in FEATURE_REGISTRY.items()
        if meta.get("seasonal", False)
    ]

