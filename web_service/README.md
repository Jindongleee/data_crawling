# HTML to PDF Converter API

HTML 파일의 각 `<section>`을 개별 PDF로 변환하고, 모든 PDF를 하나로 병합하는 웹 서비스입니다.

## 설치 방법

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. Playwright 브라우저 설치:
```bash
playwright install chromium
```

## 실행 방법

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 `http://localhost:8000`에서 접근 가능합니다.

## API 엔드포인트

### 1. 루트 (`GET /`)
API 정보를 반환합니다.

### 2. 헬스 체크 (`GET /health`)
서버 상태를 확인합니다.

### 3. PDF 변환 (`POST /convert`)
HTML 파일을 업로드하여 PDF로 변환합니다.

**요청:**
- Method: POST
- Content-Type: multipart/form-data
- Body: HTML 파일 (file)

**응답:**
- Content-Type: application/pdf
- 파일 다운로드

**예시 (curl):**
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@your_file.html" \
  -o output.pdf
```

**예시 (Python):**
```python
import requests

with open('your_file.html', 'rb') as f:
    response = requests.post('http://localhost:8000/convert', files={'file': f})
    with open('output.pdf', 'wb') as pdf_file:
        pdf_file.write(response.content)
```

## 기능

- HTML 파일의 각 `<section>` 태그를 개별 PDF로 변환
- 모든 PDF를 하나의 PDF로 병합
- 원본 HTML의 `<head>` 스타일과 구조 유지
- `id="slides-wrapper"` 구조 유지
- 자동 이미지 로딩 대기
- 동시 요청 처리 (고유 ID 사용)

## 주의사항

- HTML 파일은 `<section>` 태그를 포함해야 합니다
- 외부 리소스(이미지, 폰트 등)는 인터넷 연결이 필요합니다
- 임시 파일은 `temp/` 디렉토리에 저장되며, 자동으로 정리되지 않을 수 있습니다

