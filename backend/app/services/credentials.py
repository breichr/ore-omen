"""Pure rules for account credentials (docs/08-technik.md, "Auth")."""

from __future__ import annotations

import re
import secrets

USERNAME_MIN = 3
USERNAME_MAX = 20
PASSWORD_MIN = 8
PASSWORD_MAX = 128

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")

# Crockford Base32: no I, L, O, U – unambiguous when written down by hand
RECOVERY_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
RECOVERY_GROUPS = 5
RECOVERY_GROUP_LEN = 5
RECOVERY_LEN = RECOVERY_GROUPS * RECOVERY_GROUP_LEN
_RECOVERY_ALIASES = str.maketrans({"O": "0", "I": "1", "L": "1"})


class CredentialError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_username(username: str) -> str:
    u = username.strip()
    if not USERNAME_MIN <= len(u) <= USERNAME_MAX:
        raise CredentialError("username_length")
    if not _USERNAME_RE.match(u):
        raise CredentialError("username_chars")
    return u


def username_key(username: str) -> str:
    return username.strip().lower()


def validate_password(password: str) -> str:
    if not PASSWORD_MIN <= len(password) <= PASSWORD_MAX:
        raise CredentialError("password_length")
    return password


def new_recovery_key() -> str:
    """Random key, grouped for display: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (125 bits)."""
    raw = "".join(secrets.choice(RECOVERY_ALPHABET) for _ in range(RECOVERY_LEN))
    return format_recovery_key(raw)


def format_recovery_key(normalized: str) -> str:
    n = RECOVERY_GROUP_LEN
    return "-".join(normalized[i : i + n] for i in range(0, len(normalized), n))


def normalize_recovery_key(key: str) -> str | None:
    """Canonical form for hashing, or None if it cannot be a valid key.

    Ignores case, spaces and hyphens and maps look-alikes (O→0, I/L→1).
    """
    k = re.sub(r"[\s-]", "", key).upper().translate(_RECOVERY_ALIASES)
    if len(k) != RECOVERY_LEN or any(ch not in RECOVERY_ALPHABET for ch in k):
        return None
    return k
