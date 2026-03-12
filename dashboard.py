import streamlit as st

st.set_page_config(
    page_title="학교폭력 감수성 자가진단",
    page_icon="🏫",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page("pages/student.py", title="학교폭력 감수성 자가진단", icon="🏫", url_path="student"),
    ]
)
pg.run()
