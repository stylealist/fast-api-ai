import sys
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    # 현재 파이썬 버전을 출력하여 3.12.7이 맞는지 확인
    return {
        "message": "FastAPI running on Kubernetes!",
        "python_version": sys.version
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}