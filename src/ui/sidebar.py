import datetime
import streamlit as st
from src.config import Settings
from src.db.food_log import get_daily_totals
from src.db.user_profile import get_profile
from src.nutrition.tdee import calc_tdee


def render_sidebar(settings: Settings) -> dict:
    st.sidebar.title("🥗 ダイエットレシピ")

    # --- 今日のカロリー進捗 ---
    today = datetime.date.today().strftime("%Y-%m-%d")
    profile = get_profile(settings.sqlite_db_path)
    totals = get_daily_totals(settings.sqlite_db_path, today)

    if profile:
        result = calc_tdee(
            weight_kg=profile["weight_kg"],
            height_cm=profile["height_cm"],
            age=profile["age"],
            sex=profile["sex"],
            activity_level=profile["activity_level"],
            deficit_kcal=profile["calorie_deficit"],
        )
        target = result.target_kcal
        consumed = totals["calories_kcal"]
        remaining = max(0.0, target - consumed)
        progress = min(consumed / target, 1.0) if target > 0 else 0.0

        st.sidebar.subheader("📊 今日の摂取カロリー")
        st.sidebar.progress(progress, text=f"{consumed:.0f} / {target:.0f} kcal")
        st.sidebar.caption(f"残り約 **{remaining:.0f} kcal**")

        st.sidebar.caption(
            f"P: {totals['protein_g']:.0f}g　"
            f"F: {totals['fat_g']:.0f}g　"
            f"C: {totals['carbs_g']:.0f}g"
        )
    else:
        st.sidebar.info("プロフィールタブで目標を設定してください。")

    st.sidebar.divider()

    # --- RAG 設定 ---
    st.sidebar.subheader("⚙️ 検索設定")
    top_k = st.sidebar.slider("検索件数（k）", 1, 8, settings.top_k_default)
    temperature = st.sidebar.slider(
        "回答の創造性", 0.0, 1.0, settings.temperature_default, step=0.05
    )

    if st.sidebar.button("🧹 クリア（質問・回答をリセット）"):
        st.session_state.question = ""
        st.session_state.answer = None
        st.session_state.sources = []
        st.rerun()

    return {"top_k": top_k, "temperature": temperature}
