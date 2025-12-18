# app/main.py
import sys
from core.config import settings    # 분리한 설정 가져오기
from fastapi import FastAPI, APIRouter # 1. APIRouter 임포트

router = APIRouter(prefix="/test")

@router.get("/")
def read_root():
    return {
        "message": "FastAPI running on Kubernetes!",
        "python_version": sys.version,
        "instance_ip": settings.INSTANCE_IP  # 설정값 확인용
    }

@router.get("/health")
def health_check():
    return {"status": "ok"}
