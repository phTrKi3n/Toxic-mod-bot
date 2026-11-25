# Privacy Policy — Toxic-Mod-Bot

**Effective Date:** November 25, 2026  
**Project Repository:** https://github.com/phTrKi3n/Toxic-mod-bot

This Privacy Policy describes how **Toxic-Mod-Bot** collects, processes, stores, and protects data when added to a Discord server ("Guild") in accordance with Discord's Developer Policy and Terms of Service.

## 1. Data We Collect

When the bot operates in a server where it has been authorized with `Message Content Intent`, it processes only the minimum data necessary for automated toxicity moderation, review queues, and user appeals:

- **Guild Metadata**: Discord Guild ID, Guild name, and server moderation thresholds (`threshold_low`, `threshold_high`).
- **User Metadata**: Discord User ID, Discord username, and assigned moderation role tier (`member`, `labeler`, `mod`, `admin`).
- **Message & Moderation Records**: Discord Message ID, detected language tag (`vi` / `en`), message text content for flagged/moderated records, classification confidence score, `HardCase` review labels, `ModerationAction` audit logs, and user-submitted `/appeal` reasons.
- **Inference Service Payloads**: Only normalized message text is sent from the bot service to the local/private Inference Service (`/classify`); Discord user IDs, guild IDs, and bot tokens are never included in `/classify` requests.

## 2. How We Use Data

- **Real-Time Toxicity Classification**: Evaluate incoming Vietnamese and English messages against server-configured thresholds (`ignore`, `flag`, `delete`).
- **Human-in-the-Loop Moderation & Appeals**: Allow server moderators to review borderline `HardCase` entries privately (`/queue`, `/resolve`, `/label`) and allow members to submit appeals (`/appeal`).
- **Model Retraining (Self-Hosted Instances)**: When operated by a server administrator, corrected `HardCase` labels may be exported by that operator to fine-tune their own local model weights.

## 3. Data Storage, Access Control & Sharing

- All data is stored strictly inside the operator's self-hosted PostgreSQL database (`db`) with server-scoped isolation (`server_id` / `guild_id`).
- **No Third-Party Data Sharing or Sale**: Message content and user data are **not** sold, rented, shared with advertising brokers, or transmitted to external commercial AI APIs (inference runs locally via bundled XLM-RoBERTa models).
- Direct messages (DMs) and ephemeral Slash Command interactions are used for moderation notices and `/queue` output so sensitive moderation metadata is not posted in public channels.

## 4. Data Retention & Deletion Rights

- Operators retain moderation logs only for as long as needed to audit moderation decisions, resolve appeals, and manage server safety.
- Server administrators or individual Discord users may request deletion of their stored user/message/appeal records (or full server data removal by removing the bot and deleting matching `server_id` rows from PostgreSQL) via the server administrator or via GitHub Issues (`https://github.com/phTrKi3n/Toxic-mod-bot/issues`).

## 5. Contact

For privacy questions or data removal requests regarding the reference deployment, please open an issue at https://github.com/phTrKi3n/Toxic-mod-bot/issues or contact the bot operator of your Discord server.
