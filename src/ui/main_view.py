import streamlit as st


def render_main_view() -> str | None:
    st.markdown("### 質問してみてください")

    return st.text_input(
        "例：低カロリーで時短。お酒に合うおすすめは？",
        key="question",  # ← ここが重要
        placeholder="ここに質問を入力",
    )

