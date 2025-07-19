import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
DAYS_BACK = 7  # 直近何日分を取得するか

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🔗 Bot logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ チャンネルが見つかりません")
        await client.close()
        return

    # メッセージ取得（最新500件 or 日数ベース）
    messages = []
    async for msg in channel.history(limit=500):
        if msg.author.bot:
            continue
        messages.append(msg.content.strip())

    # ファイルに保存（またはこのままLLMに渡す）
    with open("messages.txt", "w", encoding="utf-8") as f:
        for m in messages:
            f.write(m + "\n")

    print(f"✅ メッセージ {len(messages)} 件を保存しました")
    await client.close()

# 実行
asyncio.run(client.start(TOKEN))
