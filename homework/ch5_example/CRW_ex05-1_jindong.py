# architecture
# 네이버 open api에 요청 -> 검색 결과를 json 파일로 저장
import urllib.request
import urllib.parse
import urllib.error
import json
import os
import time

def main():
    client_id = 'Q_ZBQe8hknZaoRCQivJF'
    client_secret = 'rCffqkIgDq'

    encText = input("검색어: ").strip()
    encText = urllib.parse.quote(encText) # encoding

    base = 'https://openapi.naver.com/v1/search/blog?query='
    news_list = []

    for i in range(1, 1000, 100):
        url = base + encText +"&display=100&start=%d&sort=date" % i
            
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        response_body = response.read().decode('utf-8')

        naver_json = json.loads(response_body) # 문자열을 -> dict, list로 변환

        # for j in range(len(naver_json['items'])):
        #     news_list.append(naver_json['items'][j]) # 현재 리스트
        news_list.extend(naver_json['items']) # 리스트 원소를 알아서 붙임
        
    with open('naver_crawling_.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent = 4)    
        
if __name__ == "__main__":
    main()