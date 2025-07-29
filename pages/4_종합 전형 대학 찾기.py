from openai import OpenAI
import streamlit as st
import pandas as pd
import numpy as np
import re

API_KEY = st.secrets["openai_api_key"]

with st.sidebar:
    st.subheader("HighAI")

st.set_page_config(page_title="종합 전형 대학 찾기")


st.title("💬 종합 전형 대학 찾기")
st.caption("**✅ 사용방법 :** 희망 전공과 본인의 내신 등급을 입력하고 '지원 대학 검색' 버튼을 눌러주세요.  \n **⚠️ 주의사항 :** 검색 결과는 참고용이며, 반드시 담임 선생님과 상담하여 신중하게 결정하세요.")

def askGpt(prompt, api_key):
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        gptResponse = response.choices[0].message.content
        return gptResponse
    except Exception as e:
        print(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
        st.error("AI 응답을 가져오는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
        return ""

def main():
    try:
        df = pd.read_csv("data/Early_Results2.csv")
        df['합격 등급'] = pd.to_numeric(df['합격 등급'], errors='coerce')
        df['년도'] = pd.to_numeric(df['년도'], errors='coerce')
        df.dropna(subset=['합격 등급', '년도'], inplace=True)
    except FileNotFoundError:
        st.error("`Early_Results2.csv` 파일을 찾을 수 없습니다. 파일이 올바른 위치에 있는지 확인해주세요.")
        return
    except KeyError as e:
        st.error(f"CSV 파일에 필수 컬럼이 없습니다: {e}. '대학명', '학과명', '전형명', '년도', '합격 등급' 컬럼이 정확히 있는지 확인해주세요.")
        return

    col1, col2 = st.columns(2)
    with col1:
        desired_major = st.text_input("희망 전공", placeholder="예: 컴퓨터공학 / 기계공학 / 역사")
    with col2:
        grade_input = st.text_input("내신 등급", placeholder="예: 1.5 (소수점 첫째 자리까지)")

    if st.button("지원 대학 검색"):
        if not desired_major or not grade_input:
            st.warning("희망 전공과 내신 등급을 모두 입력해야 합니다.")
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

            major_prompt = f"'{desired_major}' 전공과 가장 밀접하게 관련되거나 동일 계열의 학과명을 쉼표로 구분하여 5~7개 정도 나열해주세요. 불필요한 서론이나 설명 없이 학과명만 나열해주세요. 예시: 컴퓨터공학, 소프트웨어공학, 인공지능학과, 데이터사이언스학과"
            related_majors_str = askGpt(major_prompt, API_KEY)

            related_majors = []
            if related_majors_str:
                related_majors = [m.strip() for m in related_majors_str.split(',') if m.strip()]

            if desired_major not in related_majors:
                related_majors.insert(0, desired_major)

            seen = set()
            unique_related_majors = []
            for major in related_majors:
                if major not in seen:
                    unique_related_majors.append(major)
                    seen.add(major)

            major_pattern = '|'.join(re.escape(m) for m in unique_related_majors)

            df_2025 = df[df['년도'] == 2025].copy()
            filtered_by_major_2025_df = df_2025[df_2025['학과명'].str.contains(major_pattern, case=False, na=False)].copy()

            if filtered_by_major_2025_df.empty:
                st.warning(f"'{desired_major}'(와)과 유사한 전공으로 2025학년도 데이터가 검색되지 않았습니다.")
                return

            filtered_by_major_2025_df['match_priority'] = filtered_by_major_2025_df['학과명'].apply(lambda x: 0 if desired_major.lower() in x.lower() else 1)
            filtered_by_major_2025_df['등급_차이'] = abs(filtered_by_major_2025_df['합격 등급'] - user_grade)
            
            grade_filtered_2025_df = filtered_by_major_2025_df[filtered_by_major_2025_df['등급_차이'] <= 1.0].copy()

            if grade_filtered_2025_df.empty:
                st.info(f"입력하신 내신 등급 '{user_grade}'과 1.0등급 이내의 차이를 보이는 '{desired_major}' 계열의 2025학년도 대학을 찾지 못했습니다. 다른 등급이나 전공을 입력해보세요.")
                return

            recommended_universities_unique = grade_filtered_2025_df \
                .sort_values(by=['match_priority', '등급_차이', '합격 등급']) \
                .drop_duplicates(subset=['대학명', '학과명']) \
                .head(12)

            with result_container:
                if recommended_universities_unique.empty:
                    st.info("현재 입력된 정보로는 추천할 만한 대학을 찾을 수 없습니다. 희망 전공과 내신 등급을 다시 확인해주세요.")
                else:
                    for index, row_2025 in recommended_universities_unique.iterrows():
                        university_name = row_2025['대학명'].strip()
                        major_name = row_2025['학과명'].strip()
                        
                        historical_data_for_pair = df[
                            (df['대학명'] == university_name) & 
                            (df['학과명'] == major_name) &
                            (df['년도'].between(2023, 2025))
                        ].sort_values(by='년도', ascending=False)

                        st.markdown(f"#### 🎓 **{university_name} - {major_name}**")

                        if not historical_data_for_pair.empty:
                            details_str = ""
                            for year, year_group in historical_data_for_pair.groupby('년도'):
                                details_str += f"###### 🗓️ **{int(year)}학년도 입시 결과**\n"
                                for _, hist_row in year_group.iterrows():
                                    details_str += f"- **전형명:** {hist_row['전형명']},    **70% 등급:** {hist_row['합격 등급']:.2f} 등급\n"
                            st.markdown(details_str) 
                        else:
                            st.markdown(f"  - 해당 학과에 대한 2023-2025학년도 입시 데이터가 없습니다.")
                    st.markdown("<p style='color:#696969 ; font-size:14px;'>" \
                    "학생부 종합 전형은 내신 성적 뿐만 아니라 교과 외 활동(비교과 영역), 면접 등 학생부를 종합적으로 평가합니다. 최적의 지원 전략 수립을 위해 담임 선생님과의 심층 상담을 통해 최종 결정을 신중하게 내리시기를 권장합니다."
                    "</p>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()