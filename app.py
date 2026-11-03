import streamlit as st

# アプリの基本設定
st.set_page_config(page_title="PL e1RM Calculator", page_icon="💪")
st.title("🏋️‍♂️ パワーリフティング e1RM 計算機")

# --- データ定義 (SQ/DL用とBP用) は rpe_chart.py ---
from rpe_chart import sq_dl_chart, bp_chart  # noqa: E402

# --- UI部分 ---

# 種目選択
exercise = st.radio("種目を選択", ["SQ/DL", "Bench Press"], horizontal=True)

# 数値入力
col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("挙上重量 (kg)", min_value=0.0, value=100.0, step=2.5)
with col2:
    reps = st.number_input("レップ数", min_value=1, max_value=15, value=5)

# RPEスライダー
rpe_options = sorted(sq_dl_chart.keys(), reverse=True)
rpe = st.select_slider("RPE (自覚的運動強度)", options=rpe_options, value=9.0)

# --- 計算ロジック ---
chart = bp_chart if exercise == "Bench Press" else sq_dl_chart
intensity = chart[rpe][reps - 1]
e1rm = weight / intensity

# --- 結果表示 ---
st.divider()
st.metric(label=f"{exercise} 推定1RM", value=f"{e1rm:.2f} kg")

# パーセンテージ表
with st.expander("詳細な重量配分を見る"):
    cols = st.columns(3)
    percents = [95, 92.5, 90, 87.5, 85, 82.5, 80, 75, 70]
    for i, p in enumerate(percents):
        with cols[i % 3]:
            st.write(f"{p}%: **{e1rm * (p/100):.1f} kg**")
