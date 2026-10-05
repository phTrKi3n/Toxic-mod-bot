# RBAC security implementation (SEC)

- `/queue`, `/resolve`: Discord mod/admin **AND** DB mod/admin when DB configured.
- `/config`: Discord admin **AND** DB admin when DB configured.
- `/appeal`: available to human guild members; **must** check `owned_appeal_target` before persisting the appeal.
- `label` permission: labeler/mod/admin; DEV must use `rbac.allowed(message, 'label')` at every labeling entry point.
- All moderation reads and writes **must** use `scoped_message` or `scoped_hardcase` for the invoking guild before acting. A bare numeric ID is not authorization.
- Do not send queue data to public channels. Use restricted channels or ephemeral interactions when DEV implements commands.
- Default fail closed if DATABASE_URL is missing, DB is unreachable, user or guild missing/inactive, or role insufficient. `RBAC_DISCORD_ONLY=true` is an explicit less-restrictive compatibility mode for deployments without DB.
- DB `app_user.role` is global in the current agreed schema; guild-specific grants come from Discord member roles. Do not add new schema fields without team agreement.
- Existing command handlers deliberately remain DEV placeholders (`NotImplementedError`); this change completes authorization guards and scoped access primitives, **not** business command implementations or audit persistence.

## Validation

```powershell
python -m pip install -r requirements.txt
python -m pytest tests/test_rbac_db.py tests/test_rbac.py -v
python -m pytest tests/ -v
python -m black --check bot/rbac.py bot/commands.py tests/test_rbac_db.py
python -m isort --check bot/rbac.py bot/commands.py tests/test_rbac_db.py
git diff --check
```

Legacy `tests/test_rbac_commands.py` expects Discord-only authorization: set `RBAC_DISCORD_ONLY=true` **only in test process** for those legacy tests, or migrate their fixtures to database-backed sessions. Do not set this in production merely to make tests pass.
