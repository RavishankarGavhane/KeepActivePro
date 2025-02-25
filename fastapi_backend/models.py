from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

# Define Base
Base = declarative_base()

# ContactSubmission Model
class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(15), nullable=False)
    message = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
