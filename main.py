import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import shutil
import os
import tempfile
import uuid
from PIL import Image

from dots_ocr.parser import DotsOCRParser
from dots_ocr.utils.consts import MIN_PIXELS, MAX_PIXELS

load_dotenv()

VALID_PROMPT_MODES = {"prompt_layout_all_en", "prompt_layout_only_en", "prompt_ocr"}

dots_parser = DotsOCRParser(
    ip=os.getenv("DOTSOCR_IP", "localhost"),
    port=int(os.getenv("DOTSOCR_PORT", 3003)),
    model_name=os.getenv("DOTSOCR_MODEL", "dotsocr-model"),
    min_pixels=MIN_PIXELS,
    max_pixels=MAX_PIXELS,
)

app = FastAPI(title="DotsOCR API", description="Parse PDF or image files into Markdown", version="1.0.0")


def create_temp_session_dir():
    session_id = uuid.uuid4().hex[:8]
    temp_dir = os.path.join(tempfile.gettempdir(), f"dots_ocr_{session_id}")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir, session_id


@app.get("/")
def read_root():
    return {"dots.ocr FastAPI Server": "hit /docs for endpoint reference"}


@app.post("/parse")
async def parse_file(
        file: UploadFile = File(..., description="Upload PDF or image files"),
        prompt_mode: str = Form("prompt_layout_all_en",
                                description="must be prompt_layout_all_en / prompt_layout_only_en / prompt_ocr"),

):
    if prompt_mode not in VALID_PROMPT_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid prompt_mode，must be {VALID_PROMPT_MODES}")

    """Receive PDF/images and return Markdown"""
    temp_dir, session_id = create_temp_session_dir()
    ext = os.path.splitext(file.filename)[1].lower()
    safe_filename = f"upload{ext}"
    file_path = os.path.join(temp_dir, safe_filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if ext == ".pdf":
            results = dots_parser.parse_pdf(
                input_path=file_path,
                filename=f"demo_{session_id}",
                prompt_mode=prompt_mode,
                save_dir=temp_dir
            )

            if not results:
                raise HTTPException(status_code=400, detail="PDF Parsing failed")

            all_md_content = []
            for result in results:
                if "md_content_path" in result and os.path.exists(result["md_content_path"]):
                    with open(result["md_content_path"], "r", encoding="utf-8") as f:
                        all_md_content.append(f.read())

            combined_md = "\n\n---\n\n".join(all_md_content)
            return combined_md

        elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
            image = Image.open(file_path)
            results = dots_parser.parse_image(
                input_path=image,
                filename=f"demo_{session_id}",
                prompt_mode=prompt_mode,
                save_dir=temp_dir
            )

            if not results:
                raise HTTPException(status_code=400, detail="Image parsing failed")

            result = results[0]
            md_content = None
            if "md_content_path" in result and os.path.exists(result["md_content_path"]):
                with open(result["md_content_path"], "r", encoding="utf-8") as f:
                    md_content = f.read()

            return md_content

        else:
            raise HTTPException(status_code=400, detail="Only supports .pdf .jpg .jpeg .png .gif .bmp files")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8491))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
