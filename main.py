import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# .env の読み込み
load_dotenv()

# 環境変数の取得
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# OpenAI クライアントの初期化
client = OpenAI(api_key=OPENAI_API_KEY)

# 仮の読書感想（実運用では Discord API で取得）
sample_messages = [
    "📢 先週読んだ『センスの哲学』（千葉雅也）がめちゃくちゃ良かった。手を動かすことの大切さを改めて感じた一冊。",
    "最近読んだ『FACTFULNESS』、思い込みを疑うという視点にハッとした。データを見る目が変わる本。"
]

# LLM で書籍情報を抽出
def extract_book_info(text):
    prompt = f"""
以下の投稿から、書籍タイトル・著者・感想をMarkdown形式で抽出してください：

投稿：
{text}

出力形式（マークダウン）：
📚 書籍タイトル：（必ず1冊のみ）
🖋 著者：（不明なら「不明」）
💬 感想：（2行程度に要約）
    """.strip()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# まとめ本文
markdown = "今週の読書ログまとめです 📚\n\n"

# 各投稿を処理して Markdown に追加
for post in sample_messages:
    markdown += extract_book_info(post) + "\n\n"

# Discord Webhook へ送信
response = requests.post(DISCORD_WEBHOOK_URL, json={"content": markdown})

if response.status_code == 204:
    print("✅ Webhook投稿に成功しました。")
else:
    print(f"❌ Webhook投稿に失敗しました（ステータス: {response.status_code}）")
    print(response.text)
