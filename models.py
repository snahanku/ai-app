from sqlalchemy import Column, Integer, String, DateTime , Text
from datetime import datetime
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    path = Column(String)
    text = Column(Text , nullable=True)
