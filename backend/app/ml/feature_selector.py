"""
Feature Selection Pipeline - 변수 선택 자동화
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from app.ml.feature_registry import (
    FEATURE_REGISTRY,
    get_feature_meta,
    get_critical_features
)

logger = logging.getLogger(__name__)


class FeatureSelector:
    """변수 선택 자동화 파이프라인"""
    
    def __init__(
        self,
        threshold_missing: float = 0.3,
        correlation_threshold: float = 0.9,
        shap_threshold: float = 0.01,
        stability_threshold: float = 0.3
    ):
        self.threshold_missing = threshold_missing
        self.correlation_threshold = correlation_threshold
        self.shap_threshold = shap_threshold
        self.stability_threshold = stability_threshold
    
    def quality_filter(self, df: pd.DataFrame) -> List[str]:
        """
        1단계: Feature Quality Filter
        결측/상수/의미 없는 변수 제거
        """
        valid_features = []
        
        for col in df.columns:
            # 결측치 비율 확인
            missing_ratio = df[col].isna().mean()
            if missing_ratio > self.threshold_missing:
                logger.debug(f"Feature {col} 제거: 결측치 비율 {missing_ratio:.2%} > {self.threshold_missing:.2%}")
                continue
            
            # 상수 변수 확인
            if df[col].nunique() <= 1:
                logger.debug(f"Feature {col} 제거: 상수 변수")
                continue
            
            # 최소 히스토리 확인
            meta = get_feature_meta(col)
            min_history = meta.get("min_history", 0)
            if len(df) < min_history:
                logger.debug(f"Feature {col} 제거: 데이터 부족 ({len(df)} < {min_history})")
                continue
            
            valid_features.append(col)
        
        logger.info(f"Quality Filter: {len(df.columns)} -> {len(valid_features)} features")
        return valid_features
    
    def correlation_filter(self, df: pd.DataFrame, features: List[str]) -> List[str]:
        """
        2단계: 상관성 & 중복 제거
        동일 정보 변수 중 대표만 유지
        """
        if len(features) <= 1:
            return features
        
        # 수치형 변수만 상관관계 계산
        numeric_features = [
            f for f in features
            if df[f].dtype in ['int64', 'float64']
        ]
        
        if len(numeric_features) <= 1:
            return features
        
        try:
            corr = df[numeric_features].corr().abs()
            upper = corr.where(
                np.triu(np.ones(corr.shape), k=1).astype(bool)
            )
            
            # 높은 상관관계를 가진 변수 제거
            drop = []
            for col in upper.columns:
                if any(upper[col] > self.correlation_threshold):
                    drop.append(col)
            
            # Critical 변수는 보호
            critical = get_critical_features()
            drop = [d for d in drop if d not in critical]
            
            remaining = [f for f in features if f not in drop]
            
            logger.info(f"Correlation Filter: {len(features)} -> {len(remaining)} features (제거: {drop})")
            return remaining
        except Exception as e:
            logger.warning(f"Correlation filter 오류: {e}, 모든 변수 유지")
            return features
    
    def temporal_stability(
        self,
        df: pd.DataFrame,
        feature: str,
        target: str,
        window: int = 50
    ) -> float:
        """
        5단계: 시간 안정성 테스트
        특정 기간에만 의미 있는 변수 제거
        """
        if len(df) < window * 2:
            # 데이터가 부족하면 안정성 점수 0 (안정적이라고 가정)
            return 0.0
        
        scores = []
        for i in range(window, len(df), window):
            slice_df = df.iloc[i-window:i]
            
            if feature not in slice_df.columns or target not in slice_df.columns:
                continue
            
            try:
                # 상관관계 계산
                if slice_df[feature].dtype in ['int64', 'float64']:
                    corr = slice_df[feature].corr(slice_df[target])
                    if not np.isnan(corr):
                        scores.append(abs(corr))
            except Exception:
                continue
        
        if len(scores) < 2:
            return 0.0
        
        # 표준편차가 낮을수록 안정적
        stability_score = np.std(scores)
        return stability_score
    
    def seasonal_switch(self, feature: str, season: Optional[str] = None) -> bool:
        """
        6단계: 시즌/환경 자동 스위칭
        """
        meta = get_feature_meta(feature)
        
        # Seasonal이 False면 항상 활성
        if not meta.get("seasonal", False):
            return True
        
        # Seasonal이 True면 시즌 확인
        if season is None:
            # 현재 시즌 자동 감지
            month = datetime.now().month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "fall"
        
        # 시즌별 활성화 규칙 (필요시 확장)
        seasonal_features = {
            "summer": ["avg_temp", "temp_max", "humidity", "precipitation"],
            "winter": ["avg_temp", "temp_min"],
            "spring": ["avg_temp", "precipitation"],
            "fall": ["avg_temp", "precipitation"]
        }
        
        active_features = seasonal_features.get(season, [])
        return feature in active_features or meta.get("critical", False)
    
    def select_features(
        self,
        df: pd.DataFrame,
        target: str,
        season: Optional[str] = None,
        shap_scores: Optional[Dict[str, float]] = None
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        7단계: 최종 Feature Selection
        
        Returns:
            (selected_features, selection_log)
        """
        selection_log = {
            "timestamp": datetime.now().isoformat(),
            "total_features": len(df.columns),
            "steps": {}
        }
        
        # 1단계: Quality Filter
        features = self.quality_filter(df)
        selection_log["steps"]["quality_filter"] = {
            "count": len(features),
            "removed": [f for f in df.columns if f not in features]
        }
        
        # 2단계: Correlation Filter
        features = self.correlation_filter(df, features)
        selection_log["steps"]["correlation_filter"] = {
            "count": len(features)
        }
        
        # 3-4단계: SHAP 점수 확인 (외부에서 계산된 경우)
        if shap_scores is None:
            shap_scores = {}
        
        # 5-6단계: Stability & Seasonal Filter
        selected = []
        stability_scores = {}
        
        for feature in features:
            meta = get_feature_meta(feature)
            
            # SHAP 점수 확인
            shap_score = shap_scores.get(feature, 0.0)
            if shap_score < self.shap_threshold and not meta.get("critical", False):
                logger.debug(f"Feature {feature} 제거: SHAP 점수 {shap_score:.4f} < {self.shap_threshold}")
                continue
            
            # 시간 안정성 확인
            stability = self.temporal_stability(df, feature, target)
            stability_scores[feature] = stability
            if stability > self.stability_threshold:
                logger.debug(f"Feature {feature} 제거: 안정성 점수 {stability:.4f} > {self.stability_threshold}")
                continue
            
            # 시즌 스위칭 확인
            if not self.seasonal_switch(feature, season):
                logger.debug(f"Feature {feature} 제거: 현재 시즌 비활성")
                continue
            
            selected.append(feature)
        
        selection_log["steps"]["final_selection"] = {
            "count": len(selected),
            "selected": selected,
            "stability_scores": stability_scores,
            "shap_scores": {k: v for k, v in shap_scores.items() if k in selected}
        }
        
        logger.info(f"Feature Selection 완료: {len(df.columns)} -> {len(selected)} features")
        
        return selected, selection_log

