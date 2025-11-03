# Streamlit LangChain LLM App

簡単な Streamlit アプリで、LangChain を使って LLM に問い合わせます。Python 3.11 で動作確認済みです。

特徴:
- テキスト入力フォーム
- ラジオボタンで専門家ロールを選択（例: AI専門家 / 健康専門家）
- 選択されたロールに応じてシステムメッセージを切り替え
- `get_llm_response(input_text, role)` 関数で LangChain に問い合わせ

## セキュリティ注意事項

⚠️ **重要**: OpenAI API キーは秘密情報です。絶対に GitHub にアップロードしないでください。

- API キーは `.env` ファイルに保存します
- `.gitignore` に `.env` を記載して、Git 管理から除外します
- Streamlit Community Cloud では、シークレット機能で API キーを設定します

## ローカルでのセットアップ:

1. 仮想環境を作る（任意）

```bash
python -m venv env
source env/bin/activate
```

2. 依存をインストール

```bash
pip install -r requirements.txt
```

3. 環境変数を設定

```bash
export OPENAI_API_KEY="sk-..."
```

4. アプリを起動

```bash
streamlit run app.py
```

注意:
- `OPENAI_API_KEY` が必要です。
- LangChain のバージョンや OpenAI モデル名は必要に応じて調整してください。

## Streamlit Community Cloud へのデプロイ

1. GitHub にコードをプッシュ
   - `.env` ファイルが `.gitignore` に含まれていることを確認
   - `pyproject.toml` で Python 3.11 を指定済み

2. Streamlit Community Cloud での設定
   - New app → GitHub リポジトリを選択
   - Python version: 3.11 を選択
   - Advanced settings → Secrets に以下を追加:
     ```
     OPENAI_API_KEY=sk-...your-api-key...
     ```
   - Deploy を実行

これでアプリがデプロイされ、シークレットとして設定した API キーを使って動作します。
