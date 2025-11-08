import urllib.request
import requests
import pandas as pd
import matplotlib.pyplot as plt
import platform

def main():
    year = int(input("사고 년도 조회: "))
    siDo = int(input("시 코드: "))
    guGun = int(input('군/구 코드:'))

    key = 'a8397ec56107bfaa5703edc7d1255a3146df523a8847655259f1bf75edf96fb3'

    base = "https://apis.data.go.kr/B552061/frequentzoneBicycle/getRestFrequentzoneBicycle"

    # params가 인코딩 해주기 떄문에 이중인코딩 문제 발생
    params = {
        "ServiceKey": key, 
        "searchYearCd": year,
        "siDo": siDo,      
        "guGun": guGun,     
        "type": "json",
        "numOfRows": '10',
        "pageNo": '1'
    }


    response = requests.get(base, params=params)

    df = pd.DataFrame(response.json()['items']['item'])
    df = df.loc[:,['sido_sgg_nm', 'occrrnc_cnt']]

    system_name = platform.system()

    if system_name == 'Darwin':  # macOS
        plt.rcParams['font.family'] = 'AppleGothic'
    elif system_name == 'Windows': # Window
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:  # Linux 등
        plt.rcParams['font.family'] = 'NanumGothic'

    # 마이너스(-) 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(10, 5))
    plt.bar(df['sido_sgg_nm'], df['occrrnc_cnt'], color = 'skyblue')
    plt.title('지역별 발생 건수', fontsize = 14)
    plt.xlabel('지역명', fontsize = 12)
    plt.ylabel('발생 건수', fontsize = 12)

    plt.xticks(rotation = 45)
    plt.grid(axis='y', linestyle = '--', alpha = 0.7)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()