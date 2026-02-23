import datetime
import streamlit as st
from src.config import Settings
from src.db.food_log import add_food_log_entry, get_daily_log, get_daily_totals, delete_food_log_entry
from src.db.user_profile import get_profile
from src.nutrition.tdee import calc_tdee
from src.sample_data import get_sample_recipes

MEAL_TYPES = ["朝食", "昼食", "夕食", "間食"]


def render_tab_log(settings: Settings) -> None:
    st.header("📋 食事ログ")

    date = st.date_input("記録する日付", value=datetime.date.today())
    date_str = date.strftime("%Y-%m-%d")

    recipes = get_sample_recipes()
    recipe_map = {r["title"]: r for r in recipes}
    recipe_titles = ["（自由入力）"] + [r["title"] for r in recipes]

    st.subheader("食事を追加する")
    with st.form("food_log_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            meal_type = st.selectbox("食事の種類", MEAL_TYPES)
        with col2:
            selected_title = st.selectbox("レシピを選択（または自由入力）", recipe_titles)

        if selected_title != "（自由入力）":
            r = recipe_map[selected_title]
            recipe_title = selected_title
            default_cal = float(r.get("calories_kcal", 0))
            default_prot = float(r.get("protein_g", 0))
            default_fat = float(r.get("fat_g", 0))
            default_carbs = float(r.get("carbs_g", 0))
            default_id = r["id"]
        else:
            recipe_title_input = st.text_input("料理名", placeholder="例：外食のランチなど")
            recipe_title = recipe_title_input
            default_cal = 0.0
            default_prot = 0.0
            default_fat = 0.0
            default_carbs = 0.0
            default_id = None

        col3, col4, col5, col6 = st.columns(4)
        with col3:
            calories = st.number_input("カロリー (kcal)", min_value=0.0, value=default_cal, step=1.0)
        with col4:
            protein = st.number_input("たんぱく質 (g)", min_value=0.0, value=default_prot, step=0.1)
        with col5:
            fat = st.number_input("脂質 (g)", min_value=0.0, value=default_fat, step=0.1)
        with col6:
            carbs = st.number_input("炭水化物 (g)", min_value=0.0, value=default_carbs, step=0.1)

        submitted = st.form_submit_button("記録する", type="primary")

    if submitted:
        title = recipe_title if selected_title == "（自由入力）" else selected_title
        if not title:
            st.warning("料理名を入力してください。")
        else:
            add_food_log_entry(settings.sqlite_db_path, {
                "log_date": date_str,
                "meal_type": meal_type,
                "recipe_id": None if selected_title == "（自由入力）" else default_id,
                "recipe_title": title,
                "calories_kcal": calories,
                "protein_g": protein,
                "fat_g": fat,
                "carbs_g": carbs,
            })
            st.success(f"{meal_type}に「{title}」を記録しました。")
            st.rerun()

    st.divider()
    st.subheader(f"📅 {date_str} の食事記録")

    logs = get_daily_log(settings.sqlite_db_path, date_str)
    totals = get_daily_totals(settings.sqlite_db_path, date_str)

    profile = get_profile(settings.sqlite_db_path)
    target_kcal = None
    if profile:
        result = calc_tdee(
            weight_kg=profile["weight_kg"],
            height_cm=profile["height_cm"],
            age=profile["age"],
            sex=profile["sex"],
            activity_level=profile["activity_level"],
            deficit_kcal=profile["calorie_deficit"],
        )
        target_kcal = result.target_kcal

    if logs:
        for log in logs:
            with st.expander(f"[{log['meal_type']}] {log['recipe_title']}  —  {log['calories_kcal']:.0f}kcal"):
                col1, col2, col3 = st.columns(3)
                col1.metric("たんぱく質", f"{log['protein_g']:.1f}g")
                col2.metric("脂質", f"{log['fat_g']:.1f}g")
                col3.metric("炭水化物", f"{log['carbs_g']:.1f}g")
                if st.button("削除", key=f"del_{log['id']}"):
                    delete_food_log_entry(settings.sqlite_db_path, log["id"])
                    st.rerun()

        st.divider()
        st.subheader("本日の合計")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("カロリー", f"{totals['calories_kcal']:.0f} kcal",
                    delta=f"目標: {target_kcal:.0f}kcal" if target_kcal else None)
        col2.metric("たんぱく質", f"{totals['protein_g']:.1f} g")
        col3.metric("脂質", f"{totals['fat_g']:.1f} g")
        col4.metric("炭水化物", f"{totals['carbs_g']:.1f} g")

        if target_kcal:
            remaining = target_kcal - totals["calories_kcal"]
            progress = min(totals["calories_kcal"] / target_kcal, 1.0)
            st.progress(progress, text=f"残り {remaining:.0f} kcal / 目標 {target_kcal:.0f} kcal")
    else:
        st.info("この日の食事はまだ記録されていません。")
