import os
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas, crud, database, analyzer, seed
from app.database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chemical Risk Analyzer",
    description="FSSAI & CDSCO chemical risk profiling system for Indian products.",
    version="1.0.0"
)

# Enable CORS for local testing/development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to automatically seed empty database
@app.on_event("startup")
def startup_event():
    db = next(database.get_db())
    try:
        seed.seed_database(db, force=False)
    finally:
        db.close()

# --- API Endpoints ---

@app.get("/api/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns summary statistics for the dashboard.
    """
    total_products = db.query(models.Product).count()
    total_chemicals = db.query(models.Chemical).count()
    
    # Calculate average risk score
    avg_score_query = db.query(models.Product.risk_score).all()
    avg_score = 100
    if avg_score_query:
        scores = [r[0] for r in avg_score_query if r[0] is not None]
        if scores:
            avg_score = int(sum(scores) / len(scores))
            
    # Risk breakdowns in database chemicals
    high_risk_chems = db.query(models.Chemical).filter(models.Chemical.risk_level.ilike("High")).count()
    med_risk_chems = db.query(models.Chemical).filter(models.Chemical.risk_level.ilike("Medium")).count()
    low_risk_chems = db.query(models.Chemical).filter(models.Chemical.risk_level.ilike("Low")).count()
    
    # Recently scanned high-risk products
    high_risk_products = db.query(models.Product).filter(
        models.Product.risk_score <= 40
    ).order_by(models.Product.created_at.desc()).limit(5).all()
    
    # Recent scans list
    recent_scans = db.query(models.Product).order_by(
        models.Product.created_at.desc()
    ).limit(5).all()

    return {
        "total_products": total_products,
        "total_chemicals": total_chemicals,
        "average_risk_score": avg_score,
        "chemical_risk_breakdown": {
            "high": high_risk_chems,
            "medium": med_risk_chems,
            "low": low_risk_chems
        },
        "recent_scans": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "risk_score": p.risk_score,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
            } for p in recent_scans
        ],
        "high_risk_products": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "risk_score": p.risk_score,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
            } for p in high_risk_products
        ]
    }

@app.post("/api/analyze", response_model=schemas.AnalysisResponse)
def analyze_ingredients(request: schemas.AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyzes raw ingredients text against regulated chemicals database.
    Does not write anything to the Product list.
    """
    analysis = analyzer.analyze_ingredients_list(db, request.ingredients_text, request.category)
    return schemas.AnalysisResponse(
        product_name=request.name,
        brand=request.brand,
        category=request.category,
        risk_score=analysis["risk_score"],
        grade=analysis["grade"],
        summary=analysis["summary"],
        matched_ingredients=analysis["matched_ingredients"],
        unmatched_ingredients=analysis["unmatched_ingredients"],
        total_ingredients_count=analysis["total_ingredients_count"],
        high_risk_count=analysis["high_risk_count"],
        medium_risk_count=analysis["medium_risk_count"],
        low_risk_count=analysis["low_risk_count"]
    )

@app.get("/api/chemicals", response_model=List[schemas.ChemicalResponse])
def read_chemicals(
    search: Optional[str] = Query(None, description="Search by name, synonyms, CAS number, or hazards"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lists and searches chemicals in the registry.
    """
    return crud.get_chemicals(db, skip=skip, limit=limit, search=search)

@app.post("/api/chemicals", response_model=schemas.ChemicalResponse)
def create_chemical(chemical: schemas.ChemicalCreate, db: Session = Depends(get_db)):
    """
    Adds a new regulated chemical to the database.
    """
    db_chem = crud.get_chemical_by_name(db, chemical.name)
    if db_chem:
        raise HTTPException(status_code=400, detail=f"Chemical with name '{chemical.name}' already exists.")
    return crud.create_chemical(db, chemical)

@app.delete("/api/chemicals/{chemical_id}")
def delete_chemical(chemical_id: int, db: Session = Depends(get_db)):
    """
    Deletes a chemical from the database.
    """
    success = crud.delete_chemical(db, chemical_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chemical not found")
    return {"status": "success", "message": "Chemical deleted successfully"}

@app.get("/api/products", response_model=List[schemas.ProductResponse])
def read_products(
    search: Optional[str] = Query(None, description="Search by name, brand, or ingredients"),
    category: Optional[str] = Query(None, description="Filter products by category"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lists and searches products in the scanned product directory.
    """
    return crud.get_products(db, skip=skip, limit=limit, search=search, category=category)

@app.post("/api/products", response_model=schemas.ProductResponse)
def create_and_analyze_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Analyzes ingredients list and creates/saves the product in the database.
    """
    # 1. Analyze ingredients to find risk score
    analysis = analyzer.analyze_ingredients_list(db, product.ingredients_text, product.category)
    risk_score = analysis["risk_score"]
    
    # 2. Save product to database
    return crud.create_product(db, product, risk_score)

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Deletes an analyzed product from the directory.
    """
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "success", "message": "Product deleted successfully"}

@app.post("/api/admin/seed-reset")
def reset_seed_data(db: Session = Depends(get_db)):
    """
    Deletes existing data and refills database with official FSSAI & CDSCO rules.
    """
    seed.seed_database(db, force=True)
    return {"status": "success", "message": "Database successfully reset and re-seeded."}

# --- Static File Serving ---
# Ensure static directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

# Serve SPA Frontend
@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Catch-all to serve index.html for static routers if needed
@app.get("/scan")
def read_scan():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/products")
def read_products_page():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/chemicals")
def read_chemicals_page():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/admin")
def read_admin_page():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Mount remaining static resources
app.mount("/", StaticFiles(directory=static_dir), name="static")
