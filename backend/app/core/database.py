"""
데이터베이스 연결 및 세션 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import redis

# PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# MongoDB
mongodb_client: AsyncIOMotorClient = None


async def get_mongodb():
    """MongoDB 클라이언트 반환"""
    global mongodb_client
    if mongodb_client is None:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    return mongodb_client[settings.MONGO_DB]


# Redis (옵셔널)
redis_client = None
try:
    if settings.REDIS_HOST:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
except Exception as e:
    print(f"⚠️ Redis 연결 실패 (옵셔널): {e}")
    redis_client = None


def get_db():
    """PostgreSQL 데이터베이스 세션 반환"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """데이터베이스 초기화"""
    # PostgreSQL 테이블 생성
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL 연결 완료")
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        raise
    
    # MongoDB 연결 확인 (옵셔널)
    try:
        if settings.MONGO_HOST:
            await get_mongodb()
            print("✅ MongoDB 연결 완료")
    except Exception as e:
        print(f"⚠️ MongoDB 연결 실패 (옵셔널): {e}")
    
    # Redis 연결 확인 (옵셔널)
    try:
        if redis_client:
            redis_client.ping()
            print("✅ Redis 연결 완료")
    except Exception as e:
        print(f"⚠️ Redis 연결 실패 (옵셔널): {e}")

