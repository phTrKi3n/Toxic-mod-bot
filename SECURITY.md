# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `1.0.x` (`main`) | Yes |
| `< 1.0.0` | No |

## Security Architecture & Controls

- **Fail-Closed RBAC (`bot/rbac.py`)**: Administrative and moderation commands (`/config`, `/queue`, `/resolve`, `/label`) require authorization both on Discord (explicit role, guild owner, or native Discord moderator/admin permission) and in PostgreSQL (`app_user.role`, `server.is_active`), with guild-scoped record lookups (`scoped_message`, `scoped_hardcase`) and strict appeal ownership checks (`owned_appeal_target`).
- **Role Restriction Invariant**: Database role restrictions on existing `app_user` records are preserved across commands (`RBAC_AUTO_SYNC_ROLES=false` by default).
- **Queue Privacy & Error Sanitization**: Moderator review queues are never leaked into public Discord channels when DMs are disabled, and internal database/inference exceptions are sanitized from user responses.
- **Inference Hardening & Rate Limiting**: Per-user sliding-window rate limits protect the Inference Service against spam/DoS bursts, `/classify` enforces strict request payload bounds (`max_length=4000`), and `/ops/reload` supports `X-Ops-Api-Key` authentication.
- **Container & Host Isolation**: Containers run as non-root users (`botuser`, `appuser`), host ports in `docker-compose.yml` bind to `127.0.0.1` by default, and CI enforces blocking `black`, `isort`, `pytest`, and `pip-audit -r requirements.txt` checks.

## Reporting a Vulnerability

Please do **not** open a public GitHub issue for security vulnerabilities.

1. Use **GitHub Private Vulnerability Reporting** (`Security -> Advisories -> Report a vulnerability`) on `https://github.com/phTrKi3n/Toxic-mod-bot`, or contact the repository maintainer directly.
2. Include clear reproduction steps, affected files/versions, and potential impact.
3. Avoid accessing or modifying live data outside servers you explicitly own or administer.
