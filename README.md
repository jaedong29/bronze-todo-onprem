# Bronze Todo — 온프레미스 배포 테스트 샘플

FastAPI + SQLAlchemy + Postgres의 할 일 CRUD/UI 앱이다. Team Bronze의 P4에서 검증한
`samples/todo` 임시 변환본을 별도 저장소로 전달하기 위한 복사본이다.
원본 탐지용 SQLite 샘플은 수정하지 않았다. Python 3.12, 앱 포트 8080, `/healthz`,
표준 출력 로그, 비루트 실행 및 읽기 전용 앱 파일시스템을 사용한다.
앱 의존성은 개발 환경에서 사용한 버전으로 고정했다.

## 바로 실행

Docker Engine/Desktop + Compose v2, 환경 파일 생성/검증용 Python 3가 필요하다.
앱 자체는 컨테이너 안의 Python 3.12로 실행한다. Linux에서도 같은 명령을 사용한다.

```sh
git clone https://github.com/jaedong29/bronze-todo-onprem.git
cd bronze-todo-onprem
python3 scripts/init_env.py
docker compose -p bronze-todo-demo build web
docker compose -p bronze-todo-demo up -d --wait --wait-timeout 120
curl -f http://127.0.0.1:8080/healthz
```

브라우저에서 http://127.0.0.1:8080 에 접속한다. 첫 DB는 비어 있다. UI에서 할 일을 추가한다.
DB readiness → 일회성 migrate 완료 → web 시작 순서다.
컨테이너 DB에는 호스트 포트를 열지 않고, UI 포트는 기본 loopback에만 연결한다.
8080이 사용 중이면 `.env`에 `HOST_PORT=18080`을 추가하고 아래 smoke의 URL도 바꾼다.
생성된 `.env`는 Git/이미지에서 제외하며 기존 파일을 덮어쓰지 않는다.
이 앱에는 로그인/사용자별 접근 제어가 없다. 외부 접근 설정은 테스트 환경의 프록시에서 담당한다.

## 동작 검증

```sh
python3 scripts/smoke.py --project bronze-todo-demo
# 포트를 바꾼 경우:
python3 scripts/smoke.py --project bronze-todo-demo --url http://127.0.0.1:18080
```

검사 범위: healthz 200, 생성/조회/수정/삭제, 빈 제목 422, web 재시작 및 Compose down/up 후
DB 데이터 유지. smoke는 선택한 Compose 스택을 잠깐 내리고 다시 시작한다.
`/healthz` 자체는 DB 쿼리를 하지 않는다. DB 검증은 별도 CRUD/persistence 검사로 확인한다.

`POST /export`와 UI의 파일 내보내기는 원본의 로컬 파일 저장 구현이 남아 있다.
읽기 전용 실행에서 사용할 수 없으며 이번 검증 범위에서 제외했다.
object storage 전환이나 임의 `/tmp` 저장으로 바꾸지 않았다.
`SECRET_KEY`는 환경 주입 계약 확인용이며 현재 인증 기능에 사용되지 않는다.

## 배포 명세

- `deploy-spec.yaml`: 이 복사본의 실행 요구 사항.
- `deploy-spec.schema.json`: B의 현재 pydantic 모델에서 생성한 JSON Schema 사본.
- `docs/deploy-spec-contract.md`: 필수/선택 필드, 기본값, 설계 참조 예시와의 차이.
- `scripts/validate_spec.py`: JSON Schema + 두 교차 필드 검증. 기본값을 삽입하지는 않음.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-validation.txt
.venv/bin/python scripts/validate_spec.py
```

`release.migrate: python -m app.migrate`는 빈 Postgres에 테이블을 만드는 샘플 초기화 명령이다.
Alembic 스키마 업그레이드나 데이터 이전 기능은 없다.
기존 데이터는 자동으로 이전되지 않는다. 데이터 이전 필요(미지원) (`data_migration_unsupported`).
이 전달본은 새 테스트 DB만 사용한다. 실제 사용자 앱의 DB/파일 전환은 별도 승인 대상이다.
명세의 `source.commit`은 아직 생략되어 있다. 배포 서비스는 checkout한 실제 커밋을 확인한다.
레지스트리 주소/이미지 digest/Traefik 설정은 어댑터가 결정한다.
`request-driven`/`scale_to_zero: true`는 세트 선택 근거이며 이 Compose가 scale-to-zero를 구현하는 뜻은 아니다.

## AWS와 온프레미스에서 같은 이미지 사용

Dockerfile에 Lambda Web Adapter를 포함했고 SHA/빌드 시각은 넣지 않았다.
C가 대상 플랫폼을 확정해 이미지를 한 번 빌드하고, 동일한 digest를 두 배포 대상으로 전달한다.
각 머신에서 `docker compose build`를 따로 실행한 결과의 digest 일치를 보장하지 않는다.
운영 어댑터 검증에서는 `TODO_IMAGE=registry/repository@sha256:...`를 지정하고 이미지를 미리 pull한 뒤
`docker compose up -d --no-build --wait`를 사용한다. 기본 명령은 로컬 테스트용이다.
베이스 이미지/보조 이미지 태그는 digest로 고정하지 않았으므로 재빌드 동일성은 보장하지 않는다.
실제 AWS/온프레미스의 네트워크, 프록시, 플랫폼과 배포 검증은 C에서 수행한다.

## 로그와 정리

```sh
docker compose -p bronze-todo-demo logs web migrate
# 중지: 데이터 볼륨 유지
docker compose -p bronze-todo-demo down
# 테스트 데이터도 삭제할 때만 실행
docker compose -p bronze-todo-demo down -v
```

검증 결과는 `docs/validation.md`에 기록한다. 이 저장소의 배포 테스트 성공을
B 파이프라인의 PR 자동 승인으로 해석하지 않는다. 현재 B의 pr_eligible은 false다.
