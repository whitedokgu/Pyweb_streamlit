import streamlit as st

#웹 페이지의 정보를 쉽게 스크랩할 수 있도록 기능을 제공하는 라이브러리
from bs4 import BeautifulSoup

#HTTP 요청을 보낼 수 있도록 기능을 제공하는 라이브러리
import urllib.request as REQ

#데이터를 쉽게 다룰 수 있고, 분석을 용이하게 해주는 파이썬 라이브러리
import pandas as pd

#파이썬 기반 시각화 라이브러리
import matplotlib.pyplot as plt
import matplotlib
import plotly.express as px


#한글 폰트 설정
from matplotlib import rc

#한글 폰트 깨짐 방지
rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams["font.family"] ="Malgun Gothic"
matplotlib.rcParams["axes.unicode_minus"] =False

st.set_page_config(
    page_title="날씨 예보 | 기상청 ",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"    
)

st.title("날씨 예보 🌤️")

#출처: https://www.weather.go.kr/w/pop/rss-guide.do
#참고자료: https://www.weather.go.kr/w/resources/pdf/midtermforecast_rss.pdf
#만든날짜기준(2022-11-20) 예보 10일치
Url ="http://www.weather.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=109"
Response = REQ.urlopen( Url )

#응답받은 HTML 내용을 BeautifulSoup 클래스의 객체 형태로 생성/반환
B_soup = BeautifulSoup( Response, "html.parser") #html.parser , html5lib

#객체변환한 데이터를 Dlist에 추가하여 DataFrame생성
DList = []
for location in B_soup.select("location"):
    for data in location.select("data"):
        DList.append( {"도시":location.city.string,
                      "날짜":data.tmef.string,
                      "날씨":data.wf.string,
                      "최저":int(data.tmn.string),
                      "최고":int(data.tmx.string)}  )

Df = pd.DataFrame(DList)

#도시와 날짜를 인덱스로 설정.
Df.set_index(["도시", "날짜"], inplace=True)
pd.set_option("display.max_rows", None)

#일교차 컬럼을 추가,최고기온과 최저기온의 차이가 가장높은 도시,날짜,최저,최고,일교차.
Df["일교차"] = Df["최고"] - Df["최저"]
Df.sort_values("일교차", ascending=False).head(5)

Df.to_csv("./df.csv",sep=",")

# 해당이름의 csv파일을 읽어옴
r_csv = pd.read_csv("df.csv")
r_csv.to_excel("nalsee.xlsx")

#엑셀파일 변수에저장
data = pd.read_excel("nalsee.xlsx")

excel_file = "nalsee.xlsx"
sheet_name = "Sheet1"
df = pd.read_excel(excel_file,
                   sheet_name=sheet_name,
                   usecols='B:G'
                   )

citys = df['도시'].unique().tolist()

st.subheader('날씨 예보')
option = st.selectbox(
    '어떤 지역을 고르시겠습니까?',
    (citys))
	
st.write('선택된 지역: ', option)   

mask = df['도시'].isin([option])

df_grouped = df[mask].groupby(by=['날짜']).sum()[['최고','최저','일교차']]
df_grouped = df_grouped.reset_index()

chart_data  = px.line(df_grouped,
                   x="날짜",
                   y=['최저','최고','일교차'],
                   markers=True               
                   )


st.plotly_chart(chart_data)





