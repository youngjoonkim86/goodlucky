"""
Feature Selection Pipeline - 전체 자동화 파이프라인
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from app.ml.feature_selector import FeatureSelector
from app.ml.shap_evaluator import SHAPEvaluator
from app.ml.feature_registry import FEATURE_REGISTRY

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """전체 자동화 파이프라인"""
    
    def __init__(
        self,
        threshold_missing: float = 0.3,
        correlation_threshold: float = 0.9,
        shap_threshold: float = 0.01,
        stability_threshold: float = 0.3,
        model_type: str = "lightgbm"
    ):
        self.selector = FeatureSelector(
            threshold_missing=threshold_missing,
            correlation_threshold=correlation_threshold,
            shap_threshold=shap_threshold,
            stability_threshold=stability_threshold
        )
        self.evaluator = SHAPEvaluator(model_type=model_type)
        self.selected_features: List[str] = []
        self.selection_log: Dict[str, Any] = {}
    
    def prepare_features(
        self,
        lotto_df: pd.DataFrame,
        weather_df: Optional[pd.DataFrame] = None,
        economic_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Raw Features 준비
        로또, 기상, 경제 데이터를 결합하여 특성 데이터프레임 생성
        """
        features = []
        
        # 로또 데이터에서 구조 특성 추출
        if not lotto_df.empty:
            lotto_features = self._extract_lotto_features(lotto_df)
            features.append(lotto_features)
        
        # 기상 데이터
        if weather_df is not None and not weather_df.empty:
            weather_features = self._extract_weather_features(weather_df)
            features.append(weather_features)
        
        # 경제 데이터
        if economic_df is not None and not economic_df.empty:
            economic_features = self._extract_economic_features(economic_df)
            features.append(economic_features)
        
        # 캘린더 특성 추가
        calendar_features = self._extract_calendar_features(lotto_df)
        features.append(calendar_features)
        
        # 통계 특성 추가
        if not lotto_df.empty:
            stats_features = self._extract_statistics_features(lotto_df)
            features.append(stats_features)
        
        # 모든 특성 결합
        if features:
            feature_df = pd.concat(features, axis=1)
            # 날짜로 정렬
            if 'date' in feature_df.columns:
                feature_df = feature_df.sort_values('date').reset_index(drop=True)
            return feature_df
        else:
            return pd.DataFrame()
    
    def _extract_lotto_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """로또 데이터에서 구조 특성 추출"""
        features = pd.DataFrame()
        
        if 'numbers' in df.columns and 'draw_date' in df.columns:
            features['date'] = df['draw_date']
            
            # 홀짝 개수
            features['odd_count'] = df['numbers'].apply(
                lambda x: sum(1 for n in x if n % 2 == 1) if isinstance(x, list) else 0
            )
            features['even_count'] = 6 - features['odd_count']
            
            # 합계
            features['sum_numbers'] = df['numbers'].apply(
                lambda x: sum(x) if isinstance(x, list) else 0
            )
            
            # 연속 번호 개수
            features['consecutive_count'] = df['numbers'].apply(
                lambda x: self._count_consecutive(sorted(x)) if isinstance(x, list) else 0
            )
            
            # 고저 번호 개수
            features['low_count'] = df['numbers'].apply(
                lambda x: sum(1 for n in x if n <= 22) if isinstance(x, list) else 0
            )
            features['high_count'] = 6 - features['low_count']
        
        return features
    
    def _extract_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """기상 특성 추출"""
        features = pd.DataFrame()
        
        if 'date' in df.columns:
            features['date'] = df['date']
        
        weather_cols = ['avg_temp', 'temp_max', 'temp_min', 'humidity', 'precipitation', 'wind_speed']
        for col in weather_cols:
            if col in df.columns:
                features[col] = df[col]
        
        return features
    
    def _extract_economic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """경제 특성 추출"""
        features = pd.DataFrame()
        
        if 'date' in df.columns:
            features['date'] = df['date']
        
        economic_cols = [
            'exchange_rate_usd', 'exchange_rate_eur',
            'kospi_index', 'kosdaq_index', 'interest_rate', 'cpi'
        ]
        for col in economic_cols:
            if col in df.columns:
                features[col] = df[col]
        
        return features
    
    def _extract_calendar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """캘린더 특성 추출"""
        features = pd.DataFrame()
        
        if 'draw_date' in df.columns:
            dates = pd.to_datetime(df['draw_date'])
            features['date'] = dates
            features['day_of_week'] = dates.dt.dayofweek
            features['month'] = dates.dt.month
            features['season'] = dates.dt.month.map({
                12: 'winter', 1: 'winter', 2: 'winter',
                3: 'spring', 4: 'spring', 5: 'spring',
                6: 'summer', 7: 'summer', 8: 'summer',
                9: 'fall', 10: 'fall', 11: 'fall'
            })
            # 공휴일 여부 (간단한 예시, 실제로는 공휴일 API 필요)
            features['holiday_flag'] = 0  # TODO: 실제 공휴일 데이터 연동
        
        return features
    
    def _extract_statistics_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """통계 특성 추출"""
        features = pd.DataFrame()
        
        if 'numbers' in df.columns and 'draw_date' in df.columns:
            features['date'] = df['draw_date']
            
            # 번호별 출현 빈도 계산
            all_numbers = []
            for numbers in df['numbers']:
                if isinstance(numbers, list):
                    all_numbers.extend(numbers)
            
            from collections import Counter
            freq = Counter(all_numbers)
            
            # 각 회차의 번호들의 평균 빈도
            features['number_frequency_avg'] = df['numbers'].apply(
                lambda x: np.mean([freq.get(n, 0) for n in x]) if isinstance(x, list) else 0
            )
            features['number_frequency_max'] = df['numbers'].apply(
                lambda x: max([freq.get(n, 0) for n in x]) if isinstance(x, list) and x else 0
            )
            features['number_frequency_min'] = df['numbers'].apply(
                lambda x: min([freq.get(n, 0) for n in x]) if isinstance(x, list) and x else 0
            )
        
        return features
    
    def _count_consecutive(self, numbers: List[int]) -> int:
        """연속 번호 개수 계산"""
        if len(numbers) < 2:
            return 0
        
        consecutive = 0
        for i in range(len(numbers) - 1):
            if numbers[i+1] - numbers[i] == 1:
                consecutive += 1
        return consecutive
    
    def run_pipeline(
        self,
        feature_df: pd.DataFrame,
        target: str = "sum_numbers",
        season: Optional[str] = None
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        전체 파이프라인 실행
        
        Args:
            feature_df: 특성 데이터프레임
            target: 타겟 변수명
            season: 현재 시즌 (None이면 자동 감지)
        
        Returns:
            (selected_features, pipeline_log)
        """
        if feature_df.empty:
            logger.warning("특성 데이터프레임이 비어있습니다.")
            return [], {}
        
        pipeline_log = {
            "timestamp": datetime.now().isoformat(),
            "total_features": len(feature_df.columns),
            "target": target
        }
        
        # 타겟 변수 확인
        if target not in feature_df.columns:
            logger.warning(f"타겟 변수 {target}가 없습니다. 첫 번째 수치형 변수를 사용합니다.")
            numeric_cols = feature_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                target = numeric_cols[0]
            else:
                logger.error("타겟 변수를 찾을 수 없습니다.")
                return [], pipeline_log
        
        # 결측치 처리
        feature_df = feature_df.copy()
        feature_df[target] = feature_df[target].fillna(feature_df[target].mean())
        
        # 1-2단계: Quality & Correlation Filter
        features = self.selector.quality_filter(feature_df)
        features = self.selector.correlation_filter(feature_df, features)
        
        if len(features) == 0:
            logger.warning("필터링 후 특성이 없습니다.")
            return [], pipeline_log
        
        # 3-4단계: Baseline Model & SHAP
        X = feature_df[features].fillna(0)
        y = feature_df[target]
        
        try:
            self.evaluator.train_baseline(X, y)
            shap_scores = self.evaluator.calculate_importance(X)
        except Exception as e:
            logger.error(f"SHAP 평가 오류: {e}")
            shap_scores = {}
        
        pipeline_log["shap_scores"] = shap_scores
        
        # 5-7단계: Stability, Seasonal, Final Selection
        selected, selection_log = self.selector.select_features(
            feature_df,
            target,
            season=season,
            shap_scores=shap_scores
        )
        
        self.selected_features = selected
        self.selection_log = {**pipeline_log, **selection_log}
        
        logger.info(f"Pipeline 완료: {len(selected)} features 선택됨")
        
        return selected, self.selection_log

