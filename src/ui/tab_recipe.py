import datetime
import streamlit as st
from src.config import Settings
from src.db.food_log import add_food_log_entry
from src.db.user_profile import get_profile
from src.nutrition.tdee import calc_tdee, format_profile_context
from src.rag.retriever import build_retriever
from src.rag.qa_chain import answer_question


def render_tab_recipe(vectorstore, settings: Settings, ui_state: dict) -> None:
    st.header("🔍 ダイエットレシピ検索")
    st.caption("管理栄養士視点でレシピを提案・解説します。")

    profile = get_profile(settings.sqlite_db_path)
    if profile:
        result = calc_tdee(
            weight_kg=profile["weight_kg"],
            height_cm=profile["height_cm"],
            age=profile["age"],
            sex=profile["sex"],
            activity_level=profile["activity_level"],
            deficit_kcal=profile["calorie_deficit"],
        )
        profile_context = format_profile_context(profile, result)
    else:
        profile_context = "プロフィール未設定"

    question = st.text_input(
        "例：低カロリーで高たんぱくの夕食は？",
        key="question",
        placeholder="ここに質問を入力してください",
    )

    if question:
        retriever = build_retriever(vectorstore, top_k=ui_state["top_k"])
        with st.spinner("検索＆回答中..."):
            retrieved_docs = retriever.invoke(question)
            result_qa = answer_question(
                question=question,
                retrieved_docs=retrieved_docs,
                settings=settings,
                temperature=ui_state["temperature"],
                profile_context=profile_context,
            )

        st.session_state.answer = result_qa["answer"]
        st.session_state.sources = result_qa["sources"]

    if st.session_state.get("answer"):
        st.subheader("✅ 管理栄養士アドバイス")
        st.write(st.session_state.answer)

        if st.session_state.get("sources"):
            st.subheader("📌 参照レシピ")
            for s in st.session_state.sources:
                with st.expander(s["title"]):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("カロリー", f"{s.get('calories_kcal', 0):.0f} kcal")
                    col2.metric("たんぱく質", f"{s.get('protein_g', 0):.0f} g")
                    col3.metric("脂質", f"{s.get('fat_g', 0):.0f} g")
                    col4.metric("炭水化物", f"{s.get('carbs_g', 0):.0f} g")

                    st.write(s["snippet"])

                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        meal_type = st.selectbox(
                            "食事の種類",
                            ["朝食", "昼食", "夕食", "間食"],
                            key=f"mtype_{s['title']}",
                        )
                    with col_b:
                        if st.button(f"食事ログに追加", key=f"log_{s['title']}"):
                            add_food_log_entry(settings.sqlite_db_path, {
                                "log_date": datetime.date.today().strftime("%Y-%m-%d"),
                                "meal_type": meal_type,
                                "recipe_id": s.get("recipe_id", ""),
                                "recipe_title": s["title"],
                                "calories_kcal": s.get("calories_kcal", 0),
                                "protein_g": s.get("protein_g", 0),
                                "fat_g": s.get("fat_g", 0),
                                "carbs_g": s.get("carbs_g", 0),
                            })
                            st.success(f"「{s['title']}」を{meal_type}に記録しました。")
