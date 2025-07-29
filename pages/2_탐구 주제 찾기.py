import streamlit as st
import re
from openai import OpenAI

API_KEY = st.secrets["openai_api_key"]

with st.sidebar:
    st.subheader("HighAI")

st.set_page_config(
    page_title="HighAI",
    page_icon="🎓",
    layout="centered"
)

def askGpt(prompt, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def parse_gpt_response(response):
    pattern = r"\d+\.\s\*\*(.+?)\*\*\n\s*-\s*핵심 개념:\s*(.+?)\n\s*-\s*탐구 방법:\s*(.+?)(?=\n\d+\.|\Z)"
    matches = re.findall(pattern, response, re.DOTALL)
    return matches

def main():
    st.set_page_config(page_title="탐구 주제 찾기")
    st.title("💬 탐구 주제 찾기")
    st.caption("✅ 관심 있는 교과목과 주제, 본인의 학년, 선호하는 탐구 방식을 모두 입력하고 '탐구 주제 검색' 버튼을 눌러주세요.")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("관심 있는 교과목", placeholder="예: 생명과학 / 수학 / 지구과학")
        topic = st.text_input("관심 있는 주제(단원)", placeholder="예: 유전 / 미분 / 대기오염")
    with col2:
        grade = st.selectbox("학년", ["1", "2", "3"])
        method = st.selectbox("선호하는 탐구 방법", ["실험", "문헌 조사", "비교 연구", "혼합형"])    

    if st.button("🔍 탐구 주제 검색"):
        if not subject or not topic:
            st.warning("❗ 교과목과 주제를 모두 입력해 주세요.")
            return

        with st.spinner("탐구 주제를 추천하고 있어요..."):
            prompt = f"""
당신은 진로진학 전문 고등학교 교사입니다. 학생이 입력한 교과목과 주제에 기반하여, **대학 전공 수준의 심화 탐구 주제 10가지를 구체적으로 제시해주세요.**

각 주제는 다음의 3가지 구성요소를 포함해야 합니다:

1. **주제명** (문장형 제목)
2. **핵심 개념**: 해당 주제와 관련된 교과 개념 및 전공 개념
3. **탐구 방법**: 실험, 조사, 분석 등 실제 수행 가능한 방식

**학생 정보:**
- 학년: {grade}학년
- 좋아하는 교과목: {subject}
- 좋아하는 주제(단원): {topic}
- 선호하는 탐구 방법: {method}

**답변 형식 예시:**
1. **[주제명]**
   - 핵심 개념: ...
   - 탐구 방법: ...

※ 현실적으로 수행 가능한 고등학생 수준의 탐구를 기반으로, 교육과정 및 대입 전형에서 활용 가능한 방식으로 제안해주세요.
"""

            gpt_response = askGpt(prompt, API_KEY)
            parsed = parse_gpt_response(gpt_response)

            if parsed:
                st.markdown("---")

                for idx, (title, concept, method) in enumerate(parsed, 1):
                    with st.expander(f"📃` ` {idx}. {title.strip()}"):
                        st.markdown(f"**📌 핵심 개념:** {concept.strip()}")
                        st.markdown(f"**🔬 탐구 방법:** {method.strip()}")
            else:
                st.error("입력을 바꿔 다시 시도해 주세요.")

if __name__ == '__main__':
    main()