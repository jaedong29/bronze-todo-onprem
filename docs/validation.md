# 전달본 검증 기록

검증일: 2026-10-09 (Asia/Seoul).
환경: macOS의 Docker Desktop, Linux arm64 이미지, Python 3.12, Postgres 16-alpine.
앱 컨테이너 사용자: `10001:10001`. 앱과 migrate는 read_only, /tmp tmpfs,
cap_drop=ALL, no-new-privileges 및 CPU/메모리/PID 제한을 사용했다.

| 검사 | 결과 |
| --- | --- |
| Dockerfile로 전달본 빌드 | 통과 |
| Compose DB readiness → migrate → web healthcheck | 통과 |
| `/healthz` HTTP 200 | 통과 |
| 할 일 생성/조회/수정/삭제 | 통과 |
| 빈 제목 입력 HTTP 422 | 통과 |
| web 컨테이너 재시작 후 데이터 유지 | 통과 |
| Compose down/up 후 named volume 데이터 유지 | 통과 |
| 전달 YAML의 JSON Schema + 교차 필드 검증 | 통과 |
| 잘못된 port / binding / always-on+scale_to_zero / 알 수 없는 키 거부 | 통과 |
| JSON Schema 사본과 B의 기준 파일 바이트 일치 | 통과 |
| 전달용 Python scripts의 ruff check / format check | 통과 |
| B의 기존 기본 pytest | 167 passed, 4 skipped (유료 AWS/명시적 Docker 테스트); deprecation warning 1개 |

실행한 명령:

```sh
python3 scripts/init_env.py
docker compose -p bronze-todo-handoff-check build web
docker compose -p bronze-todo-handoff-check up -d --wait --wait-timeout 120
python3 scripts/smoke.py --project bronze-todo-handoff-check
# B 개발 환경의 Python으로 실행:
python scripts/validate_spec.py
```

파일 내보내기, object storage, Alembic 업그레이드, 기존 데이터 이전, 인증,
실제 온프레미스 서버/Traefik/SSH 및 AWS 배포는 검증 범위에 포함하지 않는다.
x86_64/amd64 대상은 이 기록으로 검증되었다고 주장하지 않으며 C가 대상 이미지로 확인한다.
명세 검증/데모 실행 결과는 일반 앱의 게이트 통과 또는 PR 자동 승인 증거가 아니다.
테스트 후 이 Compose 프로젝트의 컨테이너/네트워크/테스트 볼륨은 제거했다.
로컬 빌드 이미지와 빌드 캐시는 재사용을 위해 남겼다.
