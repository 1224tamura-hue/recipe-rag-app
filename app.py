import os

import streamlit as st
from dotenv import load_dotenv

from src.config import get_settings
from src.sample_data import get_sample_recipes
from src.utils.text import recipes_to_documents
from src.rag.build_index import load_or_build_vectorstore
from src.db.schema import init_db
from src.ui.sidebar import render_sidebar
from src.ui.tab_recipe import render_tab_recipe
from src.ui.tab_profile import render_tab_profile
from src.ui.tab_log import render_tab_log
from src.ui.tab_weight import render_tab_weight
from src.ui.tab_planner import render_tab_planner


def ensure_openai_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        st.error(
            "OPENAI_API_KEY が未設定です。"
            " 環境変数に設定するか、プロジェクト直下の .env に設定してください。"
        )
        st.stop()


def init_session_state() -> None:
    defaults = {"question": "", "answer": None, "sources": []}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main() -> None:
    load_dotenv()
    st.set_page_config(
        page_title="ダイエットレシピ管理",
        layout="wide",
        page_icon="🥗",
    )
    st.title("🥗 ダイエットレシピ管理アプリ（管理栄養士監修）")

    ensure_openai_api_key()
    init_session_state()

    settings = get_settings()

    # SQLite DB の初期化（テーブルが無ければ作成）
    init_db(settings.sqlite_db_path)

    # サンプルデータ → Document 化 → VectorDB ロード（なければ構築）
    recipes = get_sample_recipes()
    docs = recipes_to_documents(recipes)
    vectorstore = load_or_build_vectorstore(docs, settings)

    # サイドバー（カロリー進捗 + RAG 設定）
    ui_state = render_sidebar(settings)

    # タブ構成
    tab_recipe, tab_profile, tab_log, tab_weight, tab_planner = st.tabs([
        "🔍 レシピ検索",
        "👤 プロフィール",
        "📋 食事ログ",
        "⚖️ 体重ログ",
        "📅 献立プランナー",
    ])

    with tab_recipe:
        render_tab_recipe(vectorstore, settings, ui_state)

    with tab_profile:
        render_tab_profile(settings)

    with tab_log:
        render_tab_log(settings)

    with tab_weight:
        render_tab_weight(settings)

    with tab_planner:
        render_tab_planner(settings)


if __name__ == "__main__":
    main()
