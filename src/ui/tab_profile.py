import streamlit as st
from src.config import Settings
from src.db.user_profile import upsert_profile, get_profile
from src.nutrition.tdee import calc_tdee, ACTIVITY_LABELS_JA


def render_tab_profile(settings: Settings) -> None:
    st.header("👤 プロフィール設定")
    st.caption("入力した情報から1日の目標摂取カロリーとPFC目標を自動計算します。")

    profile = get_profile(settings.sqlite_db_path)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(
                "年齢", min_value=15, max_value=90, value=int(profile["age"]) if profile else 30, step=1
            )
            height_cm = st.number_input(
                "身長 (cm)", min_value=140.0, max_value=220.0,
                value=float(profile["height_cm"]) if profile else 170.0, step=0.5
            )
            weight_kg = st.number_input(
                "現在の体重 (kg)", min_value=30.0, max_value=200.0,
                value=float(profile["weight_kg"]) if profile else 70.0, step=0.1
            )
        with col2:
            sex = st.selectbox(
                "性別",
                options=["male", "female"],
                format_func=lambda x: "男性" if x == "male" else "女性",
                index=0 if (not profile or profile["sex"] == "male") else 1,
            )
            goal_weight_kg = st.number_input(
                "目標体重 (kg)", min_value=30.0, max_value=200.0,
                value=float(profile["goal_weight_kg"]) if profile else 65.0, step=0.1
            )
            activity_level = st.selectbox(
                "活動量",
                options=list(ACTIVITY_LABELS_JA.keys()),
                format_func=lambda x: ACTIVITY_LABELS_JA[x],
                index=list(ACTIVITY_LABELS_JA.keys()).index(profile["activity_level"])
                if profile else 1,
            )

        calorie_deficit = st.slider(
            "1日のカロリー赤字量",
            min_value=200, max_value=500, step=50,
            value=int(profile["calorie_deficit"]) if profile else 350,
            help="300〜500kcalが安全な範囲。大きいほど早く痩せるが筋肉も落ちやすい。",
        )
        submitted = st.form_submit_button("保存して計算する", type="primary")

    if submitted:
        upsert_profile(settings.sqlite_db_path, {
            "age": age, "sex": sex,
            "height_cm": height_cm, "weight_kg": weight_kg,
            "goal_weight_kg": goal_weight_kg,
            "activity_level": activity_level,
            "calorie_deficit": calorie_deficit,
        })
        st.success("プロフィールを保存しました")
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

        st.divider()
        st.subheader("📊 あなたの栄養目標")

        col1, col2, col3 = st.columns(3)
        col1.metric("基礎代謝（BMR）", f"{result.bmr_kcal:.0f} kcal")
        col2.metric("維持カロリー（TDEE）", f"{result.tdee_kcal:.0f} kcal")
        col3.metric("1日の目標カロリー", f"{result.target_kcal:.0f} kcal",
                    delta=f"-{result.deficit_kcal} kcal/日")

        st.divider()
        st.subheader("🥩 PFC目標（1日あたり）")
        col1, col2, col3 = st.columns(3)
        col1.metric("たんぱく質", f"{result.protein_target_g} g",
                    help="体重×1.6g。筋肉量を維持しながらダイエットするための目安量。")
        col2.metric("脂質", f"{result.fat_target_g} g",
                    help="目標カロリーの25%。ホルモンバランス維持に必要な最低限の脂質。")
        col3.metric("炭水化物", f"{result.carbs_target_g} g",
                    help="残りのカロリーを炭水化物で補う。")

        diff_kg = profile["weight_kg"] - profile["goal_weight_kg"]
        if diff_kg > 0:
            weeks = round(diff_kg / (result.deficit_kcal * 7 / 7700), 1)
            st.info(
                f"目標達成まで約 **{weeks}週間**（現体重 {profile['weight_kg']}kg → "
                f"目標 {profile['goal_weight_kg']}kg、差分 {diff_kg:.1f}kg）"
            )
        else:
            st.success("目標体重に達しています！維持モードで継続しましょう。")
    else:
        st.info("上のフォームにプロフィールを入力して保存してください。")
