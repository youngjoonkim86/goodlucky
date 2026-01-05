"""
Feature Selection 스케줄러
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.feature_selection_service import FeatureSelectionService
import logging

logger = logging.getLogger(__name__)


def run_feature_selection():
    """변수 선택 파이프라인 실행"""
    db = SessionLocal()
    try:
        service = FeatureSelectionService(db)
        result = service.run_feature_selection()
        
        if result["status"] == "success":
            logger.info(f"Feature Selection 완료: {len(result['selected_features'])} features 선택")
        else:
            logger.error(f"Feature Selection 실패: {result.get('message')}")
    except Exception as e:
        logger.error(f"Feature Selection 스케줄러 오류: {e}", exc_info=True)
    finally:
        db.close()


def setup_feature_selection_scheduler():
    """Feature Selection 스케줄러 설정"""
    scheduler = BackgroundScheduler()
    
    # 매 회차: Quality/Correlation Filter (로또 추첨 후)
    scheduler.add_job(
        run_feature_selection,
        trigger=CronTrigger(day_of_week="sat", hour=22, minute=0),
        id="feature_selection_weekly",
        name="주간 변수 선택",
        replace_existing=True
    )
    
    # 월 1회: SHAP 재계산
    scheduler.add_job(
        run_feature_selection,
        trigger=CronTrigger(day=1, hour=2, minute=0),
        id="feature_selection_monthly",
        name="월간 변수 선택",
        replace_existing=True
    )
    
    # 분기: Feature 재선정
    scheduler.add_job(
        run_feature_selection,
        trigger=CronTrigger(month="*/3", day=1, hour=3, minute=0),
        id="feature_selection_quarterly",
        name="분기별 변수 선택",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Feature Selection 스케줄러 시작")
    
    return scheduler

