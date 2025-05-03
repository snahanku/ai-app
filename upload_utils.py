import os
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_DIR = "static"

import fitz  

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()



def save_upload_file(upload_file: UploadFile) -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    ext = upload_file.filename.split('.')[-1]
    if ext.lower() != 'pdf':
        raise ValueError("Only PDF files are supported.")

    filename = f"{uuid4().hex}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return file_path
