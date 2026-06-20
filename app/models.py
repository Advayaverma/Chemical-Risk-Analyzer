import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class Chemical(Base):
    __tablename__ = "chemicals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    cas_number = Column(String, nullable=True)
    synonyms = Column(String, nullable=True)  # Comma-separated alternative names (e.g., "E211, E-211")
    category = Column(String, nullable=False)  # "Food", "Cosmetics", "General"
    regulatory_status = Column(String, nullable=False)  # "Prohibited", "Restricted", "Permitted"
    regulatory_body = Column(String, nullable=False)  # "FSSAI", "CDSCO", "CDSCO/FSSAI"
    risk_level = Column(String, nullable=False)  # "High", "Medium", "Low", "Safe"
    health_risks = Column(Text, nullable=True)  # Health effects description
    regulatory_limit = Column(String, nullable=True)  # Maximum safe limit details
    description = Column(Text, nullable=True)  # Explanatory description
    source_url = Column(String, nullable=True)  # Official PDF or reference link

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    brand = Column(String, index=True, nullable=True)
    category = Column(String, nullable=False)  # "Food", "Cosmetics", "Personal Care", "Household", "Other"
    ingredients_text = Column(Text, nullable=False)  # Raw ingredients list text
    risk_score = Column(Integer, default=100)  # Dynamic or saved overall risk score
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
