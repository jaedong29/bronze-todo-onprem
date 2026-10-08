"""Validate the exported P4 structure and its two pydantic cross-field rules."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


def validate(path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "deploy-spec.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    payload = yaml.safe_load(path.read_text())
    Draft202012Validator(schema).validate(payload)
    for service in payload["backing_services"]:
        expected = "DATABASE_URL" if service["type"] == "postgres" else "STORAGE_URL"
        if service["bind_as"] != expected:
            raise ValueError("backing_service_binding_mismatch")
    workload = payload["workload"]
    if (workload["type"] == "always-on" or workload["websocket"]) and workload["scale_to_zero"]:
        raise ValueError("persistent_workload_cannot_scale_to_zero")
    print(f"Valid P4 deploy spec: {path.name}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    validate(Path(sys.argv[1]) if len(sys.argv) > 1 else root / "deploy-spec.yaml")
