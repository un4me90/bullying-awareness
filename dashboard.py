import streamlit as st

st.set_page_config(
    page_title="학교폭력 감수성 자가진단",
    page_icon="🏫",
    layout="wide",
)

st.logo("01_Ref/ROCKTHESCHOOL.jpeg", size="large")

pg = st.navigation(
    {
        "🏫 학생": [
            st.Page("pages/student.py", title="학교폭력 감수성 자가진단", icon="🏫", url_path="student"),
        ],
        "👨‍🏫 교사 / 관리자": [
            st.Page("pages/teacher.py",     title="담임교사",   icon="👨‍🏫", url_path="teacher"),
            st.Page("pages/grade3_head.py", title="3학년 부장", icon="📊", url_path="grade3_head"),
            st.Page("pages/grade4_head.py", title="4학년 부장", icon="📊", url_path="grade4_head"),
            st.Page("pages/grade5_head.py", title="5학년 부장", icon="📊", url_path="grade5_head"),
            st.Page("pages/grade6_head.py", title="6학년 부장", icon="📊", url_path="grade6_head"),
            st.Page("pages/admin.py",       title="업무담당자", icon="🗂",  url_path="admin"),
        ],
    }
)
pg.run()
