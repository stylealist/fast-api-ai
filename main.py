# app/main.py
import sys
import uvicorn
from fastapi import FastAPI
from core.eureka import eureka  # 분리한 eureka 가져오기
from core.config import settings    # 분리한 설정 가져오기
from routes.test.connect_test import router as test_router

# FastAPI 앱 생성 (lifespan 주입)
app = FastAPI(lifespan=eureka, root_path="/fast-api-ai")

# [핵심] 여기서 라우터를 앱에 등록합니다!
app.include_router(test_router, tags=["Connect Test"])

if __name__ == "__main__":
    # 포트 정보도 settings에서 가져옴
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)