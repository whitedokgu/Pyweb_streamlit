import streamlit as st
#웹 페이지의 정보를 쉽게 스크랩할 수 있도록 기능을 제공하는 라이브러리
from bs4 import BeautifulSoup
#HTTP 요청을 보낼 수 있도록 기능을 제공하는 라이브러리
import urllib.request as REQ
import requests
#데이터를 쉽게 다룰 수 있고, 분석을 용이하게 해주는 파이썬 라이브러리
import pandas as pd
#파이썬 기반 시각화 라이브러리
import matplotlib.pyplot as plt
import matplotlib
# 번역 라이브러리
import googletrans
#한글 폰트 설정
from matplotlib import rc

API_KEY = "a88ba01f685860cc747349b67bc28056"

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

# style 적용
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</styles', unsafe_allow_html=True)

st.title("기상청 육상 중기예보 🌤️")

#출처: https://www.weather.go.kr/w/pop/rss-guide.do
#참고자료: https://www.weather.go.kr/w/resources/pdf/midtermforecast_rss.pdf
#만든날짜기준(2022-11-20) 예보 10일치
gUrl ="http://www.weather.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=109"
Response = REQ.urlopen( gUrl )

#응답받은 HTML 내용을 BeautifulSoup 클래스의 객체 형태로 생성/반환
B_soup = BeautifulSoup( Response, "html.parser") #html.parser , html5lib
dbUpdate = B_soup.find('item').find('title').text
st.caption(dbUpdate[12:])
#객체변환한 데이터를 Dlist에 추가하여 DataFrame생성
DList = []
for location in B_soup.select("location"):
    for data in location.select("data"):
        DList.append( {"도시":location.city.string,
                      "날짜":data.tmef.string,
                      "날씨":data.wf.string,
                      "최저온도":int(data.tmn.string),
                      "최고온도":int(data.tmx.string)}  )

Df = pd.DataFrame(DList)
#도시와 날짜를 인덱스로 설정.
Df.set_index(["도시", "날짜"], inplace=True)
pd.set_option("display.max_rows", None)

#일교차 컬럼을 추가,최고기온과 최저기온의 차이가 가장높은 도시,날짜,최저,최고,일교차.
Df["일교차"] = Df["최고온도"] - Df["최저온도"]
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

option = st.selectbox(
    '어떤 지역을 고르시겠습니까?',
    (citys))

translator = googletrans.Translator()
outStr = translator.translate(option, dest='en', src='auto')
st.write('선택된 지역: ', option)   

# 선택한 지역의 정보
nowNalsee = requests.get('https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query='+option+'날씨')
soup = BeautifulSoup(nowNalsee.text,'html.parser')

# 위치
address = soup.find('div',{'class': 'title_area _area_panel'}).find('h2', {'class': 'title'}).text
# 현재 날씨 
weather_data = soup.find('div',{'class': 'weather_info'})
# 현재 온도 
temperature = weather_data.find('div',{'class':'temperature_text'}).text.strip()[5:]
# 어제의 기온과 비교
tY = weather_data.find_all('p',{'class':'summary'})
for ty in tY:
    ty_list = ty.text.strip()  
    if "높아요" in ty_list:
        ct = ty_list[4:9]
    elif "낮아요" in ty_list:
        ct = "-" + ty_list[4:9]



# 체감온도와 습도
tS = weather_data.find_all('dl',{'class':'summary_list'})
for ts in tS:
    ts_list = ts.text.strip()
# 날씨 상태
weatherStatus = weather_data.find('span',{'class':'weather before_slash'}).text 

if option == "이천":
    outStr.text = "Icheon-si"
elif option == "김포":
    outStr.text = "Gimpo-si"
elif option == "강화":
    outStr.text = "Ganghwa-gun"
elif option == "시흥":
    outStr.text = "Siheung-si"
elif option == "의정부":
    outStr.text = "Uijeongbu-si"
elif option == "고양":
    outStr.text = "Goyang-si"
elif option == "양주":
    outStr.text = "Yangju-si"
elif option == "연천":
    outStr.text = "Yeoncheon-gun"
elif option == "포천":
    outStr.text = "Pocheon-si"
elif option == "구리":
    outStr.text = "Guri-si"
elif option == "양평":
    outStr.text = "Yeongdeungpo-gu"
elif option == "오산":
    outStr.text = "Osan"
elif option == "성남":
    outStr.text = "seongnam-si"

# 날씨 이미지 가져오기
base_url  = f"https://api.openweathermap.org/data/2.5/weather?q={outStr.text}&appid={API_KEY}&units=metric"
weather_data = requests.get(base_url).json()
try:     
    icon_id = weather_data['weather'][0]['icon']  
    icon = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
except KeyError:
    st.error("해당지역은 날씨 이미지가 지원되지 않습니다.")  
    icon = f"https://thenounproject.com/api/private/icons/4751555/edit/?backgroundShape=SQUARE&backgroundShapeColor=%23000000&backgroundShapeOpacity=0&exportSize=752&flipX=false&flipY=false&foregroundColor=%23FFFFFF&foregroundOpacity=1&imageFormat=png&rotation=0&token=gAAAAABjgchnJrW3bZMwlQDFMBV1ZvrfSbWUdwx327OtFSfgPN7veREt0MGcOyQFJ41A5jGFWelADPVO-3D1xlrX0W-5Qu9xyQ%3D%3D.png" 
# 공기 상태
air = soup.find('ul',{'class' : 'today_chart_list'})
infos = air.find_all('li',{'class' : 'item_today'})
air_list= []
for info in infos:
    air_list.append(info.text.strip())
# 오늘 강수 확률
rain = soup.find('div',{'class' : 'cell_weather'})
rain_rate = rain.find_all('span',{'class' : 'rainfall'})
rain_list = []
for rain in rain_rate:
    rain_list.append(rain.text.strip())

st.subheader(address)  


col1, col2, col3 = st.columns(3)
col1.metric(label='현재 기온 🌡️' ,value = temperature,delta=ct,help=ty_list[0:13])
col1.caption(ts_list[0:16])
col1.caption(ts_list[16:])
col2.metric(label='날씨 상태'  ,value= weatherStatus)
col2.image(icon)
col3.metric(label='오전 💧', value= rain_list[0] )
col3.metric(label='오후 💧', value= rain_list[1])

col1, col2, col3, col4= st.columns(4)
col1.metric(label='미세먼지 🤧',value =air_list[0][5:7])
col2.metric(label='초미세먼지 😷',value =air_list[1][6:8])
col3.metric(label='자외선 🔆',value =air_list[2][4:6])
col4.metric(label='일몰 🌇',value =air_list[3][3:])

mask = df['도시'].isin([option])
df_grouped = df[mask].groupby(by=['날짜']).sum()[['최고온도','최저온도','일교차']]
df_grouped = df_grouped.reset_index()

st.subheader('날씨 예보 그래')

st.sidebar.subheader('날씨 예보 차트 매개변수')
plot_data = st.sidebar.multiselect('데이터 선택', ['최저온도', '최고온도','일교차'], ['최저온도', '최고온도','일교차'])
plot_height = st.sidebar.slider('그래프의 높이 지정', 400, 800, 500)

st.line_chart(df_grouped,x='날짜',y=plot_data, height = plot_height)
