# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

FastAPI 기반 백엔드 서비스(`fast-api-ai`)로, Spring Cloud 기반 MSA(Eureka + Gateway) 생태계에 클라이언트로 등록되어 동작하는 마이크로서비스입니다. Kubernetes 환경에서 Gateway 뒤에 배치되며, 이름에서 알 수 있듯 향후 AI/RAG 기능을 담당할 예정입니다(현재는 라우팅·서비스 디스커버리 골격만 구현된 초기 단계).

## 개발 명령어

- 의존성 설치: `pip install -r requirements.txt`
- 로컬 서버 실행: `python main.py` (내부적으로 `uvicorn`을 `settings.PORT`(기본 8000)로 구동)
  - 리로드가 필요하면 `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` 사용
- Docker 빌드/실행: `docker build -t fast-api-ai .` → `docker run -p 8000:8000 fast-api-ai`
- 테스트/린트: 현재 테스트 스위트(pytest 등)와 린터(ruff/black 등)가 구성되어 있지 않음. 새로 도입 시 `requirements.txt`에 명시할 것

## 아키텍처

- [main.py](main.py): FastAPI 앱 엔트리포인트. `eureka`를 `lifespan`으로 주입하고, `root_path="/fast-api-ai"`로 설정(Gateway 하위 경로 매핑용). 라우터는 여기서 `app.include_router()`로 명시적으로 등록해야 실제로 노출됨
- [core/config.py](core/config.py): `pydantic-settings` 기반 전역 설정 싱글턴(`settings`). `APP_NAME`, `PORT`, `EUREKA_SERVER`, `INSTANCE_IP`를 관리
  - `INSTANCE_IP`는 `POD_IP` 환경변수를 우선 사용하고, 없으면(로컬 개발) 무조건 `127.0.0.1`로 고정됨 — 이 값이 Eureka에 등록되는 주소이므로 임의로 IP 자동탐지 로직을 되살리지 말 것(과거 `socket` 기반 자동탐지 방식에서 의도적으로 변경된 이력이 주석으로 남아 있음)
- [core/eureka.py](core/eureka.py): `@asynccontextmanager`로 구현된 Eureka 등록/해제 로직. FastAPI `lifespan`에 주입되어 앱 시작 시 `eureka_client.init_async()`, 종료 시 `eureka_client.stop_async()` 호출
- [routes/](routes/): 도메인별 하위 폴더 + `APIRouter` 조합으로 구성(예: [routes/test/connect_test.py](routes/test/connect_test.py)는 `prefix="/test"`). 새 라우터를 추가하면 반드시 `main.py`에 `include_router()`로 등록해야 함
- `service/`, `db/`: 비즈니스 로직·DB 접근 계층을 위해 미리 만들어 둔 빈 디렉토리(아직 구현 없음). 관련 코드를 추가할 때는 이 위치를 우선 사용

## 참고

- `requirements.txt`에는 향후 AI/RAG 기능(PyTorch, transformers, OpenAI SDK, tiktoken, numpy/pandas 등)을 위한 의존성이 주석 처리된 채로 미리 정리되어 있음. 실제로 해당 기능을 구현할 때 필요한 항목만 주석 해제할 것
- `Dockerfile`은 `python:3.12.7-slim` 기반이며 OpenCV 등 CNN 이미지 처리에 필요한 `libgl1-mesa-glx`, 빌드 도구용 `build-essential`, 헬스체크용 `curl`을 설치함 — 이미지 처리 관련 의존성을 추가로 쓸 경우 이 목록도 함께 검토할 것
- 커밋 메시지는 `[fix]`, `[feat]`, `[test]`, `[refactor]` 형태의 접두사 컨벤션을 사용함
- 코드 내 주석은 한글로 작성되어 있고 설정값의 의도(예: `INSTANCE_IP` 고정 이유)를 설명하는 용도로 쓰이는 경우가 많음 — 이런 맥락 주석은 삭제하지 말고 유지할 것

## README 유지 규칙

- **이 저장소에 기능·API·화면·실행 방법·설정(환경변수/시크릿)·배포 방식이 추가되거나 바뀌면, 같은 작업에서 `README.md`도 함께 갱신할 것.** 코드만 고치고 README를 그대로 두지 말 것.
- 갱신 대상 예: 새 엔드포인트·화면·모듈, 빌드/실행 명령 변경, 포트·의존 서비스 변경, 환경변수·Secret 추가, 배포 절차 변경, 해결한 이슈·새로 생긴 한계.
- **README는 면접관·처음 보는 사람이 읽는 문서**다(이 프로젝트는 포트폴리오). 사용자·리뷰어 관점의 설명(무엇을·왜·어떻게 확인하는지)은 README에, 에이전트/내부 작업 규칙은 이 문서(CLAUDE.md)에 둔다.
- 문구가 실제 코드와 어긋나지 않는지 확인하고, 구현되지 않은 기능을 적지 말 것. 한계·미구현 항목은 숨기지 말고 "현재 한계"에 적는다.

## 통합 허브

저장소를 넘나드는 작업(DB → 백엔드 → 디스커버리 → 게이트웨이 → 프론트엔드)의 총괄 기준 저장소는 `C:\developer\workspace\mapservice-rest`입니다. 시스템 전체 구조·API 계약은 그 저장소의 `docs/system-architecture.md`, 로컬 포트·기동 순서·CORS는 `docs/dev-environment.md`에 있고, MCP(GitHub/DB)와 로컬 비밀값도 그 저장소에서만 관리합니다.