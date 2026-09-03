---
name: add-route
description: fast-api-ai 프로젝트에 이 리포지토리 관례를 따르는 새 FastAPI 라우터를 추가한다. "라우트 추가해줘", "엔드포인트 만들어줘", "새 API 만들어줘" 같은 요청에서 사용.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# /add-route — 새 라우터 추가

`$ARGUMENTS`로 도메인 이름과(있다면) 원하는 엔드포인트를 전달받는다. 예: `/add-route user 회원 조회/등록`.

## 이 리포지토리의 라우터 관례

- [routes/test/connect_test.py](../../../routes/test/connect_test.py)가 참고할 기존 패턴이다: `routes/<도메인>/<이름>.py` 파일에 `APIRouter(prefix="/<도메인>")`를 만들고, 그 아래에 엔드포인트 함수를 정의한다.
- 설정값(포트, 외부 URL 등)이 필요하면 하드코딩하지 말고 [core/config.py](../../../core/config.py)의 `settings`를 import해서 사용한다.
- 새로 만든 라우터는 그 자체로는 노출되지 않는다. 반드시 [main.py](../../../main.py)에서 `from routes.<도메인>.<이름> import router as <이름>_router` 후 `app.include_router(<이름>_router, tags=["..."])`로 등록해야 한다.
- 도메인 폴더(`routes/<도메인>/`)에 `__init__.py`가 없다면 기존 `routes/__init__.py`처럼 빈 파일로 추가한다.

## 절차

1. `$ARGUMENTS`에서 도메인 이름과 엔드포인트 요구사항을 파악한다. 불명확하면 사용자에게 도메인 이름(예: `user`, `chat`)과 필요한 엔드포인트를 짧게 확인한다.
2. `routes/<도메인>/` 디렉토리가 있는지 [Glob](../../../routes)으로 확인하고, 없으면 `__init__.py`와 라우터 파일을 새로 만든다.
3. `routes/test/connect_test.py`의 스타일(임포트 순서, `APIRouter(prefix=...)`, 함수형 엔드포인트)을 그대로 따라 새 파일을 작성한다.
4. [main.py](../../../main.py)를 읽고 기존 `test_router` 등록 방식과 동일하게 새 라우터의 import와 `app.include_router()` 호출을 추가한다.
5. 비즈니스 로직이 단순 응답 이상으로 필요하면 `service/`, DB 접근이 필요하면 `db/` 아래에 관련 코드를 두고 라우터에서는 그 함수만 호출하도록 분리한다(현재 두 디렉토리는 비어 있는 준비 공간이다).
6. 변경한 파일 목록과, `python main.py`로 실행 후 어떤 경로로 확인할 수 있는지(`root_path="/fast-api-ai"` + 라우터 `prefix` 조합) 사용자에게 요약해 준다.
