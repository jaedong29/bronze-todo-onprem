# Bronze Todo 기본 샘플 앱

FastAPI + SQLAlchemy + SQLite로 만든 할 일 CRUD 샘플 앱이다.

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
