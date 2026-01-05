"""
로또 번호 분석 및 추천 플랫폼 - Backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import router as api_router
from app.core.database import init_db

app = FastAPI(
    title="로또 번호 분석 및 추천 API",
    description="환경변수를 고려한 로또 번호 분석 및 추천 플랫폼",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    await init_db()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return JSONResponse({
        "message": "로또 번호 분석 및 추천 API",
        "version": "1.0.0",
        "docs": "/docs"
    })


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return JSONResponse({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

