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
    
    # K8s Service DNS 또는 localhost
    service_name = os.getenv("SERVICE_NAME", "fast-api-ai")
    namespace = os.getenv("POD_NAMESPACE", "default")
    
    # K8s에서는 Service DNS, 로컬에서는 localhost
    if os.getenv("POD_NAMESPACE"):
        # K8s 환경
        host = f"{service_name}.{namespace}.svc.cluster.local"
        port = int(os.getenv("SERVICE_PORT", "80"))
        eureka_url = os.getenv("EUREKA_SERVER", "https://eureka.sj-lab.co.kr/eureka")
    else:
        # 로컬 환경
        host = "localhost"
        port = 8000
        eureka_url = "http://localhost:8761/eureka"

    logger.info(f"Initializing Eureka client with host: {host}, port: {port}, server: {eureka_url}")
    
    await eureka_client.init_async(
        eureka_server=eureka_url,
        app_name="fast-api-ai",
        instance_port=port,
        instance_host=host,
        instance_ip=host  # 도메인으로 등록
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

def get_host_ip():
    """
    현재 실행 중인 호스트의 IP 주소를 자동으로 감지합니다.
    K8s Pod 내부 또는 로컬 환경 모두에서 동작합니다.
    """
    try:
        # 외부 연결을 시뮬레이션하여 실제 사용되는 IP를 가져옴
        # (실제로 연결하지는 않음)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.warning(f"Failed to get IP address: {e}, falling back to localhost")
        return "localhost"

if __name__ == "__main__":
    logger.info("Starting FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=8000)