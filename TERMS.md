# Terms of Service — Toxic-Mod-Bot

**Effective Date:** November 25, 2026  
**Project Repository:** https://github.com/phTrKi3n/Toxic-mod-bot

By inviting, configuring, or interacting with **Toxic-Mod-Bot** on a Discord server, you agree to the following Terms of Service.

## 1. Description of Service

Toxic-Mod-Bot provides automated bilingual (Vietnamese and English) toxicity classification, configurable two-threshold moderation actions, private moderator review queues (`/queue`, `/resolve`, `/label`), and user appeal workflows (`/appeal`), licensed for open-source deployment under the [MIT License](LICENSE).

## 2. Acceptable Use

- Server administrators must configure and operate the bot in compliance with Discord's Terms of Service and Community Guidelines.
- Users and administrators must not attempt to overload the Inference Service through automated spam/flooding, bypass RBAC scope restrictions, or extract unauthorized data from other servers.
- Administrators must only request Discord permissions strictly required for moderation (`View Channels`, `Send Messages`, `Manage Messages`, `Read Message History`, and `applications.commands`).

## 3. Automated Moderation Accuracy & Appeals

- AI toxicity scoring is probabilistic and may produce occasional false positives or false negatives, especially for sarcasm, slang, or obfuscated text.
- Server administrators remain responsible for reviewing `HardCase` queues (`/queue`, `/resolve`), adjusting server thresholds (`/config`), and processing user appeals (`/appeal`).

## 4. Disclaimer of Warranties & Limitation of Liability

Toxic-Mod-Bot is provided **"AS IS"**, without warranties of any kind, express or implied, as set forth in the [MIT License](LICENSE). In no event shall the authors or contributors be liable for any direct or indirect damages arising from automated message deletions, service downtime, or self-hosted deployments.

## 5. Changes & Termination

We may update these Terms from time to time in this repository. Server administrators may stop using Toxic-Mod-Bot at any time by kicking the bot from their Discord server.
