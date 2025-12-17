import os
import sys
from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from py_eureka_client import eureka_client
import uvicorn
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Startup
    
    # 1. 환경변수에서 값을 가져오고, 없으면(로컬이면) 기본값을 사용
    # K8s에서는 "POD_IP"를, 로컬에서는 "localhost"를 사용
    host_ip = os.getenv("POD_IP", "localhost") 
    
    # K8s에서는 실제 Eureka 주소를, 로컬에서는 로컬 Eureka 주소를 사용
    eureka_url = os.getenv("EUREKA_SERVER", "http://localhost:8761/eureka")
    
    port = 8000

    logger.info(f"Initializing Eureka client with host: {host_ip}, port: {port}, server: {eureka_url}")
    
    await eureka_client.init_async(
        eureka_server=eureka_url,  # 변수로 교체
        app_name="fast-api-ai",
        instance_port=port,
        instance_host=host_ip,     # 변수로 교체
        instance_ip=host_ip
    )
    logger.info("Eureka client initialized")
    yield
    # Shutdown
    logger.info("Stopping Eureka client")
    await eureka_client.stop_async()


app = FastAPI(lifespan=lifespan, root_path="/fast-api-ai")

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

if __name__ == "__main__":
    logger.info("Starting FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=8000)