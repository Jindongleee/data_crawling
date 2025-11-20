from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pypdf import PdfWriter
import os
import re
import uuid
from pathlib import Path


async def convert_html_to_pdf(html_content: str, output_dir: str = None) -> str:
    """
    HTML 파일을 PDF로 변환하는 함수
    
    Args:
        html_content: HTML 파일 내용 (문자열)
        output_dir: 출력 디렉토리 (None이면 임시 디렉토리 사용)
    
    Returns:
        생성된 PDF 파일 경로
    """
    # 출력 디렉토리 설정
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(output_dir, exist_ok=True)
    
    # 고유 ID 생성 (동시 요청 처리)
    unique_id = str(uuid.uuid4())
    work_dir = os.path.join(output_dir, unique_id)
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        # HTML 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 원본 head 부분을 포맷팅 유지하며 추출
        head_match = re.search(r'<head[^>]*>.*?</head>', html_content, re.DOTALL | re.IGNORECASE)
        if head_match:
            head_content = head_match.group(0)
        else:
            head_tag = soup.find('head')
            head_content = str(head_tag) if head_tag else ''
        
        # 슬라이드 추출 (section 태그 기준)
        slides = soup.find_all('section')
        
        if not slides:
            raise ValueError("HTML에 <section> 태그가 없습니다.")
        
        # 원본 body 구조 확인
        body_tag = soup.find('body')
        body_classes = body_tag.get('class', []) if body_tag else []
        body_class_str = ' '.join(body_classes) if body_classes else ''
        
        # 원본 presentation-container 구조 확인
        presentation_container = soup.find('div', id='presentation-container')
        presentation_container_classes = presentation_container.get('class', []) if presentation_container else []
        presentation_container_class_str = ' '.join(presentation_container_classes) if presentation_container_classes else ''
        
        # 원본 slides-wrapper 구조 확인
        slides_wrapper = soup.find('div', id='slides-wrapper')
        slides_wrapper_classes = slides_wrapper.get('class', []) if slides_wrapper else []
        slides_wrapper_class_str = ' '.join(slides_wrapper_classes) if slides_wrapper_classes else 'w-full h-full relative'
        slides_wrapper_style = slides_wrapper.get('style', '') if slides_wrapper else ''
        
        # 임시 슬라이드 html 저장 경로 리스트
        slide_html_files = []
        
        for idx, slide in enumerate(slides):
            # section에 active 클래스 추가
            slide_classes = slide.get('class', [])
            if 'active' not in slide_classes:
                slide_classes.append('active')
            slide['class'] = slide_classes
            
            # 개별 슬라이드를 위한 CSS 오버라이드 추가
            slide_specific_css = """
    <style>
        /* 개별 슬라이드일 때 position: absolute가 레이아웃을 깨뜨리므로 relative로 변경 */
        .slide {
            position: relative !important;
            opacity: 1 !important;
            visibility: visible !important;
            width: 100% !important;
            height: 100% !important;
        }
        /* slides-wrapper도 relative로 확실히 설정 */
        #slides-wrapper {
            position: relative !important;
            width: 100% !important;
            height: 100% !important;
            overflow: hidden !important;
        }
        /* presentation-container가 화면 전체를 차지하도록 */
        #presentation-container {
            width: 100% !important;
            height: 100% !important;
            max-width: none !important;
            box-shadow: none !important;
            border-radius: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        /* body도 화면 전체를 차지하고 여백 제거 */
        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            height: 100% !important;
            overflow: hidden !important;
        }
        /* html도 화면 전체를 차지 */
        html {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            height: 100% !important;
        }
    </style>
    """
            
            # head에 슬라이드별 CSS 추가
            head_with_slide_css = head_content.replace('</head>', slide_specific_css + '</head>')
            
            # 원본 구조 유지: body > presentation-container > slides-wrapper > section
            slide_html = f"""<!DOCTYPE html>
<html lang="ko">
{head_with_slide_css}
<body class="{body_class_str}">
    <div id="presentation-container" class="{presentation_container_class_str}">
        <div id="slides-wrapper" class="{slides_wrapper_class_str}" style="{slides_wrapper_style}">
            {slide}
        </div>
    </div>
</body>
</html>"""
            
            temp_html_path = os.path.join(work_dir, f"slide_{idx+1}.html")
            with open(temp_html_path, 'w', encoding='utf-8') as tmp:
                tmp.write(slide_html)
            
            slide_html_files.append(temp_html_path)
        
        # Playwright를 이용한 PDF 생성 (Async API 사용)
        pdf_paths = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            for idx, html_path in enumerate(slide_html_files):
                file_url = f"file://{html_path}"
                
                await page.goto(file_url, wait_until='networkidle')
                
                # 모든 이미지와 외부 리소스가 완전히 로드될 때까지 대기
                await page.wait_for_load_state('networkidle')
                
                # 배경 이미지가 로드될 때까지 추가 대기
                await page.wait_for_timeout(3000)
                
                # 모든 이미지가 로드되었는지 확인
                images_loaded = await page.evaluate("""
                    () => {
                        return Promise.all(
                            Array.from(document.images).map(img => {
                                if (img.complete) return Promise.resolve();
                                return new Promise((resolve, reject) => {
                                    img.onload = resolve;
                                    img.onerror = resolve; // 에러가 나도 계속 진행
                                    setTimeout(resolve, 5000); // 최대 5초 대기
                                });
                            })
                        );
                    }
                """)
                
                # CSS 배경 이미지도 로드될 때까지 추가 대기
                await page.wait_for_timeout(2000)
                
                # 슬라이드 요소가 완전히 렌더링될 때까지 대기
                await page.wait_for_selector('.slide', state='visible', timeout=10000)
                
                # presentation-container의 실제 크기 측정
                container_size = await page.evaluate("""
                    () => {
                        const container = document.getElementById('presentation-container');
                        if (container) {
                            const rect = container.getBoundingClientRect();
                            return {
                                width: Math.ceil(rect.width),
                                height: Math.ceil(rect.height)
                            };
                        }
                        return { width: 1920, height: 1080 }; // 기본값
                    }
                """)
                
                # PDF 저장 (원본 HTML의 실제 렌더링 크기에 맞춤)
                pdf_path = os.path.join(work_dir, f"slide_{idx+1}.pdf")
                
                await page.pdf(
                    path=pdf_path,
                    width=f"{container_size['width']}px",
                    height=f"{container_size['height']}px",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
                )
                
                # PDF 파일이 제대로 생성되었는지 확인
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    pdf_paths.append(pdf_path)
                else:
                    raise ValueError(f"PDF 파일 생성 실패: slide_{idx+1}.pdf")
            
            await browser.close()
        
        # 모든 PDF를 하나로 병합
        if not pdf_paths:
            raise ValueError("생성된 PDF 파일이 없습니다.")
        
        merger = PdfWriter()
        
        for pdf_path in pdf_paths:
            # PDF 파일이 존재하고 유효한지 확인
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                try:
                    merger.append(pdf_path)
                except Exception as e:
                    raise ValueError(f"PDF 병합 실패 ({os.path.basename(pdf_path)}): {e}")
            else:
                raise ValueError(f"PDF 파일이 존재하지 않거나 비어있음: {os.path.basename(pdf_path)}")
        
        # 최종 병합된 PDF 저장
        output_pdf = os.path.join(work_dir, "merged_slides.pdf")
        merger.write(output_pdf)
        merger.close()
        
        return output_pdf
        
    except Exception as e:
        # 에러 발생 시 임시 파일 정리
        import shutil
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir, ignore_errors=True)
        raise e

