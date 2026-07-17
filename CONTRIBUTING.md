# Contributing

Keep changes evidence-bound and portable across Windows, macOS, and Linux.

Before opening a pull request:

```bash
python -m py_compile skills/maintain-codex-handoff/scripts/handoff.py skills/maintain-codex-handoff/scripts/hook.py
python -m unittest discover -s tests -v
python ~/.codex/skills/beautify-github-readme/scripts/audit_readme.py README.md
python ~/.codex/skills/beautify-github-readme/scripts/audit_readme.py README.zh-CN.md
```

Do not add private research data, repository-specific SHAs, user paths, tokens,
or claims that cannot be verified from the public package.
