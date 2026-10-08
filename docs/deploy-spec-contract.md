# 배포 명세 전달 계약 (P4, 2026-10-09)

현재 구현의 계약을 공유하는 초안이다. 팀 공동 확정 여부는 별도로 확인한다.
기준 모델은 `ai/src/ai/spec/models.py`, JSON Schema는 `ai/src/ai/spec/schema.json`이다.
온프레미스 샘플에는 동일한 스키마를 `deploy-spec.schema.json`으로 복사했다.
YAML을 파싱한 JSON 객체에 적용하며, 알 수 없는 키는 모든 객체에서 거부한다.

## 필드

| 필드 | 입력 필수 / 기본값 | 의미와 현재 허용 값 |
| --- | --- | --- |
| `app` | 필수 | 앱 이름, 문자열 |
| `source` / `source.repo` | 필수 | 소스 저장소 문자열. 로컬 분석 시 경로도 허용 |
| `source.commit` | 선택, 생략 | 소스 추적용 문자열. 현재 SHA 형식 검사는 없으며 배포 서비스는 정확한 커밋을 확정해야 함 |
| `build` | 선택, 아래 기본값 | 빌드 정보 |
| `build.dockerfile` | 선택, `Dockerfile` | 현재 이 값만 허용 |
| `build.runtime_hint` | 선택, `python3.12` | 현재 이 값만 허용 |
| `port` | 선택, `8080` | 현재 8080만 허용. 어댑터가 PORT로 주입 |
| `healthcheck` | 선택, `/healthz` | 현재 이 경로만 허용 |
| `ingress` | 선택, `public` | `public` 또는 `internal`. 호스트명/TLS/프록시는 어댑터 책임 |
| `env` | 필수, 빈 배열 가능 | 환경변수 목록 |
| `env[].name` | 필수 | `^[A-Z_][A-Z0-9_]*$` |
| `env[].secret` | 선택, `false` | 민감 값 여부. B의 생성 결과는 실제 시크릿 값을 담지 않음 |
| `env[].generate` | 선택, `false` | 미입력 시 어댑터에 생성 요청. DB URL을 무작위로 생성하는 의미가 아님 |
| `env[].value` | 선택, 생략 | 일반 설정 문자열. PORT도 문자열 `"8080"` |
| `backing_services` | 필수, 빈 배열 가능 | 외부 자원 요구 사항 |
| `backing_services[].type` | 필수 | `postgres` 또는 `object_storage` |
| `backing_services[].bind_as` | 필수 | 각각 `DATABASE_URL`, `STORAGE_URL` |
| `workload` / 네 하위 필드 | 필수 | 아래 네 항목 모두 필요 |
| `workload.type` | 필수 | `request-driven` 또는 `always-on` |
| `workload.scale_to_zero` | 필수 | boolean. always-on 또는 websocket이면 false |
| `workload.max_request_seconds` | 필수 | 정수 1~3600. AI/기본값의 후보이며 실측 시간이나 플랫폼 지원 보장이 아님 |
| `workload.websocket` | 필수 | boolean. 생성기는 websocket/scheduler 신호로 always-on 판정 |
| `processes.web.instances` | 선택, `1` | 현재 단일 인스턴스만 허용 |
| `release` | 선택, 생략 | 초기화/마이그레이션이 필요한 앱만 지정 |
| `release.migrate` | release가 있으면 필수 | 이미지 안에서 한 번 실행할 명령 문자열 |
| `profile` | 선택, `dev` | `dev` 또는 `prod` |

입력 기본값은 pydantic이 채운다. JSON Schema 단독 검증은 default를 삽입하지 않는다.
B가 내보내는 YAML은 기본값을 포함하고 null 필드는 생략한다.
JSON Schema에는 pydantic의 두 교차 필드 검증이 자동으로 포함되지 않는다.
따라서 어댑터도 서비스 종류↔bind_as 일치와 always-on/websocket↔scale_to_zero 조건을 확인해야 한다.
샘플의 `scripts/validate_spec.py`가 두 검증을 함께 수행한다.
실제 시크릿 분리, 환경변수 이름 중복, 명령 실행 허용 여부 등의 운영 정책은 스키마 검증만으로 보장되지 않는다.

## 로컬에 있는 설계 6장 초안과의 차이

비교 대상은 사용자가 전달한 설계 원문 1~13장 및 `reference/deploy-spec.example.yaml`이다.
원문 및 reference를 수정하지 않고 아래 현재 구현 범위만 기록한다.

| 항목 | 참조 예시 | 현재 P4 구현 / 전달 샘플 |
| --- | --- | --- |
| `source.commit` | 예시 SHA 필드 있음 | 미제공 시 생략. 어댑터가 배포 전 실제 커밋 확정 필요 |
| `release.migrate` | `alembic upgrade head` | 샘플은 `python -m app.migrate`. 빈 DB의 테이블 생성만 수행하며 기존 스키마 변경/데이터 이전은 지원하지 않음 |
| `object_storage` | 확장 예시로 포함 | 타입은 스키마에 있으나 파일 저장 전환 미구현이라 샘플에는 생성하지 않음 |
| Python/포트/헬스체크/인스턴스 | 예시 값 | 현재 계약에서는 python3.12 / 8080 / healthz / 1로 제한 |
| `max_request_seconds` | 10초 예시 | 기본 후보 10초. 플랫폼 timeout과 실제 동작은 C에서 확인 |
| secret 값과 DB URL | secret 생성 / 자원 바인딩 | SECRET_KEY는 generate=true, DATABASE_URL은 backing_services에서만 연결 |
| 워크로드 | request-driven 예시 | scheduler/websocket 감지 시 always-on, scale_to_zero=false, instances=1로 규칙 고정 |

Registry/image digest, AWS/onprem별 리소스, Traefik 설정은 이 명세에 새 필드로 추가하지 않았다.
서비스가 이미지를 한 번 빌드하고 어댑터가 같은 digest를 사용하도록 별도 배포 실행 정보로 전달한다.
`source.commit`은 소스 추적 메타데이터다. 커밋 문자열을 Dockerfile/이미지 내용에 삽입하지 않는다.
같은 이미지를 재사용하는 것과 별도 재빌드 결과가 동일한 것은 다르다.

## 설계 전체와 P4의 진행 차이

명세의 최상위 필드 이름/구조는 설계 6장과 동일하다. 아래는 계약 변경이 아니라 현재 구현과 목표의 차이다.

| 설계 항목 | 현재 B의 상태 |
| --- | --- |
| 2/4장 AI 판정·세트 선택 | 지원 등급/탐지/하드 제약은 규칙이 결정, LLM은 설명과 제한된 후보 보강. 추천 세트·tfvars·인프라 예상 비용은 P5 예정 |
| 3/4장 실패 로그로 수정 재시도 | LLM JSON 및 패키징 검증 재요청은 있으나, 컨테이너 실패 로그를 이용한 수정 루프는 P5 예정 |
| 3장 Python 서비스 서버 | B는 CLI + 함수만 제공. A의 FastAPI/Django 서버와 진행 로그 SSE는 별도 구현 |
| 3/4장 검증 게이트 | 자체 todo/todo-scheduler의 빌드·빈 Postgres 초기화·healthz·CRUD·앱 재시작을 검증. 일반 앱 실행은 skipped |
| 3장 PR → merge → ECR → 배포 | A/C의 연결 범위. 현재 B의 pr_eligible=false, 자동 승인 기능 완료로 표시하지 않음 |
| 7/8장 온프레미스 세트 | 이번 Compose는 C의 환경 구성 전 동작 확인용. Traefik/SSH/락/배포 이력/롤백 구현은 포함하지 않음 |
| 9장 release.migrate | 샘플의 create_all은 빈 DB 초기화만 검증. 기존 테이블 스키마 업그레이드와 실제 앱 마이그레이션 호환성은 미검증 |

설계 1장의 "컨테이너 재시작 시 내부 데이터 유실"은 저장 방식에 따라 달라진다.
같은 컨테이너의 stop/start는 일반적으로 writable layer를 유지하고, 제거/교체 시 그 layer의 데이터가 사라질 수 있다.
이 샘플의 Postgres는 컨테이너 밖의 named volume에 데이터를 두며 Compose down/up 후 유지 여부를 검증한다.
배포 명세는 자원 요구만 표현하므로 백업/보존/삭제 정책은 C가 별도로 정해야 한다.

설계 7/10장의 이전 SHA 이미지 롤백은 기존 DB 스키마와 이전 코드의 호환성을 자동으로 보장하지 않는다.
이번 샘플은 빈 DB 초기화만 제공하며 스키마 롤백이나 운영 롤백 검증을 구현하지 않았다.

## 검증과 실행 책임

B는 명세 구조, 코드 규칙, 자체 샘플의 게이트를 검증한다.
A/C는 실제 소스 커밋, 이미지/digest, DB 연결, 시크릿 주입, migrate 완료 후 앱 시작, ingress와 실행 환경을 연결한다.
명세 검증 통과는 앱 검증 게이트 통과나 PR 승인/운영 배포 승인을 뜻하지 않는다.
일반 앱의 컨테이너 게이트는 skipped이며 현재 pr_eligible=false다.
DB/영속 파일 저장 방식 변경은 risky이며 승인 필요다.
기존 데이터는 자동으로 이전되지 않는다. 데이터 이전 필요(미지원) (`data_migration_unsupported`).

온프레미스 검증용 새 샘플과 실행 방법은 `samples/todo-onprem/README.md`를 따른다.
원본 위반 탐지 픽스처 `samples/todo` 및 `samples/todo-scheduler`는 그대로 유지했다.
