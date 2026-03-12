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

GRADE = 5

st.header(f"📊 {GRADE}학년 부장 — {GRADE}학년 현황")

round_id = round_selector_sidebar()

df = load_data(round_id)
if df.empty:
    st.info("해당 회차에 저장된 진단 결과가 없습니다.")
    st.stop()

gdf = df[df["grade"] == GRADE]
if gdf.empty:
    st.warning(f"{GRADE}학년 데이터가 없습니다.")
    st.stop()

st.metric(f"{GRADE}학년 평균 점수", f"{gdf['total_score'].mean():.1f} / 100")
st.metric("참여 학생 수", f"{len(gdf)}명")
st.divider()

c_avg = gdf.groupby("class")["total_score"].mean().reset_index()
c_avg["class"] = c_avg["class"].astype(int).astype(str) + "반"
fig1 = px.bar(c_avg, x="class", y="total_score",
              title=f"{GRADE}학년 학급별 평균 총점",
              labels={"class": "반", "total_score": "평균 점수"})
st.plotly_chart(fig1, use_container_width=True)

valid_cats = [c for c in CATEGORIES if c in gdf.columns and gdf[c].notna().any()]
if valid_cats:
    avg = gdf[valid_cats].mean()
    fig2 = px.bar(
        x=avg.index, y=avg.values,
        title=f"{GRADE}학년 범주별 평균 점수 (20점 만점)",
        range_y=[0, 20], labels={"x": "", "y": "점수"},
        color=avg.index.tolist(),
        color_discrete_sequence=["#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#DDA0DD"],
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader(f"{GRADE}학년 학생 목록")
show_cols = ["grade", "class", "student_name", "total_score"] + valid_cats
st.dataframe(
    gdf[show_cols].rename(columns={
        "student_name": "번호", "grade": "학년", "class": "반", "total_score": "총점"
    }),
    use_container_width=True, hide_index=True,
)

st.divider()
st.subheader("데이터 관리")
c1, c2 = st.columns(2)
with c1:
    download_csv_button(gdf, f"{GRADE}학년_진단결과.csv")
with c2:
    reset_button(round_id, grade=GRADE, label=f"{GRADE}학년")
