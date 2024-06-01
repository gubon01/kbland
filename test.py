import streamlit as st
import pandas as pd
import numpy as np

# Streamlit 애플리케이션 제목 설정
st.title('Simple Streamlit App')

# 사용자 입력을 받는 슬라이더
number = st.slider('Pick a number', 0, 100)

# 입력된 숫자를 사용하여 데이터 프레임 생성
df = pd.DataFrame({
    'Column 1': np.arange(number),
    'Column 2': np.random.randn(number)
})

# 데이터 프레임을 화면에 출력
st.write('Data Frame:')
st.write(df)

# 데이터 프레임을 라인 차트로 시각화
st.line_chart(df)
