# app/core/eureka.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from py_eureka_client import eureka_client
from core.config import settings  # 위에서 만든 설정 가져오기

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def eureka(app: FastAPI):
    # --- [Startup] Eureka 등록 ---
    logger.info(f"Initializing Eureka: {settings.EUREKA_SERVER} for {settings.APP_NAME}")
    
    await eureka_client.init_async(
        eureka_server=settings.EUREKA_SERVER,
        app_name=settings.APP_NAME,
        instance_port=settings.PORT,
        instance_host=settings.INSTANCE_IP,
        instance_ip=settings.INSTANCE_IP
    )
    logger.info("Eureka client initialized successfully.")
    
    yield  # 앱 실행 중...
    
    # --- [Shutdown] Eureka 해제 ---
    logger.info("Stopping Eureka client...")
    await eureka_client.stop_async()