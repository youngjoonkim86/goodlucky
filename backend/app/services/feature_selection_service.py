"""
Feature Selection Service - 변수 선택 서비스
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import logging

from app.models.lotto import LottoDraw
from app.models.weather import WeatherFeature
from app.models.economic import EconomicFeature
from app.ml.feature_pipeline import FeaturePipeline
from app.ml.rollback_manager import RollbackManager

logger = logging.getLogger(__name__)


class FeatureSelectionService:
    """변수 선택 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = FeaturePipeline()
        self.rollback_manager = RollbackManager()
        self.current_features: List[str] = []
        self.selection_log: Dict[str, Any] = {}
    
    def run_feature_selection(
        self,
        target: str = "sum_numbers",
        season: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        변수 선택 파이프라인 실행
        
        Args:
            target: 타겟 변수명
            season: 현재 시즌
        
        Returns:
            {
                "selected_features": List[str],
                "selection_log": Dict,
                "status": "success" or "error"
            }
        """
        try:
            # 데이터 로드
            lotto_df = self._load_lotto_data()
            weather_df = self._load_weather_data()
            economic_df = self._load_economic_data()
            
            # 특성 준비
            feature_df = self.pipeline.prepare_features(
                lotto_df,
                weather_df,
                economic_df
            )
            
            if feature_df.empty:
                return {
                    "selected_features": [],
                    "selection_log": {},
                    "status": "error",
                    "message": "특성 데이터가 없습니다."
                }
            
            # 파이프라인 실행
            selected, log = self.pipeline.run_pipeline(
                feature_df,
                target=target,
                season=season
            )
            
            self.current_features = selected
            self.selection_log = log
            
            return {
                "selected_features": selected,
                "selection_log": log,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Feature selection 오류: {e}", exc_info=True)
            return {
                "selected_features": [],
                "selection_log": {},
                "status": "error",
                "message": str(e)
            }
    
    def _load_lotto_data(self) -> pd.DataFrame:
        """로또 데이터 로드"""
        draws = self.db.query(LottoDraw).order_by(LottoDraw.draw_no).all()
        
        data = []
        for draw in draws:
            data.append({
                "draw_no": draw.draw_no,
                "draw_date": draw.draw_date,
                "numbers": draw.numbers,
                "bonus": draw.bonus,
                "sum_numbers": sum(draw.numbers) if draw.numbers else 0
            })
        
        return pd.DataFrame(data)
    
    def _load_weather_data(self) -> pd.DataFrame:
        """기상 데이터 로드"""
        weather = self.db.query(WeatherFeature).order_by(WeatherFeature.date).all()
        
        data = []
        for w in weather:
            data.append({
                "date": w.date,
                "avg_temp": w.temp_avg,
                "temp_max": w.temp_max,
                "temp_min": w.temp_min,
                "humidity": w.humidity,
                "precipitation": w.precipitation,
                "wind_speed": w.wind_speed
            })
        
        return pd.DataFrame(data)
    
    def _load_economic_data(self) -> pd.DataFrame:
        """경제 데이터 로드"""
        economic = self.db.query(EconomicFeature).order_by(EconomicFeature.date).all()
        
        data = []
        for e in economic:
            data.append({
                "date": e.date,
                "exchange_rate_usd": e.exchange_rate_usd,
                "exchange_rate_eur": e.exchange_rate_eur,
                "kospi_index": e.kospi_index,
                "kosdaq_index": e.kosdaq_index,
                "interest_rate": e.interest_rate,
                "cpi": e.cpi
            })
        
        return pd.DataFrame(data)
    
    def get_current_features(self) -> List[str]:
        """현재 활성화된 특성 목록"""
        return self.current_features
    
    def get_selection_log(self) -> Dict[str, Any]:
        """선택 로그 조회"""
        return self.selection_log
    
    def validate_and_deploy(
        self,
        old_features: List[str],
        new_features: List[str],
        test_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Feature Set 변경 검증 및 배포
        
        Args:
            old_features: 이전 특성 목록
            new_features: 새로운 특성 목록
            test_data: 테스트 데이터 (선택사항)
        
        Returns:
            검증 결과
        """
        # 간단한 검증 (실제로는 더 정교한 검증 필요)
        if test_data is not None:
            # 성능 비교 (예시)
            old_perf = 0.5  # TODO: 실제 성능 계산
            new_perf = 0.52  # TODO: 실제 성능 계산
            
            result = self.rollback_manager.validate_feature_set(
                old_perf,
                new_perf
            )
        else:
            # 데이터가 없으면 변경사항만 기록
            result = {
                "decision": "DEPLOY",
                "old_features": old_features,
                "new_features": new_features,
                "added": [f for f in new_features if f not in old_features],
                "removed": [f for f in old_features if f not in new_features],
                "timestamp": datetime.now().isoformat()
            }
        
        return result

