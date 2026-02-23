import streamlit as st
from src.config import Settings
from src.db.user_profile import get_profile
from src.db.food_log import get_daily_totals
from src.nutrition.tdee import calc_tdee
from src.nutrition.meal_planner import (
    suggest_meal_plan,
    find_recipes_by_ingredients,
    generate_shopping_list,
)
from src.sample_data import get_sample_recipes
import datetime


def render_tab_planner(settings: Settings) -> None:
    st.header("📅 献立プランナー")

    recipes = get_sample_recipes()

    # ===== Section 1: 献立提案 =====
    with st.expander("① 今日の献立を提案してもらう", expanded=True):
        st.caption("残りカロリーから朝・昼・夕・間食の献立を自動提案します。")

        profile = get_profile(settings.sqlite_db_path)
        today = datetime.date.today().strftime("%Y-%m-%d")
        totals = get_daily_totals(settings.sqlite_db_path, today)

        if profile:
            tdee_result = calc_tdee(
                weight_kg=profile["weight_kg"],
                height_cm=profile["height_cm"],
                age=profile["age"],
                sex=profile["sex"],
                activity_level=profile["activity_level"],
                deficit_kcal=profile["calorie_deficit"],
            )
            default_remaining = max(0.0, tdee_result.target_kcal - totals["calories_kcal"])
            st.info(
                f"今日の目標: **{tdee_result.target_kcal:.0f}kcal** / "
                f"摂取済み: **{totals['calories_kcal']:.0f}kcal** / "
                f"残り: **{default_remaining:.0f}kcal**"
            )
        else:
            default_remaining = 1600.0
            st.warning("プロフィールが未設定です。目標カロリーを手動で入力してください。")

        remaining_kcal = st.number_input(
            "残りカロリー (kcal)",
            min_value=100.0, max_value=3000.0,
            value=float(default_remaining),
            step=50.0,
        )

        meal_types_options = ["朝食", "昼食", "夕食", "間食"]
        selected_meals = st.multiselect(
            "提案する食事の種類",
            options=meal_types_options,
            default=meal_types_options,
        )

        if st.button("献立を提案する", type="primary", key="suggest_btn"):
            if not selected_meals:
                st.warning("食事の種類を1つ以上選択してください。")
            else:
                plan = suggest_meal_plan(recipes, remaining_kcal, selected_meals)
                total_planned = sum(
                    r.get("calories_kcal", 0) for r in plan.values() if r
                )

                st.success(f"合計カロリー: {total_planned:.0f} kcal / 残り {remaining_kcal:.0f} kcal")
                for meal_type, recipe in plan.items():
                    if recipe:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(
                                f"**{meal_type}**: {recipe['title']}"
                            )
                        with col2:
                            kcal = recipe.get("calories_kcal", 0)
                            p = recipe.get("protein_g", 0)
                            f = recipe.get("fat_g", 0)
                            c = recipe.get("carbs_g", 0)
                            st.caption(
                                f"{kcal:.0f}kcal｜P:{p:.0f}g F:{f:.0f}g C:{c:.0f}g"
                            )
                    else:
                        st.write(f"**{meal_type}**: 該当レシピなし")

    st.divider()

    # ===== Section 2: 食材から逆引き =====
    with st.expander("② 冷蔵庫の食材からレシピを探す"):
        st.caption("手持ちの食材を入力するとマッチするレシピを表示します。")
        ingredient_input = st.text_input(
            "食材を入力（カンマ区切り）",
            placeholder="例：鶏むね、豆腐、卵",
            key="ingredient_input",
        )

        if st.button("レシピを探す", key="search_ingredient_btn"):
            if not ingredient_input.strip():
                st.warning("食材を入力してください。")
            else:
                ingredients = [i.strip() for i in ingredient_input.replace("、", ",").split(",")]
                results = find_recipes_by_ingredients(recipes, ingredients)
                if results:
                    st.success(f"{len(results)}件のレシピが見つかりました。")
                    for count, recipe in results:
                        with st.expander(
                            f"[{recipe.get('meal_type', '')}] {recipe['title']}  "
                            f"— マッチ食材: {count}種"
                        ):
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("カロリー", f"{recipe.get('calories_kcal', 0):.0f} kcal")
                            col2.metric("たんぱく質", f"{recipe.get('protein_g', 0):.0f} g")
                            col3.metric("脂質", f"{recipe.get('fat_g', 0):.0f} g")
                            col4.metric("炭水化物", f"{recipe.get('carbs_g', 0):.0f} g")
                            st.write(recipe.get("text", "")[:300] + "...")
                else:
                    st.info("入力した食材に一致するレシピが見つかりませんでした。")

    st.divider()

    # ===== Section 3: 買い物リスト =====
    with st.expander("③ 買い物リストを作成する"):
        st.caption("作りたいレシピを選ぶと必要な食材リストを生成します。")
        all_titles = [r["title"] for r in recipes]
        selected_titles = st.multiselect(
            "レシピを選択してください",
            options=all_titles,
            key="shopping_recipes",
        )

        if st.button("買い物リストを作成", key="shopping_btn"):
            if not selected_titles:
                st.warning("レシピを1つ以上選択してください。")
            else:
                selected_recipes = [r for r in recipes if r["title"] in selected_titles]
                shopping = generate_shopping_list(selected_recipes)

                lines = []
                for category, items in shopping.items():
                    lines.append(f"## {category}")
                    for item in items:
                        lines.append(f"- [ ] {item}")
                    lines.append("")

                shopping_text = "\n".join(lines)
                st.markdown(shopping_text)
                st.code(shopping_text, language="markdown")
                st.caption("上のテキストをコピーしてメモアプリ等に貼り付けてお使いください。")
