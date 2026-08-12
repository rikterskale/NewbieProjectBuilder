"""Stable beginner-facing error codes and recovery cards."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorInfo:
    title: str
    explanation: str
    fixes: tuple[str, ...]


CATALOG: dict[str, ErrorInfo] = {
    "NPB-001": ErrorInfo(
        "Unsupported operating system",
        "Automatic setup supports Windows and APT-based Ubuntu, Debian, and Kali Linux.",
        ("Use diagnostics only.", "Follow the manual Linux guide without bypassing safeguards."),
    ),
    "NPB-002": ErrorInfo(
        "Not enough disk space",
        "At least 2 GB of free space is required for tools, logs, backups, and project files.",
        ("Free disk space.", "Run diagnostics again before continuing."),
    ),
    "NPB-003": ErrorInfo(
        "Internet unavailable",
        "GitHub could not be reached over HTTPS. Local-only generation can still work.",
        ("Check Wi-Fi, VPN, proxy, and firewall settings.", "Try again or choose local-only."),
    ),
    "NPB-010": ErrorInfo(
        "WinGet unavailable",
        "Windows Package Manager was not found.",
        ("Install or update App Installer from Microsoft Store.", "Restart the builder."),
    ),
    "NPB-011": ErrorInfo(
        "APT unavailable",
        "Automatic Linux installation requires APT on Ubuntu, Debian, or Kali Linux.",
        ("Use diagnostics only.", "Follow docs/START_HERE_LINUX.md."),
    ),
    "NPB-101": ErrorInfo(
        "Git not found",
        "Git records changes and is required for GitHub workflows.",
        ("Choose the guided Git installation.", "Restart the builder after installation."),
    ),
    "NPB-102": ErrorInfo(
        "GitHub CLI not found",
        "GitHub CLI is used for browser sign-in and optional repository operations.",
        ("Choose the guided GitHub CLI installation.", "Local-only projects remain available."),
    ),
    "NPB-103": ErrorInfo(
        "Python not found",
        "Python 3.11 or newer is required for the shared builder core.",
        ("Use the platform launcher to install Python.", "Restart the terminal after installation."),
    ),
    "NPB-104": ErrorInfo(
        "Codex not found",
        "Codex is optional for scaffolding but required for the guided AI workflow.",
        ("Install Codex from the official OpenAI source.", "Restart Codex and the builder."),
    ),
    "NPB-105": ErrorInfo(
        "GitHub Desktop not found",
        "GitHub Desktop is the recommended Windows interface for routine Git operations.",
        ("Install GitHub Desktop on Windows.", "Linux users may use GitHub CLI."),
    ),
    "NPB-201": ErrorInfo(
        "GitHub sign-in required",
        "No active authenticated GitHub CLI account was found.",
        ("Use browser sign-in.", "Never paste a token into this program or a support message."),
    ),
    "NPB-203": ErrorInfo(
        "GitHub permission insufficient",
        "The active account cannot perform the requested repository action.",
        ("Confirm the account and repository owner.", "Ask an administrator; do not share credentials."),
    ),
    "NPB-301": ErrorInfo(
        "Superpowers not verified",
        "Codex remains the source of truth for plugin availability and workspace policy.",
        ("Open Codex Plugins and install Superpowers.", "Ask a workspace administrator if blocked."),
    ),
    "NPB-302": ErrorInfo(
        "Agency Agents setup failed",
        "The official repository or one of its conversion/install scripts returned an error.",
        ("Open the latest log.", "Use the official Agency Agents desktop app as a fallback."),
    ),
    "NPB-401": ErrorInfo(
        "Project folder is not empty",
        "The builder refuses to silently replace an existing project.",
        ("Choose another name or folder.", "Back up and inspect existing files first."),
    ),
    "NPB-402": ErrorInfo(
        "Invalid project name",
        "A portable project name must contain letters or numbers and avoid reserved paths.",
        ("Use a name such as Weather Helper.", "Avoid slashes, device names, and punctuation-only names."),
    ),
    "NPB-403": ErrorInfo(
        "Repository already exists or creation failed",
        "GitHub could not create the selected repository.",
        ("Choose another name.", "Confirm account permissions and inspect the existing repository."),
    ),
    "NPB-501": ErrorInfo(
        "Git operation failed",
        "Git returned an error. The builder did not intentionally delete project files.",
        ("Open the latest log and read the Git error.", "Run diagnostics before retrying."),
    ),
    "NPB-502": ErrorInfo(
        "Work is on main",
        "Unfinished feature work should not be pushed directly from the trusted main branch.",
        ("Create a feature branch without discarding files.", "Review changes before publishing."),
    ),
    "NPB-503": ErrorInfo(
        "Push rejected",
        "The remote may have newer work, protections, or an authentication problem.",
        ("Do not force-push.", "Fetch, inspect, and resolve the specific cause."),
    ),
    "NPB-601": ErrorInfo(
        "Tests failed",
        "One or more automated behavior checks did not pass.",
        ("Reproduce and find the root cause.", "Do not delete or skip tests to get green."),
    ),
    "NPB-701": ErrorInfo(
        "Possible secret detected",
        "A token, password, private key, or credential-like value may be present.",
        ("Stop publishing and rotate real credentials.", "Remove the secret and scan again."),
    ),
    "NPB-801": ErrorInfo(
        "GitHub Actions failed",
        "A remote automated check did not complete successfully.",
        ("Read the first failing step.", "Compare OS, runtime, and dependencies with local checks."),
    ),
    "NPB-901": ErrorInfo(
        "Unexpected internal error",
        "The builder encountered an error without a more specific public code.",
        ("Create a sanitized support bundle.", "Share the code and bundle without credentials."),
    ),
}


class BuilderError(RuntimeError):
    """Expected categorized error suitable for direct beginner display."""

    def __init__(self, code: str, details: str = "") -> None:
        self.code = code if code in CATALOG else "NPB-901"
        self.details = details
        super().__init__(self.render())

    @property
    def info(self) -> ErrorInfo:
        return CATALOG[self.code]

    def render(self) -> str:
        lines = [
            "=" * 60,
            f"ERROR {self.code}: {self.info.title.upper()}",
            "=" * 60,
            "",
            "What happened:",
            self.info.explanation,
        ]
        if self.details:
            lines.extend(("", "Technical summary:", self.details))
        lines.extend(("", "Recommended fixes:"))
        lines.extend(f"  {index}. {fix}" for index, fix in enumerate(self.info.fixes, 1))
        lines.extend(("", "Nothing else was attempted after this error."))
        return "\n".join(lines)
