"""
bot/main.py — Discord client, Slash Command registration, and real-time message moderation.
"""

import os
from typing import Literal

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

from bot import actions, commands
from db.session import init_db

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name="status",
    description="Check Toxic-Mod-Bot health, active AI model, and server thresholds",
)
async def slash_status(interaction: discord.Interaction) -> None:
    await commands.handle_status_slash(interaction)


@tree.command(
    name="queue",
    description="List pending borderline HardCase messages for moderator review",
)
async def slash_queue(interaction: discord.Interaction) -> None:
    await commands.handle_slash_command(interaction, "/queue")


@tree.command(
    name="appeal",
    description="Submit an appeal for one of your moderated messages",
)
@app_commands.describe(
    message_id="Target Discord message ID",
    reason="Reason for appealing the moderation action",
)
async def slash_appeal(
    interaction: discord.Interaction, message_id: str, reason: str
) -> None:
    await commands.handle_slash_command(interaction, f"/appeal {message_id} {reason}")


@tree.command(
    name="resolve",
    description="Resolve a flagged message or pending appeal (Mod/Admin)",
)
@app_commands.describe(
    message_id="Target Discord message ID",
    action="Moderation resolution action",
)
async def slash_resolve(
    interaction: discord.Interaction,
    message_id: str,
    action: Literal["delete", "keep", "restore", "approve", "reject"],
) -> None:
    await commands.handle_slash_command(interaction, f"/resolve {message_id} {action}")


@tree.command(
    name="label",
    description="Label a pending HardCase for dataset retraining (Labeler/Mod/Admin)",
)
@app_commands.describe(
    hardcase_id="HardCase ID from /queue",
    label="Ground-truth toxicity label",
)
async def slash_label(
    interaction: discord.Interaction,
    hardcase_id: int,
    label: Literal["toxic", "not_toxic"],
) -> None:
    await commands.handle_slash_command(interaction, f"/label {hardcase_id} {label}")


@tree.command(
    name="config",
    description="Update toxicity score thresholds for this server (Admin)",
)
@app_commands.describe(
    param="Threshold parameter to update",
    value="Threshold float value between 0.0 and 1.0",
)
async def slash_config(
    interaction: discord.Interaction,
    param: Literal["threshold_low", "threshold_high"],
    value: float,
) -> None:
    await commands.handle_slash_command(interaction, f"/config {param} {value}")


async def _sync_guild_commands(guild: discord.Guild) -> None:
    try:
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
    except Exception as err:
        print(f"Không thể đồng bộ slash commands cho guild {guild.id}: {err}")


@client.event
async def on_ready() -> None:
    print(f"Đăng nhập thành công: {client.user}")
    for guild in getattr(client, "guilds", ()):
        await _sync_guild_commands(guild)
    try:
        await tree.sync()
    except Exception as err:
        print(f"Không thể đồng bộ global slash commands: {err}")


@client.event
async def on_guild_join(guild: discord.Guild) -> None:
    await _sync_guild_commands(guild)


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if message.content.startswith("/"):
        await commands.handle_command(message)
        return

    await actions.classify_and_act(message)


def run() -> None:
    init_db()
    token = os.getenv("DISCORD_BOT_TOKEN") or os.environ["DISCORD_TOKEN"]
    client.run(token)


if __name__ == "__main__":
    run()
