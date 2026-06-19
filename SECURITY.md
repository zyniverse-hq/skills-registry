# Security Policy

The skills in this registry ship runnable code (scripts under `skills/*/scripts/`)
that executes in your environment, so we take security reports seriously.

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Email **varun@zysk.tech** with:

- the affected skill (folder name) and file(s),
- a description of the issue and its impact,
- steps to reproduce or a proof of concept, if possible.

We aim to acknowledge reports within 3 business days and to share a remediation
timeline after triage. Please give us a reasonable window to address the issue
before any public disclosure.

## Scope

**In scope**
- Malicious or unsafe behavior in a bundled skill or its scripts (data exfiltration,
  destructive commands, credential leakage, prompt-injection sinks).
- Supply-chain risks in a skill's dependencies or bundled assets.
- Issues in the registry tooling (`scripts/`) or CI workflows.

**Out of scope**
- Vulnerabilities in third-party tools a skill merely invokes — report those upstream.
- Issues requiring an already-compromised local machine, or social engineering.

## Installing skills safely

Skills run with your agent's permissions. Review a skill's `SKILL.md` and any
`scripts/` before installing — especially scripts that touch the network, the
shell, or `gh`/git.
