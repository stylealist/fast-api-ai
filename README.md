# fast-api-ai — MSA 생태계 연동 Python AI/RAG 마이크로서비스

`fast-api-ai`는 Spring Cloud 기반 마이크로서비스 아키텍처(MSA) 생태계에 Python 환경을 연동하기 위해 구축된 FastAPI 마이크로서비스입니다. Netflix Eureka를 통한 동적 서비스 등록 및 Spring Cloud Gateway 라우팅 규격을 준수하며, 향후 시설물 점검 데이터에 대한 AI 요약, 분류 및 RAG(검색 증강 생성) 기능을 담당할 백엔드 서비스입니다.

---

## 1. 서비스 역할 및 핵심 책임

- **Polyglot MSA 연동**: Java/Spring 중심의 MSA 인프라(Spring Cloud Gateway, Netflix Eureka)와 완벽히 호환되는 Python 백엔드 인터페이스 제공.
- **동적 수명 주기 관리(Lifespan Management)**: FastAPI의 비동기 수명 주기(`lifespan`)를 활용하여 서비스 기동 시 Eureka 레지스트리에 인스턴스를 자동 등록하고, 종료 시 정상 해제(Unregister)하여 좀비 인스턴스 발생을 방지.
- **AI/ML 파이프라인 기반 인프라**: 시설물 현장 음성 메모 STT 요약, 이상 상태 텍스트 분류, 임베딩 기반 유사 사례 검색 등 향후 AI 워크로드를 처리할 수 있는 모듈화된 아키텍처 제공.

---

## 2. 기술 스택

- **언어 및 런타임**: Python 3.12, Uvicorn (ASGI Server)
- **웹 프레임워크**: FastAPI
- **설정 및 유효성 검증**: Pydantic Settings
- **서비스 디스커버리**: `py-eureka-client`
- **배포 환경**: Docker, Kubernetes (ClusterIP 80 -> 8000), Helm, Jenkins CI, ArgoCD (GitOps)

---

## 3. 시스템 아키텍처 및 라우팅 구조

```
[클라이언트 브라우저]
       │
       ▼ (/fast-api-ai/**)
[sj-lab-apigateway] (:8100) ──서비스 조회──> [Eureka Server] (:8761)
       │ (lb://FAST-API-AI)                       ▲
       ▼                                         │ py-eureka-client
[fast-api-ai] (:8000) ───────────────────────────┘
  ├── core/eureka.py  (비동기 등록/해제)
  ├── core/config.py  (환경변수 및 설정)
  └── routes/         (도메인별 API 엔드포인트)
```

### 경로 처리 규칙 (Path Transparency)
- Spring Cloud Gateway의 기본 정책인 "경로 유지(Preserve Path)"를 지원하기 위해 `FastAPI(root_path="/fast-api-ai")`를 적용합니다.
- 게이트웨이 경유 시 Swagger 문서(`/fast-api-ai/docs`)와 OpenAPI 스키마가 올바른 URL 프리픽스를 인식합니다.

---

## 4. 핵심 엔지니어링 구현 상세

### 4.1 비동기 수명 주기(Lifespan) 기반 Eureka 등록 및 해제
Spring Cloud Eureka와의 일관된 인스턴스 라이프사이클을 보장하기 위해 `@asynccontextmanager` 수명 주기를 구현했습니다.

```python
# core/eureka.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.EUREKA_SERVER:
        await eureka_client.init_async(
            eureka_server=settings.EUREKA_SERVER,
            app_name=settings.APP_NAME,
            instance_port=settings.PORT,
            instance_host=settings.INSTANCE_IP,
        )
    yield
    if settings.EUREKA_SERVER:
        await eureka_client.stop_async()
```

### 4.2 컨테이너 및 로컬 환경 IP 바인딩 전략
- 네트워크 인터페이스 자동 감지 시 발생할 수 있는 가상 NIC 바인딩 오류를 방지하기 위해, Kubernetes Pod 환경에서는 `POD_IP` 환경변수를 우선 참조하고 로컬 환경에서는 `127.0.0.1`로 명시적 고정 바인딩을 수행합니다.

### 4.3 확장 가능한 프로젝트 디렉터리 레이아웃
```
fast-api-ai/
├── core/            # 설정(Config) 및 Eureka 연동 모듈
├── routes/          # 도메인별 APIRouter 정의
├── service/         # 비즈니스 로직 및 AI 모델 추론 계층
├── db/              # 데이터베이스 커넥션 및 모델
├── main.py          # 애플리케이션 엔트리포인트
└── requirements.txt # 런타임 및 AI 의존성 명세
```

---

## 5. 실행 및 개발 환경

### 로컬 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 단독 실행 (기본 포트 8000)
python main.py

# 핫 리로드 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker 빌드 및 실행
```bash
docker build -t fast-api-ai .
docker run -p 8000:8000 -e EUREKA_SERVER=http://host.docker.internal:8761/eureka fast-api-ai
```

### API 문서 확인
- 로컬 단독: `http://localhost:8000/docs`
- 게이트웨이 경유: `http://localhost:8100/fast-api-ai/docs`
