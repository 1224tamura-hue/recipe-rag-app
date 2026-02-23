import datetime
import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from src.config import Settings
from src.db.weight_log import upsert_weight, get_weight_history
from src.db.user_profile import get_profile

matplotlib.use("Agg")


def _get_japanese_font():
    candidates = [
        "Hiragino Sans", "Hiragino Maru Gothic Pro",
        "Noto Sans CJK JP", "IPAexGothic", "IPAGothic",
    ]
    for name in candidates:
        try:
            fm.findfont(fm.FontProperties(family=name), fallback_to_default=False)
            return name
        except Exception:
            continue
    return None


def render_tab_weight(settings: Settings) -> None:
    st.header("⚖️ 体重ログ")

    with st.form("weight_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("日付", value=datetime.date.today())
        with col2:
            weight_kg = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0,
                                        value=60.0, step=0.1)
        with col3:
            body_fat = st.number_input("体脂肪率 (%) ※任意", min_value=0.0, max_value=60.0,
                                       value=0.0, step=0.1)

        submitted = st.form_submit_button("記録する", type="primary")

    if submitted:
        upsert_weight(
            settings.sqlite_db_path,
            date.strftime("%Y-%m-%d"),
            weight_kg,
            body_fat if body_fat > 0 else None,
        )
        st.success(f"{date} の体重 {weight_kg}kg を記録しました。")
        st.rerun()

    history = get_weight_history(settings.sqlite_db_path, days=60)
    profile = get_profile(settings.sqlite_db_path)

    if not history:
        st.info("体重データがまだありません。上のフォームから記録を始めましょう。")
        return

    df = pd.DataFrame(history)
    df["log_date"] = pd.to_datetime(df["log_date"])

    st.divider()
    st.subheader("📈 体重推移グラフ（過去60日）")

    font_name = _get_japanese_font()
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(df["log_date"], df["weight_kg"], marker="o", linewidth=2,
            color="#2196F3", label="体重 (kg)")

    if profile and profile.get("goal_weight_kg"):
        ax.axhline(y=profile["goal_weight_kg"], color="#F44336", linestyle="--",
                   linewidth=1.5, label=f"目標体重 {profile['goal_weight_kg']}kg")

    ax.set_xlabel("日付", fontfamily=font_name if font_name else None)
    ax.set_ylabel("体重 (kg)", fontfamily=font_name if font_name else None)
    ax.set_title("体重推移", fontfamily=font_name if font_name else None)
    ax.legend(prop={"family": font_name} if font_name else {})
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=30)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    if df["body_fat_pct"].notna().any():
        st.subheader("体脂肪率推移")
        bf_df = df.dropna(subset=["body_fat_pct"])
        fig2, ax2 = plt.subplots(figsize=(10, 3))
        ax2.plot(bf_df["log_date"], bf_df["body_fat_pct"], marker="o",
                 linewidth=2, color="#FF9800", label="体脂肪率 (%)")
        ax2.set_xlabel("日付", fontfamily=font_name if font_name else None)
        ax2.set_ylabel("体脂肪率 (%)", fontfamily=font_name if font_name else None)
        ax2.legend(prop={"family": font_name} if font_name else {})
        ax2.grid(True, alpha=0.3)
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    st.divider()
    st.subheader("📋 記録一覧（最新10件）")
    display_df = df[["log_date", "weight_kg", "body_fat_pct"]].copy()
    display_df.columns = ["日付", "体重(kg)", "体脂肪率(%)"]
    display_df["日付"] = display_df["日付"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df.tail(10).iloc[::-1], use_container_width=True, hide_index=True)
