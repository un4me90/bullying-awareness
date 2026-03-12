import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
from quiz_data import (
    load_data, CATEGORIES, require_auth,
    round_selector_sidebar, download_csv_button, reset_button,
)

require_auth()
st.header("👨‍🏫 담임교사 — 학급 세부현황")

round_id = round_selector_sidebar()

df = load_data(round_id)
if df.empty:
    st.info("해당 회차에 저장된 진단 결과가 없습니다.")
    st.stop()

cats = CATEGORIES

col_f1, col_f2 = st.columns(2)
with col_f1:
    grades = sorted(df["grade"].dropna().unique())
    sel_grade = st.selectbox("학년", grades)
with col_f2:
    classes = sorted(df[df["grade"] == sel_grade]["class"].dropna().unique())
    sel_class = st.selectbox("반", classes)

cdf = df[(df["grade"] == sel_grade) & (df["class"] == sel_class)]

if cdf.empty:
    st.warning("해당 학급의 데이터가 없습니다.")
    st.stop()

st.subheader(f"{int(sel_grade)}학년 {int(sel_class)}반 학생 목록")
display_cols = ["student_name", "total_score"] + [c for c in cats if c in cdf.columns]
st.dataframe(
    cdf[display_cols].rename(columns={"student_name": "번호", "total_score": "총점"}),
    use_container_width=True,
    hide_index=True,
)

st.metric("학급 평균 점수", f"{cdf['total_score'].mean():.1f} / 100")

st.divider()
valid_cats = [c for c in cats if c in cdf.columns and cdf[c].notna().any()]
if valid_cats:
    avg = cdf[valid_cats].mean()
    fig = px.bar(
        x=avg.index, y=avg.values,
        title="범주별 평균 점수 (20점 만점)",
        range_y=[0, 20], labels={"x": "", "y": "점수"},
        color=avg.index.tolist(),
        color_discrete_sequence=["#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#DDA0DD"],
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("데이터 관리")
c1, c2 = st.columns(2)
with c1:
    filename = f"{int(sel_grade)}학년_{int(sel_class)}반_진단결과.csv"
    download_csv_button(cdf, filename)
with c2:
    label = f"{int(sel_grade)}학년 {int(sel_class)}반"
    reset_button(round_id, grade=int(sel_grade), cls=int(sel_class), label=label)
