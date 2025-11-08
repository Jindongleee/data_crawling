import requests
import time
import xml.etree.ElementTree as ET
import xml.dom.minidom


def main():
    key = '506d4e6e51736b64383150517a4264'
    base = 'http://openapi.seoul.go.kr:8088/'
    service = 'ChunmanFreeSuggestions'

    # 전체 개수 확인
    url = f'{base}{key}/xml/{service}/1/1'
    response = requests.get(url)
    root = ET.fromstring(response.content.decode('utf-8'))
    total_count = int(root.find('list_total_count').text)
    print(f"전체 데이터 개수: {total_count}")

    # 루트 노드 생성 (최종 XML 통합용)
    root_total = ET.Element(service)

    # 1000개씩 요청 반복
    for start in range(1, total_count + 1, 1000):
        end = min(start + 999, total_count) # 끝나는 지점
        url = f'{base}{key}/xml/{service}/{start}/{end}'
        response = requests.get(url)
        time.sleep(0.2)  # 서버 과부하 방지용 딜레이
        xml_str = response.content.decode('utf-8')
        
        # 현재 구간 XML 파싱
        try:
            chunk_root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            continue

        # <row> 요소만 추출해서 전체 XML에 추가
        for row in chunk_root.findall('row'):
            root_total.append(row)

        print(f"{start}~{end} 완료 ({len(root_total)}건 누적)")

    # 전체 XML 문자열로 변환
    xml_str = ET.tostring(root_total, encoding='utf-8')

    # 보기 좋게 정렬 (minidom으로 들여쓰기)
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="    ")

    with open('seoul_data.xml', 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
if __name__ == "__main__":
    main()