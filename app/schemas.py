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
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "BHA (Butylated Hydroxyanisole)",
                    "cas_number": "25013-16-5",
                    "synonyms": "E320, E-320",
                    "category": "Food",
                    "regulatory_status": "Restricted",
                    "regulatory_body": "FSSAI",
                    "risk_level": "Medium",
                    "health_risks": "Endocrine disruptor, estrogenic mimic, anticipated human carcinogen.",
                    "regulatory_limit": "Max 200 ppm in fats/oils.",
                    "description": "A synthetic antioxidant used to preserve fats and oils in food.",
                    "source_url": "https://www.fssai.gov.in/"
                }
            ]
        }
    }

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
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Atta White Sandwich Bread",
                    "brand": "Britannia Premium",
                    "category": "Food",
                    "ingredients_text": "Wheat Flour (Atta 60%), Maida, Sugar, Yeast, Iodized Salt, Preservative (Sodium Benzoate E211), Flour Treatment Agent (Potassium Bromate E924)"
                },
                {
                    "name": "Daily Brightness Glow Cream",
                    "brand": "Fair Glow",
                    "category": "Cosmetics",
                    "ingredients_text": "Water, Palmitic Acid, Stearic Acid, Niacinamide, Glycerin, Preservative (Isopropylparaben), Methylparaben, Perfume"
                }
            ]
        }
    }

class ProductResponse(ProductBase):
    id: int
    risk_score: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- Catalog Schemas ---
class CatalogProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    category: str
    ingredients_text: str

class CatalogProductCreate(CatalogProductBase):
    pass

class CatalogProductResponse(CatalogProductBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

class CatalogSuggestion(BaseModel):
    """Lightweight catalog entry used for product-name autocomplete."""
    id: int
    name: str
    brand: Optional[str] = None
    category: str

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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Atta White Sandwich Bread",
                    "brand": "Britannia Premium",
                    "category": "Food",
                    "ingredients_text": "Wheat Flour (Atta 60%), Maida, Sugar, Yeast, Iodized Salt, Preservative (Sodium Benzoate E211), Flour Treatment Agent (Potassium Bromate E924)"
                },
                {
                    "name": "Daily Brightness Glow Cream",
                    "brand": "Fair Glow",
                    "category": "Cosmetics",
                    "ingredients_text": "Water, Palmitic Acid, Stearic Acid, Niacinamide, Glycerin, Preservative (Isopropylparaben), Methylparaben, Perfume"
                }
            ]
        }
    }

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
