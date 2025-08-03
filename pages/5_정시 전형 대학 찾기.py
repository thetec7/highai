from openai import OpenAI
import streamlit as st
import pandas as pd
import numpy as np
import re

API_KEY = st.secrets["openai_api_key"]

with st.sidebar:
    st.subheader("HighAI")

st.set_page_config(
    page_title="HighAI",
    page_icon="🎓",
    layout="centered"
)

st.title("💬 정시 전형 대학 찾기")
st.caption("**✅ 사용방법 :** 희망 전공과 모의고사 백분위 평균을 입력하고 '지원 대학 검색' 버튼을 눌러주세요.  \n**⚠️ 주의사항 :** 검색 결과는 참고용이며, 반드시 담임 선생님과 상담하여 신중하게 결정하세요.")

def ask_gpt(prompt, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    gptResponse = response.choices[0].message.content
    return gptResponse

def main():
    df = pd.read_csv("data/Regular_Results1.csv")
    df['합격 백분위'] = pd.to_numeric(df['합격 백분위'], errors='coerce')
    df['년도'] = pd.to_numeric(df['년도'], errors='coerce')
    df.dropna(subset=['합격 백분위', '년도'], inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        major_input = st.text_input("희망 전공", placeholder="예: 컴퓨터공학 / 기계공학 / 역사")
    with col2:
        grade_input = st.text_input("모의고사 백분위 평균", placeholder="예: 85.5 (소수점 첫째 자리까지)")

    if st.button("지원 대학 검색"):
        if not major_input or not grade_input:
            st.error("희망 전공과 모의고사 백분위 평균을 모두 입력해야 합니다.")
            return

        try:
            user_grade = float(grade_input)
            if not (0.0 <= user_grade <= 100.0):
                st.error("모의고사 백분위 평균은 0.0부터 100.0 사이의 값으로 입력해주세요.")
                return
        except ValueError:
            st.error("모의고사 백분위 평균을 올바른 숫자 형식(예: 85.5)으로 입력해주세요.")
            return

        result_container = st.container(border=True)

        with st.spinner("지원 가능 대학 정보를 검색하고 있습니다. 잠시만 기다려주세요..."):

            major_prompt = f"'{major_input}' 전공과 가장 밀접하게 관련되거나 동일 계열의 학과명을 쉼표로 구분하여 5~7개 정도 나열해주세요. 불필요한 서론이나 설명 없이 학과명만 나열해주세요. 예시: 컴퓨터공학, 소프트웨어공학, 인공지능학과, 데이터사이언스학과"
            related_majors_str = ask_gpt(major_prompt, API_KEY)

            related_majors = []
            if related_majors_str:
                related_majors = [m.strip() for m in related_majors_str.split(',') if m.strip()]

            if major_input not in related_majors:
                related_majors.insert(0, major_input)

            unique_related_majors = list(dict.fromkeys(related_majors))

            major_pattern = '|'.join(re.escape(m) for m in unique_related_majors)

            df_2024 = df[df['년도'] == 2024].copy()
            major_filter_2024 = df_2024[df_2024['학과명'].str.contains(major_pattern, case=False, na=False)].copy()

            if major_filter_2024.empty:
                st.warning(f"'{major_input}'(와)과 유사한 전공으로 2024학년도 데이터가 검색되지 않았습니다.")
                return

            major_filter_2024['match_priority'] = major_filter_2024['학과명'].apply(lambda x: 0 if major_input.lower() in x.lower() else 1)
            major_filter_2024['백분위_차이'] = abs(major_filter_2024['합격 백분위'] - user_grade)
            
            grade_filter_2024 = major_filter_2024[major_filter_2024['백분위_차이'] <= 5.0].copy()

            if grade_filter_2024.empty:
                st.info(f"입력하신 모의고사 백분위 평균 '{user_grade}'과 5.0 백분위 이내의 차이를 보이는 '{major_input}' 계열의 2024학년도 대학을 찾지 못했습니다. 다른 백분위나 전공을 입력해보세요.")
                return

            result_2024 = grade_filter_2024 \
                .sort_values(by=['match_priority', '백분위_차이']) \
                .drop_duplicates(subset=['대학명', '학과명']) \
                .head(10)

            with result_container:
                for index, row_2024 in result_2024.iterrows():
                    university_name = row_2024['대학명'].strip()
                    major_name = row_2024['학과명'].strip()
                    
                    past_data = df[
                        (df['대학명'] == university_name) & 
                        (df['학과명'] == major_name) &
                        (df['년도'].between(2023, 2024))
                    ].sort_values(by='년도', ascending=False)

                    st.markdown(f"#### 🎓 **{university_name} - {major_name}**")

                    if not past_data.empty:
                        table_data = past_data[['년도', '전형명', '합격 백분위']].rename(columns={
                            '합격 백분위': '70% 백분위'
                        })
                        table_data['년도'] = table_data['년도'].astype(str)
                        table_data['70% 백분위'] = table_data['70% 백분위'].map('{:.1f}'.format)
                        st.table(table_data.set_index('년도'))
                    else:
                        st.markdown(f"  - 해당 학과에 대한 2023-2024학년도 입시 데이터가 없습니다.")

                st.markdown("<p style='color:#696969 ; font-size:14px;'>" \
                            "정시 전형에서 수능 점수 외에 다양한 요소를 반영할 수 있으며, 대학 및 모집단위별로 반영 비율이 상이합니다. 최적의 지원 전략 수립을 위해 담임 선생님과의 심층 상담을 통해 최종 결정을 신중하게 내리시기를 권장합니다."
                            "</p>", unsafe_allow_html=True)
                
if __name__ == '__main__':
    main()