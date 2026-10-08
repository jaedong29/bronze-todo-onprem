"""Create local demo credentials without printing them or overwriting existing settings."""

import os
import secrets
from pathlib import Path

path = Path(__file__).resolve().parents[1] / ".env"
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as stream:
    stream.write(f"POSTGRES_PASSWORD={secrets.token_hex(24)}\n")
    stream.write(f"SECRET_KEY={secrets.token_hex(32)}\n")
print("Created .env for this local demo (not tracked by Git).")
