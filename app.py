from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

# Try multiple import paths for ChatOpenAI to support different langchain versions.
ChatOpenAI = None
LLMChain = None
ChatPromptTemplate = None
SystemMessagePromptTemplate = None
HumanMessagePromptTemplate = None
import traceback
try:
    # Preferred import (works for many langchain versions)
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import (
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
    )
except Exception:
    try:
        # Some langchain builds expose ChatOpenAI under a submodule
        from langchain.chat_models.openai import ChatOpenAI
        from langchain.chains import LLMChain
        from langchain.prompts import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
        )
    except Exception:
        try:
            # Other langchain versions use a generic OpenAI LLM class
            from langchain import OpenAI as ChatOpenAI
            from langchain.chains import LLMChain
            # prompts API might differ; fall back to simple string prompt if missing
            from langchain.prompts import (
                ChatPromptTemplate,
                SystemMessagePromptTemplate,
                HumanMessagePromptTemplate,
            )
        except Exception:
            # Keep ChatOpenAI as None — we'll fall back to direct openai API in that case.
            tb = traceback.format_exc()
            st.warning(
                "langchain の ChatOpenAI をインポートできませんでした。\n`langchain` のバージョンと `requirements.txt` を確認してください。\n代替として OpenAI SDK を直接使って動かします。\n詳細:"
            )
            st.code(tb)


st.title("LangChain を使った簡易 LLM アプリ")

# アプリ概要と操作方法の表示
st.subheader("アプリの概要")
st.write(
    "このアプリは、ユーザーが入力したテキストを LangChain 経由で LLM に送信し、選択した専門家ロールに応じた応答を取得・表示します。"
)

st.subheader("使い方（操作手順）")
st.markdown(
    "1. 画面上部のラジオボタンで専門家モードを選択します（例: AI専門家 / 健康専門家）。\n"
    "2. テキストエリアに質問や相談したい内容を入力します。\n"
    "3. 「実行」ボタンを押すと、LLM に問い合わせを行い、回答が下部に表示されます。\n"
    "4. 医療や法的な重要判断が必要な場合は専門家に相談してください。"
)

st.info(
    "注意: このアプリは OpenAI API を使用します。環境変数 `OPENAI_API_KEY` を設定してから実行してください。"
)

# 定義する専門家ロール（ここは自由に追加できます）
ROLE_SYSTEM_PROMPTS = {
    "AI専門家": (
        "あなたは高度なAIと機械学習の専門家です。ユーザーの質問に対して、技術的に正確で簡潔、かつ実践的な説明を提供してください。必要なら簡単なコード例やアルゴリズムの擬似コードを含めてください。"
    ),
    "健康専門家": (
        "あなたは医療と健康分野の専門家です。一般的な健康アドバイスをわかりやすく提供してください。ただし、診断や治療の確定は避け、専門医の受診を促す表現を含めてください。"
    ),
}

selected_role = st.radio("専門家モードを選択してください。", list(ROLE_SYSTEM_PROMPTS.keys()))

user_input = st.text_area("入力テキスト", height=150)


def get_llm_response(input_text: str, role: str) -> str:
    """入力テキストと選択ロールを受け取り、LLM（LangChain）へ問い合わせて回答文字列を返す。

    引数:
      - input_text: ユーザーが入力したテキスト
      - role: ROLE_SYSTEM_PROMPTS のキー（例: 'AI専門家'）

    戻り値:
      - LLM の応答テキスト
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY が設定されていません。環境変数を確認してください。")

    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["AI専門家"])

    # If ChatOpenAI is available from langchain, use LLMChain as before.
    if ChatOpenAI is not None and LLMChain is not None and ChatPromptTemplate is not None:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template("{user_input}"),
            ]
        )

        # ChatOpenAI を使って LLM 呼び出し（model_name は環境に応じて変更してください）
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-3.5-turbo")
        chain = LLMChain(llm=llm, prompt=prompt)

        # LLMChain.run は prompt の変数名に合わせて kwargs を渡す
        response = chain.run(user_input=input_text)
        return response

    # Fallback: use OpenAI SDK directly if langchain ChatOpenAI is unavailable
    try:
        import openai

        openai.api_key = api_key
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text},
        ]
        resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        # Re-raise with context
        raise RuntimeError(f"LLM 呼び出しに失敗しました: {e}")


if st.button("実行"):
    st.divider()
    if not user_input:
        st.error("入力テキストを入力してください。")
    else:
        with st.spinner("LLMに問い合わせ中..."):
            try:
                answer = get_llm_response(user_input, selected_role)
                st.markdown("### 回答")
                st.write(answer)
            except Exception as e:
                st.error(f"LLM 呼び出しでエラーが発生しました: {e}")
