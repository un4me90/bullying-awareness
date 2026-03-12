import sys, base64
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from quiz_data import (
    hide_sidebar, apply_css, IMAGE_DIR,
    show_quiz_page, show_result_page,
)

hide_sidebar()
apply_css()

GK = "student_grade_group"


def show_select():
    logo_b64 = base64.b64encode((IMAGE_DIR / "ROCKTHESCHOOL.jpeg").read_bytes()).decode()
    c_logo, c_title = st.columns([1, 3], vertical_alignment="center")
    with c_logo:
        st.markdown(f"""
        <div style='text-align:center'>
            <div style='font-weight:800;font-size:1.6em;margin-bottom:8px'>인천석암초등학교</div>
            <img src='data:image/jpeg;base64,{logo_b64}' width='160' style='display:block;margin:0 auto'>
        </div>""", unsafe_allow_html=True)
    with c_title:
        st.markdown("## 👋 안녕! 학교폭력에 대한 내 마음을 확인해 보자!")
        st.markdown("15개의 그림 문제를 보고 솔직하게 답해줘! 정답은 없어 😊")
    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        grade = st.selectbox("학년", [3, 4, 5, 6])
    with c2:
        cls = st.selectbox("반", list(range(1, 11)))
    with c3:
        num = st.selectbox("번호", list(range(1, 41)))
    st.divider()

    if st.button("시작하기! 🚀", use_container_width=True, type="primary"):
        gg = "34" if grade <= 4 else "56"
        prefix = f"quiz_{gg}"
        st.session_state[GK] = gg
        st.session_state[f"{prefix}_info"]    = {"name": str(num), "grade": grade, "class": cls}
        st.session_state[f"{prefix}_page"]    = "quiz"
        st.session_state[f"{prefix}_q"]       = 0
        st.session_state[f"{prefix}_answers"] = {}
        st.rerun()


if not st.session_state.get(GK):
    show_select()
else:
    gg     = st.session_state[GK]
    prefix = f"quiz_{gg}"
    page   = st.session_state.get(f"{prefix}_page", "select")

    if page == "quiz":
        show_quiz_page(prefix, gg)
    elif page == "result":
        show_result_page(prefix, gg)
    else:
        # 퀴즈 리셋 후 → 학년 선택 화면으로 복귀
        st.session_state.pop(GK, None)
        st.rerun()
