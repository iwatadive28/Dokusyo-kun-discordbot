import os
import asyncio
import discord
from dotenv import load_dotenv
from datetime import datetime, timedelta

# .env からトークンとチャンネルIDを読み込み
load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
DAYS_BACK = 7  # 過去〇日分

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

    # 日付フィルター：過去7日間の投稿のみ
    since = datetime.utcnow() - timedelta(days=DAYS_BACK)
    print(f"📅 {DAYS_BACK}日前以降のメッセージを取得中...")

    messages = []
    async for msg in channel.history(after=since, limit=None, oldest_first=True):
        if msg.author.bot:
            continue
        content = msg.content.strip()
        if content:
            messages.append(content)

    with open("messages.txt", "w", encoding="utf-8") as f:
        for m in messages:
            f.write(m + "\n")

    print(f"✅ {len(messages)} 件のメッセージを messages.txt に保存しました")
    await client.close()

# 実行
asyncio.run(client.start(TOKEN))
