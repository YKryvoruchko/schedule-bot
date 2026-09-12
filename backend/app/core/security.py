from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    try:
        scheme, iterations, salt, expected = stored_hash.split("$", 3)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
    return hmac.compare_digest(base64.b64encode(derived).decode(), expected)


def hash_password(password: str, iterations: int = 260_000) -> str:
    salt = secrets.token_urlsafe(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(derived).decode()}"


@dataclass(frozen=True)
class SessionSigner:
    secret_key: str
    max_age_seconds: int = 60 * 60 * 12

    def sign(self, username: str) -> str:
        issued = str(int(time.time()))
        payload = base64.urlsafe_b64encode(f"{username}:{issued}".encode()).decode()
        signature = hmac.new(self.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{signature}"

    def verify(self, token: str) -> str | None:
        try:
            payload, signature = token.rsplit(".", 1)
        except ValueError:
            return None
        expected = hmac.new(self.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        try:
            decoded = base64.urlsafe_b64decode(payload.encode()).decode()
            username, issued = decoded.rsplit(":", 1)
        except Exception:
            return None
        if int(time.time()) - int(issued) > self.max_age_seconds:
            return None
        return username
