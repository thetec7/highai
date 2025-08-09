import streamlit as st

st.set_page_config(
    page_title="HighAI",
    page_icon="🎓",
    layout="centered"
)

st.markdown("<h1 style='text-align: center; color: #2C3E50; font-size: 5em; display: block; margin: 0 auto;'>HighAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.4em; color: #555; display: block; margin: 0 auto;'>무엇을 도와드릴까요?</p>", unsafe_allow_html=True)

if st.button("진로 직업 추천 받기", use_container_width=True):
    st.switch_page("pages/1_진로 추천 받기.py")
if st.button("심화 탐구 주제 찾기", use_container_width=True):
    st.switch_page("pages/2_탐구 주제 찾기.py")
if st.button("교과 전형 대학 찾기", use_container_width=True):
    st.switch_page("pages/3_교과 전형 대학 찾기.py")
if st.button("종합 전형 대학 찾기", use_container_width=True):
    st.switch_page("pages/4_종합 전형 대학 찾기.py")
if st.button("정시 전형 대학 찾기", use_container_width=True):
    st.switch_page("pages/5_정시 전형 대학 찾기.py")
if st.button("특별 전형 대학 찾기", use_container_width=True):
    st.switch_page("pages/6_특별 전형 대학 찾기.py")
        

st.markdown("""
<div style='text-align: center; margin-top: 50px;'>
    <p style='color:#696969; f`ont-size:14px;'>
        Developed by <strong>IYT</strong><br>
        Contact: <a href="mailto:488pista@daum.net" style="color:#696969; text-decoration:none;">488pista@daum.net</a>
    </p>
</div>
""", unsafe_allow_html=True)