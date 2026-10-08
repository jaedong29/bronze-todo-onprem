"""Check HTTP CRUD and persistence across app and full Compose restarts."""

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Same Compose -p project name used for up")
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    compose = ["docker", "compose", "-p", args.project]

    def request(method: str, route: str, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            args.url.rstrip("/") + route,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read()
            return response.status, json.loads(body) if body else None

    def wait_ready() -> None:
        for _ in range(60):
            try:
                if request("GET", "/healthz")[0] == 200:
                    return
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(1)
        raise RuntimeError("healthz timeout")

    wait_ready()
    status, todo = request("POST", "/todos", {"title": "onprem persistence check"})
    assert status == 201
    todo_id = todo["id"]
    try:
        request("POST", "/todos", {"title": "   "})
        raise AssertionError("blank title accepted")
    except urllib.error.HTTPError as error:
        assert error.code == 422
    status, changed = request("PUT", f"/todos/{todo_id}", {"title": todo["title"], "done": True})
    assert status == 200 and changed["done"]
    for commands in (["restart", "web"], ["down"], ["up", "-d", "--wait", "--wait-timeout", "120"]):
        subprocess.run(compose + commands, cwd=root, check=True)
        if commands[0] == "down":
            continue
        wait_ready()
        items = request("GET", "/todos")[1]
        assert any(item["id"] == todo_id and item["done"] for item in items)
    assert request("DELETE", f"/todos/{todo_id}")[0] == 204
    assert all(item["id"] != todo_id for item in request("GET", "/todos")[1])
    print("PASS: healthz, CRUD, blank title 422, app restart and Compose down/up persistence")


if __name__ == "__main__":
    main()
