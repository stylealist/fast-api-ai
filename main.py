# app/main.py
import sys
import uvicorn
from fastapi import FastAPI
from core.eureka import eureka  # 분리한 eureka 가져오기
from core.config import settings    # 분리한 설정 가져오기
from routes.test.connect_test import router as test_router
from routes.estate.transactions import router as estate_router

# FastAPI 앱 생성 (lifespan 주입)
app = FastAPI(lifespan=eureka, root_path="/fast-api-ai")

# [핵심] 여기서 라우터를 앱에 등록합니다!
app.include_router(test_router, tags=["Connect Test"])
# 부동산 실거래(아파트 매매·전월세) 조회. estate 스키마를 읽기만 한다.
# ESTATE_DB_DSN 이 없으면 이 라우터만 503 이고 나머지는 그대로 동작한다.
app.include_router(estate_router, tags=["Estate"])

if __name__ == "__main__":
    # 포트 정보도 settings에서 가져옴
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)