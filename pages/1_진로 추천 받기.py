from openai import OpenAI
import streamlit as st

API_KEY = st.secrets["openai_api_key"]

with st.sidebar:
    st.subheader("HighAI")

st.set_page_config(
    page_title="HighAI",
    page_icon="🎓",
    layout="centered"
)

st.header("💬 진로 추천 받기")
st.caption("😀 **사용 방법:** 채팅창에 당신의 **관심사**, **성향**, **좋아하는 활동** 등을 자유롭게 입력해주세요.  \n 😍 **작성 예시:**  물리가 정말 좋아요 💡 MBTI는 ENFP예요!🌟 만드는 걸 좋아해요🔨")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 저는 고등학생 여러분의 진로 고민을 함께 나누고, 여러분의 꿈을 찾아가는 데 도움을 드리는 진로 상담 챗봇입니다."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("여기에 질문을 입력해주세요."): 

    client = OpenAI(api_key=API_KEY)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    system_prompt = """
    당신은 고등학생의 진로를 전문적으로 상담해주는 AI입니다. 사용자가 관심 있는 분야나 키워드를 제시하면, 이에 기반하여 다음 정보를 따뜻하고 친절한 말투로 구체적으로 단계별로 안내합니다:
    1.  **관련 직업 설명**: 학생이 관심을 보인 직업이나 분야에 대해 추가 질문을 이어가며 진로를 구체화하도록 돕습니다.
    2.  **관련 학과 및 대학, 계열 안내**: 대한민국 전체 대학을 탐색하여 직업과 관련된 학과, 계열을 10개 이상 설명합니다.

    **응답 지침**:
    * 학생 눈높이에 맞게 쉬운 표현을 사용하며, 가능한 한 실질적이고 구체적인 조언을 포함합니다.
    * 처음 직업, 계열을 추천할 때에는 최대한 다양한 직업(7개 이상)을 추천하고, 어떤 직업인지도 간단히 소개합니다.
    * 대학교를 추천할 때에는 수도권 대학, 지역 거점 국립대, 국립대 순서로 추천합니다.
    * 항상 따뜻하고 친절한 말투를 유지하며, 하위목록을 자제하고 이모지를 적극적으로 활용하여 가독성을 높입니다.
    * 단계를 구분하여 순차적으로 정보를 제공하고, 다음 단계로 나아갈 수 있도록 유도 질문을 합니다.
    """
    messages_with_system = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_with_system
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)