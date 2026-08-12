## What changed?

Explain the change in plain English.

## Why is it needed?

Link the approved specification, plan, issue, or documented problem.

## Safety review

- [ ] No password, token, cookie, private key, `.env` file, or private data was added.
- [ ] No force push, automatic merge, automatic release, or hidden destructive action was added.
- [ ] User-visible operations explain what changes and require confirmation where appropriate.
- [ ] Logs redact sensitive values before they are written.
- [ ] Cleanup remains limited to marked builder-owned data.

## Validation evidence

List exact commands and results.

```text
python -m compileall -q src
python -m pytest
python -m ruff check .
python -m mypy src
python -m bandit -r src -ll
python -m pip_audit
python -m build
```

## Beginner documentation

- [ ] `README.md` is accurate.
- [ ] Windows instructions are accurate.
- [ ] Linux instructions are accurate.
- [ ] Troubleshooting and error codes were updated when behavior changed.
- [ ] Expected successful output and safe recovery steps are documented.

## Risks and rollback

State known risks and the exact rollback method.
