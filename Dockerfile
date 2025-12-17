#
# 1. 베이스 이미지: Python 3.12.7 slim 버전 (가볍고 보안에 좋음)
FROM python:3.12.7-slim

# 2. 환경 변수 설정
# PYTHONDONTWRITEBYTECODE: 파이썬 .pyc 파일 생성 방지 (디스크 절약)
# PYTHONUNBUFFERED: 로그가 버퍼링 없이 즉시 출력되도록 설정 (K8s 로그 확인용)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 필수 시스템 패키지 설치
# build-essential: 일부 파이썬 패키지 컴파일에 필요 (gcc 등)
# libgl1-mesa-glx: CNN 이미지 처리(OpenCV) 사용 시 필수 라이브러리
# curl: 컨테이너 헬스 체크용
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. 의존성 파일 복사 및 설치
# requirements.txt를 먼저 복사해야 소스코드 변경 시 캐시를 활용해 빌드 속도가 빨라짐
COPY requirements.txt .

# pip 업그레이드 및 라이브러리 설치 (--no-cache-dir로 이미지 용량 최소화)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. 소스 코드 전체 복사
COPY . .

# 7. 포트 노출 (FastAPI 기본 포트)
EXPOSE 8000

# 8. 서버 실행 명령
# host 0.0.0.0은 외부(K8s Ingress 등)에서 접속하기 위해 필수
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]