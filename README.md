# Bronze Todo 기본 샘플 앱

기존 `samples/todo` 원본의 FastAPI + SQLAlchemy + SQLite 할 일 앱이다.
앱 코드와 requirements.txt는 원본 그대로이며, AI 진단용 의도적 위반을 포함한다.

## 실행

Python 3.12를 사용한다.

```sh
git clone https://github.com/jaedong29/bronze-todo-onprem.git
cd bronze-todo-onprem
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

브라우저에서 http://127.0.0.1:8000 에 접속한다. 종료는 Ctrl+C.

## 기능

- 할 일 추가/조회/수정/삭제, 완료 표시와 마감일 입력.
- 시작 시 데모 할 일 2개 생성.
- `POST /export`: `data/todos.json`으로 내보내기.
- SQLite 데이터는 `todo.db`, 로그는 `app.log`에 저장.

## AI 진단용 위반

SQLite 하드코딩, 더미 시크릿 `dummy-secret-do-not-use`, 파일 로그,
고정 포트, 의존성 버전 미고정, 로컬 내보내기 파일 저장을 포함한다.
정답 목록은 `VIOLATIONS.json`에 있다. `/healthz`는 원본에 없어 404다.
