from dotenv import load_dotenv
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

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
    """入力テキストと選択ロールを受け取り、LangChainを使用してLLMに問い合わせて回答文字列を返す。

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

    try:
        # プロンプトテンプレートの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_input}")
        ])

        # LLMの設定
        llm = ChatOpenAI(
            temperature=0.2,
            model="gpt-3.5-turbo",
            openai_api_key=api_key
        )
        
        # チェーンの作成と実行（新しいLangChain LCEL方式）
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"user_input": input_text})
        return response

    except Exception as e:
        # Re-raise with context
        raise RuntimeError(f"LangChain/OpenAI API 呼び出しに失敗しました: {e}")


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
