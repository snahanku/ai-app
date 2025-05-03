
from pydantic import BaseModel
from datetime import datetime



class DocumentResponse(BaseModel):
    id: int
    filename: str
    path: str
    text: str
    upload_date: datetime

    class Config:
         from_attributes = True





class QARequest(BaseModel):
    document_id: int
    question: str

