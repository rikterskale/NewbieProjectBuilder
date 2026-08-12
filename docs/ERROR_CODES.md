# Error Codes

Error codes remain stable so a beginner can search documentation or ask for help without
copying an entire log.

| Code | Meaning | First safe action |
|---|---|---|
| `NPB-001` | Unsupported operating system | Use diagnostics or the manual guide |
| `NPB-002` | Less than 2 GB free disk space | Free space and rerun diagnostics |
| `NPB-003` | GitHub HTTPS connection unavailable | Check network, VPN, proxy, and firewall |
| `NPB-010` | WinGet unavailable | Install/update Microsoft App Installer |
| `NPB-011` | APT unavailable or unsupported Linux | Do not guess a package-manager command |
| `NPB-101` | Git missing | Use guided Git installation |
| `NPB-102` | GitHub CLI missing | Install it or keep the project local |
| `NPB-103` | Python 3.11+ missing | Use the platform launcher |
| `NPB-104` | Codex unavailable | Install from the official OpenAI source |
| `NPB-105` | GitHub Desktop unavailable | Install it on Windows or use GitHub CLI on Linux |
| `NPB-201` | GitHub authentication required | Use browser sign-in; never paste a token |
| `NPB-203` | GitHub permission insufficient | Verify account and ask an administrator |
| `NPB-301` | Superpowers not verified | Check Codex Plugins and workspace policy |
| `NPB-302` | Agency Agents setup failed | Read the first failing logged command |
| `NPB-401` | Project destination is nonempty | Choose another folder or inspect existing files |
| `NPB-402` | Project name is invalid | Use a simple portable name |
| `NPB-403` | GitHub repository creation failed | Check name, account, and permissions |
| `NPB-501` | Git operation failed | Read the Git stderr in the latest log |
| `NPB-502` | Feature publish attempted from `main` | Create a feature branch without discarding files |
| `NPB-503` | Push rejected | Do not force-push; fetch and investigate |
| `NPB-601` | Tests failed | Reproduce and identify root cause |
| `NPB-701` | Possible secret detected | Stop publishing and rotate real credentials |
| `NPB-801` | GitHub Actions failed | Read the first failed step |
| `NPB-901` | Unexpected internal error | Create and review a sanitized support bundle |

Every error card contains a plain-language explanation, safe recovery guidance, and a
statement that no additional action was attempted after the error.
