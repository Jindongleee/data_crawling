import urllib.parse
import urllib.request
import pandas as pd
import requests

def main():
    key = 'e1T6q1NWu4cmSjE98s1SM6V551NLQvS2M2OBmxHO'

    base = 'https://bigdata.kepco.co.kr/openapi/v1/EVcharge.do'

    metro_list = ['11','21','22','23','24','25','26','31','32','33','34','35','36','37','38','39']

    arr_total = []

    for i in metro_list:
        dict = {} # 도시와, 도시의 충전량 개수를 담기 위한 딕셔너리
        params = {
            'metroCd': i,
            'apiKey': key,
            'returnType' : 'json',
        }

        response = requests.get(base, params=params)

        arr = response.json()['data']

        total = 0

        for i in range(len(arr)):
            total = total + arr[i]['rapidCnt'] + arr[i]['slowCnt']

        dict['metro'] = arr[i]['metro']
        dict['total'] = total

        arr_total.append(dict)

    df = pd.DataFrame(arr_total)
    df.to_csv('시도별 충전소 설치 현황.csv')

if __name__ == "__main__":
    main()