import streamlit as st

with st.sidebar:
    st.subheader("HighAI")

st.set_page_config(
    page_title="HighAI",
    page_icon="🎓",
    layout="centered"
)

st.markdown("<h1 style='text-align: center; color: black; font-size: 5em; display: block; margin: 0 auto;'>HighAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.4em; color: black; display: block; margin: 0 auto;'>무엇을 도와드릴까요?</p>", unsafe_allow_html=True)

st.markdown("<br> <br>", unsafe_allow_html=True)

with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("진로 직업 추천 받기", use_container_width=True):
            st.switch_page("pages/1_진로 추천 받기.py")
    with col2:
        if st.button("심화 탐구 주제 찾기", use_container_width=True):
            st.switch_page("pages/2_탐구 주제 찾기.py")
    with col3:
        if st.button("교과 전형 대학 찾기", use_container_width=True):
            st.switch_page("pages/3_교과 전형 대학 찾기.py")
    with col4:
        if st.button("종합 전형 대학 찾기", use_container_width=True):
            st.switch_page("pages/4_종합 전형 대학 찾기.py")
    with col5:
        if st.button("정시 전형 대학 찾기", use_container_width=True):
            st.switch_page("pages/5_정시 전형 대학 찾기.py")

st.markdown("<br> <br>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 0.75em; color: #7F8C8D;'>© 2025 HighAI. All rights reserved.</p>", unsafe_allow_html=True)
