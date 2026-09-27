"""
bot/main.py — khởi tạo discord.py client, đăng ký sự kiện tin nhắn mới (UC13),
gọi Inference Service (UC14), rồi hành động theo ngưỡng (UC15).
Khung khởi điểm khớp luồng Activity đã chốt ở Chương III mục II của báo cáo.
"""

import os

import discord
from dotenv import load_dotenv

from bot import actions, commands

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    print(f"Đăng nhập thành công: {client.user}")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if message.content.startswith("/"):
        await commands.handle_command(message)
        return

    # UC13: tiền xử lý, UC14: gọi model, UC15: hành động theo ngưỡng
    await actions.classify_and_act(message)


def run() -> None:
    token = os.environ["DISCORD_BOT_TOKEN"]
    client.run(token)


if __name__ == "__main__":
    run()
