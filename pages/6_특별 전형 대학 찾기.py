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

st.header("💬 특별 전형 대학 찾기")
st.caption("**✅ 사용방법 :** 희망 전공, 본인의 내신 등급, 그리고 특별 전형 지원 자격을 입력하고 '지원 대학 검색' 버튼을 눌러주세요.  \n **⚠️ 주의사항 :** 검색 결과는 참고용이며, 반드시 담임 선생님과 상담하여 신중하게 결정하세요.")

def ask_gpt(prompt, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    gptResponse = response.choices[0].message.content
    return gptResponse

def main():
    df = pd.read_csv("data/Early_Results3.csv")
    df['합격 등급'] = pd.to_numeric(df['합격 등급'], errors='coerce')
    df.dropna(subset=['합격 등급'], inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        major_input = st.text_input("희망 전공", placeholder="예: 컴퓨터공학 / 생명과학 / 역사")
    with col2:
        grade_input = st.text_input("내신 등급", placeholder="예: 1.5 (소수점 첫째 자리까지)")
    
    option_input = st.selectbox(
        "특별 전형 지원 자격",
        options=['기초생활', '차상위', '한부모', '특성화고', '농어촌'],
        index=None,
        placeholder="지원 자격을 선택하세요."
    )

    if st.button("지원 대학 검색"):
        if not major_input or not grade_input or not option_input:
            st.error("희망 전공, 내신 등급, 특별 전형 지원 자격을 모두 입력해야 합니다.")
            return

        try:
            user_grade = float(grade_input)
            if not (1.0 <= user_grade <= 9.0):
                st.error("내신 등급은 1.0부터 9.0 사이의 값으로 입력해주세요.")
                return
        except ValueError:
            st.error("내신 등급을 올바른 숫자 형식(예: 1.5)으로 입력해주세요.")
            return

        with st.spinner("지원 가능 대학 정보를 검색하고 있습니다. 잠시만 기다려주세요..."):

            major_prompt = f"""
            당신은 한국 대학의 전공 및 학과 연계성 전문가입니다.
            '{major_input}' 전공과 관련된 학과를 다음 기준에 따라 폭넓지만, **학문적 연관성**을 최우선으로 고려하여 제시하세요.
            만약 사용자가 선호 교과목으로 '{major_input}'을(를) 선택했다면, 해당 교과목의 지식이 많이 활용되는 관련 학과도 함께 추천하세요.

            선정 기준:
            1. **동일 전공/다른 표현** — 명칭만 다르고 내용이 동일한 학과.
            2. **세부 전공/세부분야** — 해당 전공에서 파생된 세부 연구 분야.
            3. **상위 계열 전공** — 해당 전공을 포함하는 넓은 계열.
            4. **연구·교육 내용상 밀접한 전공** — 주요 교과목, 실험·연구 주제, 산업 응용 분야가 겹치는 전공.
            5. **융합·응용 전공** — 타 분야와 결합하여 새로운 학문 영역을 형성한 전공.
            6. **선호 교과목 연계** - 선호 교과목의 지식이 많이 활용되는 전공을 추가로 추천 (예: 물리 → 기계공학과, 전기전자공학과; 화학 → 신소재공학과, 약학과; 생명과학 → 의예과, 농학과).

            **최우선 조건:**
            **- 전공명에 키워드가 포함되어 있더라도, 학문적 연관성이 전혀 없는 학과(예: 물리 → 물리치료학과, 화학 → 문화학과)는 절대 포함하지 마세요.**
            **- 오직 학문적, 교육적 내용이 실제로 밀접하게 연관된 전공만을 엄선하여 제시하세요.**

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

            major_filter = df[
                (df['학과명'].str.contains(major_pattern, case=False, na=False)) &
                (df['지원자격'].str.contains(option_input, case=False, na=False))
            ].copy()

            if major_filter.empty:
                st.warning(f"'{major_input}'(와)과 유사한 전공 및 '{option_input}' 지원 자격으로 검색된 데이터가 없습니다.")
                return

            major_filter['match_priority'] = major_filter['학과명'].apply(lambda x: 0 if major_input.lower() in x.lower() else 1)
            major_filter['등급_차이'] = abs(major_filter['합격 등급'] - user_grade)

            grade_filter = major_filter[major_filter['등급_차이'] <= 0.8].copy()

            if grade_filter.empty:
                st.info(f"입력하신 내신 등급 '{user_grade}'과 0.8등급 이내의 차이를 보이는 '{major_input}' 계열의 대학을 찾지 못했습니다. 다른 등급이나 전공을 입력해보세요.")
                return
            
            final_results = []
            result_df = grade_filter \
                .sort_values(by=['match_priority', '등급_차이']) \
                .drop_duplicates(subset=['대학명', '학과명', '전형명']) \
                .head(15)
            
            for index, row in result_df.iterrows():
                final_results.append({
                    '대학명': row['대학명'],
                    '학과명': row['학과명'],
                    '전형유형': row['전형유형'],
                    '전형명': row['전형명'],
                    '70% 등급': f"{row['합격 등급']:.2f}"
                })
            
            final_df = pd.DataFrame(final_results)

            result_container = st.container(border=True)
            with result_container:
                st.markdown("<p style='color:#696969 ; font-size:14px;'>"
                            f"작성하신 <b>[{major_input}]</b> 관련 학과에는 "
                            + ", ".join(display_related)
                            + " 등이 있습니다. 특별 전형에는 교과 성적뿐만 아니라 비교과 활동 등 다양한 평가 요소가 반영할 수 있으며, 지원 자격이 되는지 꼭 확인해야 합니다. 반드시 대학별 모집요강을 면밀히 검토하고 선생님과의 심층 상담을 통하여 최적화된 지원 전략을 수립하는 것이 바람직합니다."
                            "</p>", unsafe_allow_html=True)

                st.markdown("##### 🔍 검색 결과")
                st.dataframe(final_df, hide_index=True, use_container_width=True)

if __name__ == '__main__':
    main()