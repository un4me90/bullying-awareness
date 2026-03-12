import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
from quiz_data import (
    load_data, CATEGORIES, require_auth,
    load_rounds, create_new_round, set_current_round,
    round_selector_sidebar, download_csv_button, reset_button,
)

require_auth()
st.header("🗂 업무담당자 — 학교 전체 현황")

round_id = round_selector_sidebar()

# ── 회차 관리 ─────────────────────────────────────────────
with st.expander("📋 검사 회차 관리", expanded=False):
    rounds_data = load_rounds()
    rounds      = rounds_data["rounds"]
    current_id  = rounds_data["current"]

    # 회차 목록 표시
    import pandas as pd
    rounds_df = pd.DataFrame(rounds).rename(columns={
        "id": "회차 ID", "name": "회차명", "date": "생성일"
    })
    rounds_df["현재 진행"] = rounds_df["회차 ID"].apply(
        lambda x: "✅ 진행 중" if x == current_id else ""
    )
    st.dataframe(rounds_df, use_container_width=True, hide_index=True)

    st.markdown("**새 회차 시작**")
    c1, c2 = st.columns([3, 1])
    with c1:
        new_name = st.text_input(
            "회차명",
            value=f"{len(rounds) + 1}회차",
            label_visibility="collapsed",
            placeholder="예: 2026년 2회차",
        )
    with c2:
        if st.button("➕ 새 회차 생성", use_container_width=True, type="primary"):
            if new_name.strip():
                create_new_round(new_name.strip())
                st.success(f"'{new_name}' 회차가 생성되어 진행 중으로 설정되었습니다.")
                st.rerun()

    if len(rounds) > 1:
        st.markdown("**진행 회차 변경**")
        round_options = {r["id"]: f"{r['name']} ({r['date']})" for r in rounds}
        sel = st.selectbox(
            "진행 회차 선택",
            options=list(round_options.keys()),
            format_func=lambda x: round_options[x],
            index=list(round_options.keys()).index(current_id),
            key="admin_current_round_sel",
        )
        if st.button("설정 저장", use_container_width=True):
            set_current_round(sel)
            st.success(f"진행 회차를 '{round_options[sel]}'로 변경했습니다.")
            st.rerun()

st.divider()

# ── 현황 대시보드 ─────────────────────────────────────────
df = load_data(round_id)
if df.empty:
    st.info("해당 회차에 저장된 진단 결과가 없습니다.")
    st.stop()

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("전체 참여 학생", f"{len(df)}명")
with m2:
    st.metric("학교 평균 점수", f"{df['total_score'].mean():.1f} / 100")
with m3:
    grades = df["grade"].nunique()
    st.metric("참여 학년 수", f"{grades}개 학년")

st.divider()

g_avg = df.groupby("grade")["total_score"].mean().reset_index()
g_avg["grade"] = g_avg["grade"].astype(int).astype(str) + "학년"
fig1 = px.bar(g_avg, x="grade", y="total_score",
              title="학년별 평균 총점", labels={"grade": "학년", "total_score": "평균 점수"})
st.plotly_chart(fig1, use_container_width=True)

valid_cats = [c for c in CATEGORIES if c in df.columns and df[c].notna().any()]
if valid_cats:
    avg = df[valid_cats].mean()
    fig2 = px.bar(
        x=avg.index, y=avg.values,
        title="학교 전체 범주별 평균 (20점 만점)",
        range_y=[0, 20], labels={"x": "", "y": "점수"},
        color=avg.index.tolist(),
        color_discrete_sequence=["#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#DDA0DD"],
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("점수 분포")
fig3 = px.histogram(df, x="total_score", nbins=20,
                    title="전체 학생 점수 분포", labels={"total_score": "총점"})
st.plotly_chart(fig3, use_container_width=True)

st.subheader("전체 학생 목록")
show_cols = ["student_name", "grade", "class", "total_score"] + valid_cats
st.dataframe(
    df[show_cols].rename(columns={
        "student_name": "번호", "grade": "학년",
        "class": "반", "total_score": "총점"
    }),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("데이터 관리")
c1, c2 = st.columns(2)
with c1:
    download_csv_button(df, "전체_진단결과.csv")
with c2:
    reset_button(round_id, label="전체")
