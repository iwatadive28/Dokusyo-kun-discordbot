import os
import asyncio
import discord
from dotenv import load_dotenv
from pathlib import Path
import traceback
import google.generativeai as genai

# --- GeminiでMarkdown抽出 ---
def extract_book_info(text: str, model) -> str:
    print("LLMでMarkdown抽出：")
    prompt = f"""
以下のチャットログには、参加者が読んでいる本のタイトル、著者、感想などが含まれています。このログから、各書籍ごとに以下の形式で情報をまとめてください：

---
📚 書籍タイトル：（書名を抽出）
🖋 著者：（わかれば著者名、なければ「不明」）
💬 感想：（内容や気づき・学びなど、投稿から読み取れる範囲で要約）

--- の区切りで複数冊まとめてください。

【チャットログ】
{text.strip()}
""".strip()

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ 抽出エラー: {e}"

# --- Discord投稿処理 ---
async def run_bot(token, channel_id, model, messages_file: Path):
    intents = discord.Intents.default()
    intents.guilds = True
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f"🤖 Logged in as {bot.user}")

        channel = await bot.fetch_channel(channel_id)
        print(f"📨 投稿先チャンネル: {channel.name}")

        if not messages_file.exists():
            print("❌ messages.txt が存在しません")
            await bot.close()
            return

        with messages_file.open("r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            print("⚠️ 有効な投稿がありません")
            await bot.close()
            return

        print("📦 全文から抽出を実行")
        markdown = extract_book_info(text, model)
        print("📤 投稿内容:\n", markdown)

        if len(markdown) < 2000:
            await channel.send(markdown)
            print("✅ 投稿成功")
        else:
            print("⚠️ 投稿内容が長すぎてスキップされました")

        await asyncio.sleep(1)
        await bot.close()

    await bot.start(token)

# --- メイン関数 ---
def main():
    print("📂 main.py を実行しています")

    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID_TEST")
    MESSAGES_FILE = Path("messages.txt")

    print("環境変数確認：")
    print("GEMINI_API_KEY:", "OK" if GEMINI_API_KEY else "❌ 未設定")
    print("DISCORD_BOT_TOKEN:", "OK" if DISCORD_BOT_TOKEN else "❌ 未設定")
    print("DISCORD_CHANNEL_ID:", DISCORD_CHANNEL_ID if DISCORD_CHANNEL_ID else "❌ 未設定")

    if not GEMINI_API_KEY or not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
        print("❌ .env の環境変数が不足しています")
        return

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID)

    try:
        asyncio.run(run_bot(DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, model, MESSAGES_FILE))
    except Exception as e:
        print("❌ 実行中に例外が発生しました")
        traceback.print_exc()

# --- 実行ブロック ---
if __name__ == "__main__":
    main()
