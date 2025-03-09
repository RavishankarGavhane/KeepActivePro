from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime



Base = declarative_base()



# Contact Form Table
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



# Visitor Count & Downloads Table
class VisitorMetrics(Base):
    __tablename__ = "visitor_metrics"
    id = Column(Integer, primary_key=True, index=True)
    visitor_count = Column(Integer, default=0)  # Tracks website visits
    download_count = Column(Integer, default=0)  # Tracks downloads
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f"Visitors: {self.visitor_count}, Downloads: {self.download_count}"

