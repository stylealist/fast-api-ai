# app/main.py
import sys
import uvicorn
from fastapi import FastAPI
from core.eureka import eureka  # 분리한 eureka 가져오기
from core.config import settings    # 분리한 설정 가져오기

# FastAPI 앱 생성 (lifespan 주입)
app = FastAPI(lifespan=eureka, root_path="/fast-api-ai")

@app.get("/")
def read_root():
    return {
        "message": "FastAPI running on Kubernetes!",
        "python_version": sys.version,
        "instance_ip": settings.INSTANCE_IP  # 설정값 확인용
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # 포트 정보도 settings에서 가져옴
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)