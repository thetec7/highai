from openai import OpenAI
import streamlit as st
import pandas as pd
import numpy as np
import re

API_KEY = st.secrets["openai_api_key"]

st.set_page_config(
    page_title="HighAI",
    page_icon="🎓",
    layout="centered"
)

st.header("💬 종합 전형 대학 찾기")
st.caption("**✅ 사용방법 :** 희망 전공과 본인의 내신 등급을 입력하고 '지원 대학 검색' 버튼을 눌러주세요.  \n **⚠️ 주의사항 :** 검색 결과는 참고용이며, 반드시 담임 선생님과 상담하여 신중하게 결정하세요.")

def ask_gpt(prompt, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    gptResponse = response.choices[0].message.content
    return gptResponse

def main():
    df = pd.read_csv("data/Early_Results2.csv")
    df['합격 등급'] = pd.to_numeric(df['합격 등급'], errors='coerce')
    df['년도'] = pd.to_numeric(df['년도'], errors='coerce')
    df.dropna(subset=['합격 등급', '년도'], inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        major_input = st.text_input("희망 전공", placeholder="예: 컴퓨터공학 / 생명과학 / 역사")
    with col2:
        grade_input = st.text_input("내신 등급", placeholder="예: 1.5 (소수점 첫째 자리까지)")

    if st.button("지원 대학 검색"):
        if not major_input or not grade_input:
            st.error("희망 전공과 내신 등급을 모두 입력해야 합니다.")
            return

        try:
            user_grade = float(grade_input)
            if not (1.0 <= user_grade <= 9.0):
                st.error("내신 등급은 1.0부터 9.0 사이의 값으로 입력해주세요.")
                return
        except ValueError:
            st.error("내신 등급을 올바른 숫자 형식(예: 1.5)으로 입력해주세요.")
            return

        result_container = st.container(border=True)

        with st.spinner("지원 가능 대학 정보를 검색하고 있습니다. 잠시만 기다려주세요..."):

            major_prompt = f"""
            당신은 한국 대학의 전공 및 학과 연계성 전문가입니다. 
            '{major_input}' 전공과 관련된 학과를 다음 기준으로 폭넓게 제시하세요.

            선정 기준:
            1. **동일 전공/다른 표현** — 명칭만 다르고 내용이 동일한 학과
            2. **세부 전공/세부분야** — 해당 전공에서 파생된 세부 연구 분야
            3. **상위 계열 전공** — 해당 전공을 포함하는 넓은 계열
            4. **연구·교육 내용상 밀접한 전공** — 주요 교과목, 실험·연구 주제, 산업 응용 분야가 겹치는 전공
            (예: 화학 → 신소재공학, 에너지공학, 화학공학, 환경공학 등)
            5. **융합·응용 전공** — 타 분야와 결합하여 새로운 학문 영역을 형성한 전공

            조건:
            - 반드시 한국 대학에 실존하는 학과명 사용
            - 10~15개 정도 제시
            - 불필요한 설명 없이, 쉼표로 구분
            - 명칭은 정확하게 표기

            출력 예시:
            화학과, 응용화학과, 화학공학과, 신소재공학과, 고분자공학과, 나노공학과, 에너지공학과, 환경공학과, 제약학과, 생명화학공학과, 재료공학과, 바이오화학과
            """
            related_majors_str = ask_gpt(major_prompt, API_KEY)

            related_majors = []
            if related_majors_str:
                related_majors = [m.strip() for m in related_majors_str.split(',') if m.strip()]

            if major_input not in related_majors:
                related_majors.insert(0, major_input)

            unique_related_majors = list(dict.fromkeys(related_majors))

            display_related = [m for m in unique_related_majors if m and m.lower() != major_input.lower()]
            display_related = display_related[:10]

            major_pattern = '|'.join(re.escape(m) for m in unique_related_majors)

            df_2025 = df[df['년도'] == 2025].copy()
            major_filter_2025 = df_2025[df_2025['학과명'].str.contains(major_pattern, case=False, na=False)].copy()

            if major_filter_2025.empty:
                st.warning(f"'{major_input}'(와)과 유사한 전공으로 2025학년도 데이터가 검색되지 않았습니다.")
                return

            major_filter_2025['match_priority'] = major_filter_2025['학과명'].apply(lambda x: 0 if major_input.lower() in x.lower() else 1)
            major_filter_2025['등급_차이'] = abs(major_filter_2025['합격 등급'] - user_grade)
            
            grade_filter_2025 = major_filter_2025[major_filter_2025['등급_차이'] <= 0.5].copy()

            if grade_filter_2025.empty:
                st.info(f"입력하신 내신 등급 '{user_grade}'과 0.5등급 이내의 차이를 보이는 '{major_input}' 계열의 2025학년도 대학을 찾지 못했습니다. 다른 등급이나 전공을 입력해보세요.")
                return

            result_2025 = grade_filter_2025 \
                .sort_values(by=['match_priority', '등급_차이']) \
                .drop_duplicates(subset=['대학명', '학과명']) \
                .head(12)

            with result_container:
                st.markdown("<p style='color:#696969 ; font-size:12px;'>"
                    f"작성하신 <b>[{major_input}]</b> 관련 학과에는 "
                    + ", ".join(display_related)
                    + " 등이 있습니다. 학생부 종합 전형은 교과 성적뿐만 아니라 비교과 활동 등 다양한 정성 평가 요소가 반영됩니다. 반드시 대학별 모집요강을 면밀히 검토하고 선생님과의 심층 상담을 통하여 최적화된 지원 전략을 수립하는 것이 바람직합니다."
                "</p>", unsafe_allow_html=True)

                for index, row_2025 in result_2025.iterrows():
                    university_name = row_2025['대학명'].strip()
                    major_name = row_2025['학과명'].strip()
                    
                    past_data = df[
                        (df['대학명'] == university_name) & 
                        (df['학과명'] == major_name) &
                        (df['년도'].between(2023, 2025))
                    ].sort_values(by='년도', ascending=False)

                    st.markdown(f"##### 🎓 **{university_name} - {major_name}**")

                    if not past_data.empty:
                        table_data = past_data[['년도', '전형명', '합격 등급']].rename(columns={
                            '합격 등급': '70% 등급'
                        })
                        table_data['년도'] = table_data['년도'].astype(str)
                        table_data['70% 등급'] = table_data['70% 등급'].map('{:.2f}'.format)
                        st.table(table_data.set_index('년도'))
                    else:
                        st.markdown(f"  - 해당 학과에 대한 2023-2025학년도 입시 데이터가 없습니다.")

if __name__ == '__main__':
    main()