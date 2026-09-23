# fast-api-ai — MSA에 합류한 Python 서비스

> Java 기반 Spring Cloud MSA에 **Python(FastAPI) 서비스를 이질감 없이 끼워 넣은** 마이크로서비스입니다.
> 같은 Eureka에 등록되고 같은 게이트웨이 경로 규칙을 따릅니다. **현재는 디스커버리·라우팅 골격까지 구현된 초기 단계**이고, AI/RAG 기능이 들어갈 자리입니다.

| | |
|---|---|
| **게이트웨이 경로** | `/fast-api-ai/**` |
| **로컬** | `http://localhost:8000` (문서 `/docs`) |
| **스택** | Python 3.12 · FastAPI · Uvicorn · pydantic-settings · py-eureka-client |

---

## 1. 위치

```
[게이트웨이] sj-lab-apigateway :8100 ──/fast-api-ai/**──▶ [이 서비스] :8000
                    │                                          │
                    └────────── [Eureka] :8761 ◀──등록─────────┘
```

Spring 서비스들과 같은 레지스트리에 `FAST-API-AI`로 등록됩니다.

---

## 2. 면접에서 봐주셨으면 하는 부분

### ① 이기종 언어 서비스를 같은 규약으로

Spring Cloud 생태계에 Python 서비스를 넣을 때 필요한 두 가지를 맞췄습니다.

- **서비스 등록**: `py-eureka-client`를 FastAPI `lifespan`에 물려, 앱 시작 시 `init_async()` / 종료 시 `stop_async()`가 확실히 호출되도록 했습니다(프로세스가 죽을 때 레지스트리에 유령 인스턴스가 남지 않게).
- **경로 규약**: `root_path="/fast-api-ai"`로 설정해 게이트웨이가 경로를 벗기지 않고 그대로 전달하는 이 시스템의 규칙과 일치시켰습니다. Swagger 문서 경로도 자동으로 맞습니다.

### ② 등록 IP를 고정한 이유

`INSTANCE_IP`는 `POD_IP` 환경변수를 우선 쓰고, 없으면 **`127.0.0.1`로 고정**합니다. 예전에 `socket` 기반 자동탐지를 썼다가 로컬에서 엉뚱한 NIC 주소가 Eureka에 등록돼 게이트웨이가 접속하지 못하는 문제가 있었습니다. 자동탐지를 되살리지 말라는 경고를 코드 주석과 문서에 남겨 두었습니다.

### ③ 확장을 염두에 둔 골격

`routes/<도메인>/` + `APIRouter` 구조, `service/`·`db/` 자리 확보, AI/RAG 의존성(PyTorch·transformers·OpenAI SDK 등)을 `requirements.txt`에 **주석으로 미리 정리**해 두었습니다. 이미지 처리까지 고려해 Dockerfile에 `libgl1-mesa-glx`·`build-essential`·헬스체크용 `curl`을 포함했습니다.

---

## 3. 실행

```bash
pip install -r requirements.txt
python main.py                                        # settings.PORT(기본 8000)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload  # 리로드가 필요할 때
```

```bash
docker build -t fast-api-ai .
docker run -p 8000:8000 fast-api-ai
```

---

## 4. 구조

| 경로 | 역할 |
|---|---|
| `main.py` | 엔트리포인트. `root_path`, Eureka `lifespan`, **라우터 등록(`include_router`)** |
| `core/config.py` | `pydantic-settings` 전역 설정 — `APP_NAME`, `PORT`, `EUREKA_SERVER`, `INSTANCE_IP` |
| `core/eureka.py` | Eureka 등록/해제(`@asynccontextmanager`) |
| `routes/` | 도메인별 `APIRouter` (예: `routes/test/connect_test.py`) |
| `service/`, `db/` | 비즈니스 로직·DB 접근용으로 비워 둔 자리 |

**라우트 추가**: `routes/<도메인>/`에 `APIRouter`를 만들고 → `main.py`에서 `include_router()` → 외부 경로는 `/fast-api-ai/<prefix>/...`. 등록을 빠뜨리면 노출되지 않습니다.

---

## 5. 배포

```
git push → Jenkins(빌드 → 이미지 push) → sj-lab-k8s-manifests 의 image.tag 자동 커밋
        → ArgoCD 동기화 → Kubernetes 롤아웃 (ClusterIP 80 → 8000)
```

---

## 6. 현재 상태와 다음 계획

- **골격 단계입니다.** 실제 AI 기능은 아직 없습니다.
- 계획 중인 첫 기능: 현장 음성 메모의 STT 결과(이미 DB에 적재됨)를 요약하고 **보수 우선순위를 제안**하는 엔드포인트. 시설물 데이터와 바로 연결되는 주제라 MSA·GIS·AI가 한 줄기로 이어집니다.
- 테스트·린터가 없어 도입이 필요합니다(pytest, ruff).

## 참고

- 전체 구조: 총괄 저장소 `mapservice-rest`의 `docs/system-architecture.md`
- 작업 규칙: 이 저장소의 `CLAUDE.md`
