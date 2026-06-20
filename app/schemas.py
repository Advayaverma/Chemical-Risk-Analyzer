from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Chemical Schemas ---
class ChemicalBase(BaseModel):
    name: str
    cas_number: Optional[str] = None
    synonyms: Optional[str] = None
    category: str
    regulatory_status: str
    regulatory_body: str
    risk_level: str
    health_risks: Optional[str] = None
    regulatory_limit: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None

class ChemicalCreate(ChemicalBase):
    pass

class ChemicalResponse(ChemicalBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    category: str
    ingredients_text: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    risk_score: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- Analysis Schemas ---
class IngredientAnalysisDetail(BaseModel):
    ingredient_raw: str
    matched_chemical: ChemicalResponse
    match_type: str  # "exact", "synonym", "substring"

class AnalysisRequest(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: str  # "Food", "Cosmetics", "Personal Care", "Household", "Other"
    ingredients_text: str

class AnalysisResponse(BaseModel):
    product_name: Optional[str] = None
    brand: Optional[str] = None
    category: str
    risk_score: int
    grade: str  # "A", "B", "C", "D", "F"
    summary: str
    matched_ingredients: List[IngredientAnalysisDetail]
    unmatched_ingredients: List[str]
    total_ingredients_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
