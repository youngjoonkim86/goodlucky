"""
SHAP 기반 변수 기여도 평가
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Any
import logging

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP 라이브러리가 설치되지 않았습니다. pip install shap 필요")

from sklearn.ensemble import RandomForestRegressor
from lightgbm import LGBMRegressor

logger = logging.getLogger(__name__)


class SHAPEvaluator:
    """SHAP 기반 변수 중요도 평가"""
    
    def __init__(self, model_type: str = "lightgbm"):
        """
        Args:
            model_type: "lightgbm" or "random_forest"
        """
        self.model_type = model_type
        self.model = None
        self.explainer = None
    
    def train_baseline(self, X: pd.DataFrame, y: pd.Series):
        """
        3단계: 기준 모델 학습
        복잡한 모델 사용 금지 (의도적)
        """
        if self.model_type == "lightgbm":
            self.model = LGBMRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                random_state=42,
                verbose=-1
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=200,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            )
        
        self.model.fit(X, y)
        logger.info(f"Baseline model 학습 완료 ({self.model_type})")
        return self.model
    
    def calculate_importance(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
        use_tree_explainer: bool = True
    ) -> Dict[str, float]:
        """
        4단계: SHAP 기반 변수 기여도 평가
        
        Args:
            X: 특성 데이터
            y: 타겟 데이터 (모델이 없을 경우 학습용)
            use_tree_explainer: TreeExplainer 사용 여부 (더 빠름)
        
        Returns:
            {feature_name: importance_score}
        """
        if not SHAP_AVAILABLE:
            logger.warning("SHAP 미설치, 대체 방법 사용")
            return self._fallback_importance(X, y)
        
        # 모델이 없으면 학습
        if self.model is None:
            if y is None:
                raise ValueError("모델이 없고 y도 제공되지 않았습니다.")
            self.train_baseline(X, y)
        
        try:
            # TreeExplainer 사용 (더 빠름)
            if use_tree_explainer and hasattr(self.model, 'tree_'):
                explainer = shap.TreeExplainer(self.model)
            else:
                # 일반 Explainer (모든 모델 지원)
                explainer = shap.Explainer(self.model, X)
            
            # SHAP 값 계산
            shap_values = explainer(X)
            
            # 중요도 계산 (절대값 평균)
            if isinstance(shap_values, shap.Explanation):
                importance = np.abs(shap_values.values).mean(axis=0)
            else:
                importance = np.abs(shap_values).mean(axis=0)
            
            importance_dict = dict(zip(X.columns, importance))
            
            logger.info(f"SHAP 중요도 계산 완료: {len(importance_dict)} features")
            return importance_dict
            
        except Exception as e:
            logger.error(f"SHAP 계산 오류: {e}, 대체 방법 사용")
            return self._fallback_importance(X, y)
    
    def _fallback_importance(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """
        SHAP 사용 불가 시 대체 방법
        - 모델의 feature_importances_ 사용
        - 또는 상관관계 기반
        """
        if self.model is not None and hasattr(self.model, 'feature_importances_'):
            # 모델의 feature importance 사용
            importance = self.model.feature_importances_
            return dict(zip(X.columns, importance))
        
        elif y is not None:
            # 상관관계 기반 중요도
            importance = {}
            for col in X.columns:
                try:
                    corr = abs(X[col].corr(y))
                    importance[col] = corr if not np.isnan(corr) else 0.0
                except Exception:
                    importance[col] = 0.0
            return importance
        
        else:
            # 균등 분배
            return {col: 1.0 / len(X.columns) for col in X.columns}
    
    def get_explanation(
        self,
        X: pd.DataFrame,
        instance_idx: int = 0
    ) -> Dict[str, Any]:
        """
        특정 인스턴스에 대한 SHAP 설명 생성
        """
        if not SHAP_AVAILABLE or self.model is None:
            return {"error": "SHAP 또는 모델이 없습니다."}
        
        try:
            explainer = shap.TreeExplainer(self.model) if hasattr(self.model, 'tree_') else shap.Explainer(self.model, X)
            shap_values = explainer(X.iloc[[instance_idx]])
            
            if isinstance(shap_values, shap.Explanation):
                values = shap_values.values[0]
                base_value = shap_values.base_values[0] if hasattr(shap_values, 'base_values') else 0
            else:
                values = shap_values[0]
                base_value = 0
            
            explanation = {
                "base_value": float(base_value),
                "feature_contributions": dict(zip(X.columns, values.tolist())),
                "prediction": float(self.model.predict(X.iloc[[instance_idx]])[0])
            }
            
            return explanation
        except Exception as e:
            logger.error(f"SHAP 설명 생성 오류: {e}")
            return {"error": str(e)}

