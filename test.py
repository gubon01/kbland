import streamlit as st
from PublicDataReader import Kbland
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import mplcursors
import datetime


# 실행하자마자 전체 데이터 수집

api = Kbland()

매매_params = {
    "월간주간구분코드": "02",
    "매물종별구분": "01",
    "매매전세코드": "01",
}

전세_params = {
    "월간주간구분코드": "02",
    "매물종별구분": "01",
    "매매전세코드": "02",
}

매매_raw = api.get_price_index(**매매_params)
전세_raw = api.get_price_index(**전세_params)



# 사용자로부터 입력을 받았다고 가정

date_list = 매매_raw['날짜'].astype(str).to_list()
from_date = '2024-04-29'
to_date = '2024-05-27'


# 기간 조건으로 데이터 필터링

매매_fromTo = 매매_raw.query('날짜 >= @from_date and 날짜 <= @to_date')
전세_fromTo = 전세_raw.query('날짜 >= @from_date and 날짜 <= @to_date')


# 기준가격지수 대비 증감지수 계산

매매_fromTo = 매매_fromTo.sort_values(['지역명', '날짜'])
매매_fromTo['기준가격지수'] = 매매_fromTo.groupby('지역명')['가격지수'].transform('first')
매매_fromTo['매매증감지수'] = 매매_fromTo['가격지수'] - 매매_fromTo['기준가격지수']

전세_fromTo = 전세_fromTo.sort_values(['지역명', '날짜'])
전세_fromTo['기준가격지수'] = 전세_fromTo.groupby('지역명')['가격지수'].transform('first')
전세_fromTo['전세증감지수'] = 전세_fromTo['가격지수'] - 전세_fromTo['기준가격지수']



df = pd.merge(매매_fromTo, 전세_fromTo, how='inner', on=['지역명', '날짜'], suffixes=('', '_y'))
df = df[['월간주간구분', '매물종별구분', '지역코드', '지역명', '날짜', '매매증감지수', '전세증감지수']]

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False



# 매매증감지수와 전세증감지수의 최댓값과 최솟값 계산
x_max = df['매매증감지수'].max() + 0.1
x_min = df['매매증감지수'].min() - 0.1
y_max = df['전세증감지수'].max() + 0.1
y_min = df['전세증감지수'].min() - 0.1

# x축과 y축의 최대 절대값을 계산하여 범위 설정
x_lim = max(abs(x_min), abs(x_max))
y_lim = max(abs(y_min), abs(y_max))

# 시각화
fig, ax = plt.subplots(figsize=(10, 6))
plt.style.use('dark_background')

# 지역별로 색깔을 다르게 하여 표시
regions = df['지역명'].unique()
colors = ['r', 'b', 'g', 'c', 'm', 'y', 'w']  # 필요시 색상 추가

for i, region in enumerate(regions):
    region_df = df[df['지역명'] == region]
    x = region_df['매매증감지수']
    y = region_df['전세증감지수']
    
    # 보간을 사용하여 곡선 생성
    interp_x = np.linspace(x.min(), x.max(), num=500)
    interp_func = interp1d(x, y, kind='cubic')
    interp_y = interp_func(interp_x)
    
    ax.plot(interp_x, interp_y, linestyle='-', color=colors[i % len(colors)], alpha=0.7)
    scatter = ax.scatter(x, y, color=colors[i % len(colors)], s=50, edgecolors='w', linewidths=0.5, alpha=0.9, label=region)

# 축과 레이블 설정
ax.axhline(0, color='white', linewidth=0.5)
ax.axvline(0, color='white', linewidth=0.5)
ax.set_xlim(-x_lim, x_lim)
ax.set_ylim(-y_lim, y_lim)
ax.set_xlabel('매매증감지수', color='white')
ax.set_ylabel('전세증감지수', color='white')
ax.set_title('지역별 매매증감지수와 전세증감지수 변화', color='white')
ax.legend()
ax.grid(True, color='gray', linestyle='--', linewidth=0.5)

# mplcursors를 사용하여 마우스 오버 기능 추가
mplcursors.cursor(scatter, hover=True).connect(
    "add", lambda sel: sel.annotation.set_text(f'{regions[sel.index]}: 매매증감지수={sel.target[0]}, 전세증감지수={sel.target[1]}'))



# Streamlit 애플리케이션 제목 설정
st.title('지역별 매매증감지수와 전세증감지수 변화')

# 시작 날짜와 종료 날짜 선택 위젯
start_date = st.date_input("시작 날짜", datetime.date(2023, 1, 1))
end_date = st.date_input("종료 날짜", datetime.date(2023, 12, 31))

# 종료 날짜는 시작 날짜보다 빠를 수 없음
if start_date > end_date:
    st.error("종료 날짜는 시작 날짜 이후여야 합니다.")

# 단일 옵션 선택
options = ["서울시", "대구시", "부산시"]

# 다중 옵션 선택
multi_options = st.multiselect("지역명 선택", options)

# Streamlit을 사용하여 그래프 출력
st.pyplot(fig)
