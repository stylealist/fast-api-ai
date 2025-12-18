# app/core/config.py

import os
# socket은 이제 필요 없으니 주석 처리하거나 지우셔도 됩니다.
# import socket 
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "fast-api-ai"
    PORT: int = 8000
    EUREKA_SERVER: str = "http://localhost:8761/eureka"
    
    INSTANCE_IP: str | None = os.getenv("POD_IP") 

    def model_post_init(self, __context):
        if not self.INSTANCE_IP:
            self.INSTANCE_IP = self._get_host_ip()

    def _get_host_ip(self):
        # [수정 전 - 이 코드가 10.10.10.55를 가져와서 문제입니다]
        # try:
        #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #     s.connect(("8.8.8.8", 80))
        #     ip = s.getsockname()[0]
        #     s.close()
        #     return ip
        # except Exception:
        #     return "localhost"

        # [수정 후 - 무조건 127.0.0.1 반환]
        # 로컬 개발(POD_IP 없음) 환경에서는 uvicorn이 기본적으로 127.0.0.1로 뜹니다.
        # 따라서 Eureka에도 127.0.0.1이라고 알려줘야 Gateway가 찾아올 수 있습니다.
        return "127.0.0.1"

settings = Settings()