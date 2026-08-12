"""Redact credentials before logs or support files are written."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

REDACTED = "<REDACTED>"

_SENSITIVE_NAME = (
    r"(?:password|passwd|pwd|token|access[_-]?token|refresh[_-]?token|"
    r"github[_-]?token|api[_-]?key|secret|client[_-]?secret|authorization|"
    r"proxy[_-]?authorization|cookie|set[_-]?cookie|aws[_-]?secret[_-]?access[_-]?key|"
    r"database[_-]?url)"
)
_TOKEN_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}"),
)
_HEADER = re.compile(
    r"(?i)(\b(?:authorization|proxy-authorization|cookie|set-cookie)\s*:\s*)([^\r\n]+)"
)
_CLI_SECRET = re.compile(
    rf"(?i)(--{_SENSITIVE_NAME}(?:=|\s+))"
    r"(\"[^\r\n\"]*\"|'[^\r\n']*'|[^\s,;]+)"
)
_ASSIGNMENT = re.compile(
    rf"(?i)([\"']?{_SENSITIVE_NAME}[\"']?\s*[:=]\s*)"
    r"(\"[^\r\n\"]*\"|'[^\r\n']*'|[^\s,;]+)"
)
_URL_CREDENTIAL = re.compile(r"(?P<scheme>https?://)(?P<user>[^\s:/@]+):[^\s@/]+@")
_PRIVATE_KEY = re.compile(
    r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----", re.DOTALL
)
_SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "proxy_authorization",
        "cookie",
        "set_cookie",
        "password",
        "passwd",
        "pwd",
        "token",
        "access_token",
        "refresh_token",
        "github_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "aws_secret_access_key",
        "database_url",
        "private_key",
    }
)
_SENSITIVE_SUFFIXES = ("_password", "_token", "_secret", "_private_key")


def redact(text: str) -> str:
    """Return text with supported credential forms replaced."""

    sanitized = _PRIVATE_KEY.sub(REDACTED, text)
    sanitized = _URL_CREDENTIAL.sub(
        lambda match: f"{match.group('scheme')}{match.group('user')}:{REDACTED}@", sanitized
    )
    sanitized = _HEADER.sub(lambda match: f"{match.group(1)}{REDACTED}", sanitized)
    sanitized = _CLI_SECRET.sub(lambda match: f"{match.group(1)}{REDACTED}", sanitized)
    for pattern in _TOKEN_PATTERNS:
        sanitized = pattern.sub(REDACTED, sanitized)
    return _ASSIGNMENT.sub(lambda match: f"{match.group(1)}{REDACTED}", sanitized)


def contains_sensitive(text: str) -> bool:
    """Return whether the redactor recognizes a credential-like value."""

    return redact(text) != text


def redact_data(value: Any) -> Any:
    """Recursively redact structured data before persistence."""

    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            sensitive = normalized in _SENSITIVE_KEYS or normalized.endswith(_SENSITIVE_SUFFIXES)
            result[str(key)] = REDACTED if sensitive else redact_data(item)
        return result
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_data(item) for item in value)
    return redact(value) if isinstance(value, str) else value
