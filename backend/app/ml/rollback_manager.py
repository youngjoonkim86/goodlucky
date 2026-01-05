"""
운영 안정성 로직 - Rollback 관리
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RollbackManager:
    """Feature Set 변경 시 성능 검증 및 Rollback 관리"""
    
    def __init__(self, tolerance: float = 0.02):
        """
        Args:
            tolerance: 성능 저하 허용 범위 (2% = 0.02)
        """
        self.tolerance = tolerance
        self.performance_history: list = []
    
    def validate_feature_set(
        self,
        old_performance: float,
        new_performance: float,
        metric: str = "accuracy"
    ) -> Dict[str, Any]:
        """
        Feature Set 변경 검증
        
        Args:
            old_performance: 이전 성능 점수
            new_performance: 새로운 성능 점수
            metric: 성능 지표명
        
        Returns:
            {
                "decision": "DEPLOY" or "ROLLBACK",
                "old_performance": float,
                "new_performance": float,
                "change": float,
                "reason": str
            }
        """
        if old_performance == 0:
            # 이전 성능이 없으면 무조건 배포
            decision = "DEPLOY"
            reason = "이전 성능 데이터 없음"
        else:
            # 성능 변화율 계산
            change_ratio = (new_performance - old_performance) / old_performance
            
            if change_ratio < -self.tolerance:
                # 성능 저하가 허용 범위를 넘으면 Rollback
                decision = "ROLLBACK"
                reason = f"성능 저하 {abs(change_ratio)*100:.2f}% (허용 범위: {self.tolerance*100}%)"
            else:
                decision = "DEPLOY"
                reason = f"성능 변화 {change_ratio*100:.2f}% (허용 범위 내)"
        
        result = {
            "decision": decision,
            "old_performance": old_performance,
            "new_performance": new_performance,
            "change": new_performance - old_performance,
            "change_ratio": (new_performance - old_performance) / old_performance if old_performance > 0 else 0,
            "metric": metric,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # 히스토리 저장
        self.performance_history.append(result)
        
        logger.info(f"Feature Set 검증: {decision} - {reason}")
        
        return result
    
    def get_performance_history(self, limit: int = 10) -> list:
        """성능 히스토리 조회"""
        return self.performance_history[-limit:]
    
    def calculate_performance(
        self,
        y_true: list,
        y_pred: list,
        metric: str = "accuracy"
    ) -> float:
        """
        성능 지표 계산
        
        Args:
            y_true: 실제 값
            y_pred: 예측 값
            metric: "accuracy", "mae", "mse", "r2"
        """
        import numpy as np
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        if metric == "accuracy":
            # 분류 정확도 (이진 분류 가정)
            if len(y_true) == 0:
                return 0.0
            return np.mean(y_true == y_pred)
        elif metric == "mae":
            return -mean_absolute_error(y_true, y_pred)  # 음수로 변환 (높을수록 좋음)
        elif metric == "mse":
            return -mean_squared_error(y_true, y_pred)
        elif metric == "r2":
            return r2_score(y_true, y_pred)
        else:
            logger.warning(f"알 수 없는 지표: {metric}, MAE 사용")
            return -mean_absolute_error(y_true, y_pred)

