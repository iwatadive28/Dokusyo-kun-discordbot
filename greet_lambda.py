import os
import discord
import asyncio

DISCORD_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

MESSAGES = {
    "day_before": "明日の朝も「もくもく読書会」やります！\nジャンル不問ですし、ほかの人の面白そうな本と出合えるかもしれません。気軽にご参加ください～！",
    "start_notice": "おはようございます☀ 今日ももくもく読書していきましょう！\n\n「読む本のタイトル or 内容」を軽く投稿してください。\n例：「○○の設計思想（3章から）読みます」\n\n📖読書スタート📖",
    "end_notice": "終了5分前～アウトプットタイムです\n読んだ内容や感想・学びを共有（短くてもOK！）"
}

async def send_message(mode):
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"✅ Discordに接続成功！モード: {mode}")
        channel = await client.fetch_channel(CHANNEL_ID)
        await channel.send(MESSAGES.get(mode, f"（未定義モード: {mode}）"))
        await client.close()

    await client.start(DISCORD_TOKEN)

def lambda_handler(event, context):
    print("🚀 Lambda 起動")
    print(f"📦 イベント受信: {event}")

    # モード取得とバリデーション
    mode = event.get("mode")
    if not mode:
        print("❌ モードが指定されていません")
        return {
            "statusCode": 400,
            "body": "Error: 'mode' must be specified in the event payload."
        }

    if mode not in MESSAGES:
        print(f"❌ 無効なモード: {mode}")
        return {
            "statusCode": 400,
            "body": f"Error: Invalid mode '{mode}' specified."
        }

    print(f"🟢 使用モード: {mode}")
    asyncio.run(send_message(mode))
    return {
        "statusCode": 200,
        "body": f"Message sent in mode: {mode}"
    }
