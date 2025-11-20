from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import shutil
from pathlib import Path
from pdf_converter import convert_html_to_pdf

app = FastAPI(title="HTML to PDF Converter", version="1.0.0")

# CORS 설정 (프론트엔드에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 임시 파일 저장 디렉토리
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "HTML to PDF Converter API",
        "version": "1.0.0",
        "endpoints": {
            "POST /convert": "HTML 파일을 업로드하여 PDF로 변환",
            "GET /health": "서버 상태 확인"
        }
    }


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}


@app.post("/convert")
async def convert_html_to_pdf_endpoint(file: UploadFile = File(...)):
    """
    HTML 파일을 업로드받아 PDF로 변환하는 엔드포인트
    
    Args:
        file: 업로드된 HTML 파일
    
    Returns:
        생성된 PDF 파일 (다운로드)
    """
    # 파일 확장자 확인
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="HTML 파일만 업로드 가능합니다.")
    
    try:
        # 업로드된 파일 내용 읽기
        html_content = await file.read()
        html_content_str = html_content.decode('utf-8')
        
        # PDF 변환 (async 함수이므로 await 필요)
        pdf_path = await convert_html_to_pdf(html_content_str, TEMP_DIR)
        
        # PDF 파일명 생성
        original_filename = Path(file.filename).stem
        pdf_filename = f"{original_filename}_merged.pdf"
        
        # 임시 디렉토리에 최종 파일 복사 (다운로드용)
        final_pdf_path = os.path.join(TEMP_DIR, pdf_filename)
        shutil.copy2(pdf_path, final_pdf_path)
        
        # 파일 응답 반환
        return FileResponse(
            path=final_pdf_path,
            filename=pdf_filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 변환 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

