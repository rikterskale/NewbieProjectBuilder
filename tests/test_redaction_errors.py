from __future__ import annotations

from newbie_project_builder.errors import CATALOG, BuilderError
from newbie_project_builder.redaction import REDACTED, contains_sensitive, redact, redact_data


def test_redact_common_secret_formats() -> None:
    fake_github_token = "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456"
    fake_aws_key = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
    private_key_header = "-----BEGIN " + "PRIVATE KEY-----"
    private_key_footer = "-----END " + "PRIVATE KEY-----"
    fake_bearer = "abc" + "defghijklmnopqrstuvwxyz"
    fake_openai_key = "s" + "k-" + "abcdefghijklmnopqrstuvwxyz123456"
    text = "\n".join(
        (
            f"token={fake_github_token}",
            f"Authorization: Bearer {fake_bearer}",
            f"aws={fake_aws_key}",
            'password="two word secret"',
            '"access_token": "json-secret-value"',
            "--api-key cli-secret-value",
            f"openai={fake_openai_key}",
            "https://user:secret@example.com/path",
            f"{private_key_header}\nsecret\n{private_key_footer}",
        )
    )
    sanitized = redact(text)
    assert "two word secret" not in sanitized
    assert "json-secret-value" not in sanitized
    assert "cli-secret-value" not in sanitized
    assert fake_openai_key not in sanitized
    assert "abcdefghijklmnopqrstuvwxyz123456" not in sanitized
    assert fake_aws_key not in sanitized
    assert "user:secret@" not in sanitized
    assert "BEGIN PRIVATE KEY" not in sanitized
    assert sanitized.count(REDACTED) >= 9
    assert contains_sensitive(text)
    assert not contains_sensitive("This sentence discusses tokens without assigning one.")


def test_redact_data_recursively() -> None:
    value = {
        "token": "secret",
        "nested": {"api-key": "abc", "safe": "token=secret-value"},
        "items": ["Bearer abcdefghijkl", ("password=bad",)],
        "service_access_token": "suffix-secret",
        "count": 3,
    }
    sanitized = redact_data(value)
    assert sanitized["token"] == REDACTED
    assert sanitized["nested"]["api-key"] == REDACTED
    assert sanitized["nested"]["safe"] == f"token={REDACTED}"
    assert sanitized["items"][0] == REDACTED
    assert sanitized["items"][1] == (f"password={REDACTED}",)
    assert sanitized["service_access_token"] == REDACTED
    assert sanitized["count"] == 3


def test_builder_error_known_unknown_and_render() -> None:
    error = BuilderError("NPB-101", "git executable missing")
    assert error.code == "NPB-101"
    assert error.info == CATALOG["NPB-101"]
    rendered = error.render()
    assert "ERROR NPB-101" in rendered
    assert "git executable missing" in rendered
    assert "Nothing else was attempted" in rendered
    unknown = BuilderError("NOPE")
    assert unknown.code == "NPB-901"
    assert "UNEXPECTED INTERNAL ERROR" in str(unknown)
