# Dokusyo-kun-discordbot

このBotは、Discordサーバーで開催される「もくもく読書会」をサポートするために作られました。  
主に以下の2つの機能を備えています：

---

## 機能概要

### 1. 読書ログのまとめ投稿（GitHub Actions 実行）

- 毎週の読書ログ投稿を収集・要約し、Discordに自動投稿します。
- **GitHub Actions** により、週1回のスケジュールで自動実行されます。

使用ファイル：

- `main.py`：読書ログを要約・構造化し、Discordに投稿
- `fetch_messages.py`：Discordから過去ログを取得する補助スクリプト
- `.github/workflows/booklog.yml`：週次の自動実行設定ファイル（GitHub Actions）

### 2. Greet投稿（AWS Lambda + EventBridge）

- 読書会の前日や当日の開始・終了時に、Discordへリマインド／アナウンスメッセージを投稿します。
- **AWS Lambda + EventBridge (cron)** により、指定時刻に自動で投稿されます。

使用ファイル：

- `greet_lambda.py`：モードに応じた定型メッセージを送信するLambdaスクリプト
- `lambda_package/`：Lambdaにアップロードするコード・依存ファイル
- `lambda.zip`：LambdaにアップロードするZIPパッケージ

---

## 読書ログのまとめ投稿（GitHub Actions 実行）

### ローカル実行

#### 環境変数の設定

`.env` ファイル等に以下の環境変数を設定してください：

```
DISCORD_BOT_TOKEN=xxxxx
DISCORD_CHANNEL_ID=1234567890
DISCORD_CHANNEL_ID_TEST=1234567890
GEMINI_API_KEY=sk-xxxxx
```

※ 現時点では Gemini API を使用しています。

#### 実行手順

```bash
python3 fetch_messages.py  # 過去7日間の投稿を取得
python3 main.py            # 投稿内容から読書ログを生成・投稿
```

### GitHub Actions での定期実行

定期実行のワークフローは `.github/workflows/booklog.yml` に定義されています。

#### GitHub Secrets の設定

Discord Botの認証やチャンネル指定などに必要な情報は、GitHub Secrets に登録してください。

1. リポジトリの [Settings] → [Secrets and variables] → [Actions] に移動
2. [New repository secret] をクリックし、以下のように設定

| Name                      | 説明                                       |
|---------------------------|--------------------------------------------|
| `DISCORD_BOT_TOKEN`       | Discord Bot のトークン                     |
| `DISCORD_CHANNEL_ID`      | 本番用チャンネルID                         |
| `DISCORD_CHANNEL_ID_TEST` | テスト用チャンネルID（任意）              |
| `OPENAI_API_KEY`          | OpenAI API のキー（必要な場合のみ）        |

`main.py` や `fetch_messages.py` がこれらの環境変数を参照します。

---

## Greet投稿（AWS Lambda + EventBridge）

このプロジェクトでは、Lambda関数のコードをGitHubで管理し、必要に応じて手動でデプロイします。

### 初期準備

#### AWS Lambda 関数の作成

1. AWSマネジメントコンソールにログイン
2. 「Lambda」→「関数の作成」→「一から作成」
3. 関数名、ランタイム（例：Python 3.10）を設定
4. 適切なIAMロールを設定  
   ※ Secrets Manager等へのアクセスを許可しておくと便利です

#### 環境変数の設定（Lambda内）

| 環境変数キー            | 内容                         |
|-------------------------|------------------------------|
| `DISCORD_BOT_TOKEN`     | Discord Bot のトークン       |
| `DISCORD_CHANNEL_ID`    | 投稿先チャンネルのID         |

### Lambda ZIPパッケージの作成とアップロード

#### ZIPパッケージの作成手順

```bash
mkdir lambda_package
# 必要なPythonスクリプトやライブラリを配置
pip install -r requirements.txt -t lambda_package
cp greet_lambda.py lambda_package/
cd lambda_package
zip -r ../lambda.zip .
```

#### ZIPのアップロード手順

1. Lambda関数の「コード」タブを開く
2. 「アップロード」→「.zipファイルをアップロード」を選択
3. 作成した `lambda.zip` をアップロードし、保存

---

### テスト実行方法

Lambda管理画面 → 「テスト」から以下のような JSON を指定して実行：

```json
{
  "mode": "start_notice"
}
```

`mode` には以下のいずれかを指定してください：

- `day_before`
- `start_notice`
- `end_notice`

---

### スケジュール実行の設定（EventBridge）

EventBridge → 「ルールの作成」から、以下のスケジュールを設定してください：

| モード         | JST 実行時刻 | cron式（UTC）   |
|----------------|--------------|-----------------|
| `day_before`   | 金曜 21:00   | `0 12 * * 5`     |
| `start_notice` | 土曜 07:00   | `0 22 * * 5`     |
| `end_notice`   | 土曜 07:55   | `55 22 * * 5`    |

---

### 補足事項

- Lambda関数のログは CloudWatch Logs で確認できます
- Lambda のタイムアウト設定は **最低10秒以上** を推奨します
