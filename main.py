import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, engine, get_db
from models import Base, Document
from schemas import DocumentResponse , QARequest
from upload_utils import save_upload_file
from nlp_engine import build_qa_pipeline
import os
import subprocess
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=[  "http://localhost:5173",  # Your React app's URL
        "http://127.0.0.1:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Base.metadata.drop_all(bind=engine)
# Create tables
Base.metadata.create_all(bind=engine)



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_text_from_pdf(file_path: str) -> str:
    try:
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    except Exception as e:
        raise ValueError(f"Failed to extract text: {str(e)}")





@app.post("/upload", response_model=DocumentResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = save_upload_file(file)
        extracted_text = extract_text_from_pdf(file_path)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save metadata to DB
    doc = Document(filename=file.filename, path=file_path , text=extracted_text)
    db.add(doc)
    db.commit()
    db.refresh(doc)


    return {
        "id": doc.id,
        "filename": doc.filename,
        "path": doc.path,
        "text": extracted_text,
        "upload_date": datetime.utcnow()   # Optional: return extracted text in response
    }





@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()


@app.get("/document/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc # Let FastAPI use ORM mode to return fields



@app.get("/text/{doc_id}")
def test_text(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"text": doc.text}





@app.post("/ask")
def ask_question(payload: QARequest, db: Session = Depends(get_db)):
    # Retrieve the document from the database
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Build the QA pipeline
        qa = build_qa_pipeline(doc.text)

        # Use the pipeline to get an answer to the question
        answer = qa.run(payload.question)  # This assumes query_ollama is in the pipeline

        return {"answer": answer}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
