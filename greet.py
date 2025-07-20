import os
import discord
import asyncio
from dotenv import load_dotenv
from datetime import datetime

# --- 環境読み込み ---
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID_TEST"))

# --- 投稿メッセージ定義 ---
MESSAGES = {
    "day_before": "明日の朝も「もくもく読書会」やります！\nジャンル不問ですし、ほかの人の面白そうな本と出合えるかもしれません。気軽にご参加ください～！",
    "start_notice": "おはようございます☀ 今日ももくもく読書していきましょう！\n\n「読む本のタイトル or 内容」を軽く投稿してください。\n例：「○○の設計思想（3章から）読みます」\n\n📖読書スタート📖",
    "end_notice": "終了5分前～アウトプットタイムです\n読んだ内容や感想・学びを共有（短くてもOK！）"
}

# --- メッセージ送信処理 ---
async def send_discord_message(tag: str):
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"🤖 Bot logged in as {client.user}")
        channel = await client.fetch_channel(CHANNEL_ID)

        if tag not in MESSAGES:
            print(f"❌ 不明なタグ: {tag}")
            await client.close()
            return

        message = MESSAGES[tag]
        await channel.send(message)
        print(f"✉️ 投稿完了: {tag}")
        await client.close()

    await client.start(TOKEN)

# --- 実行ブロック（例：python greet.py saturday_morning） ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python greet.py [day_before|start_notice|end_notice]")
    else:
        asyncio.run(send_discord_message(sys.argv[1]))
