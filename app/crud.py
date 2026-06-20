from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas

# --- Chemical CRUD ---
def get_chemical(db: Session, chemical_id: int):
    return db.query(models.Chemical).filter(models.Chemical.id == chemical_id).first()

def get_chemical_by_name(db: Session, name: str):
    return db.query(models.Chemical).filter(models.Chemical.name.ilike(name)).first()

def get_chemicals(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.Chemical)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.Chemical.name.ilike(search_filter),
                models.Chemical.synonyms.ilike(search_filter),
                models.Chemical.cas_number.ilike(search_filter),
                models.Chemical.health_risks.ilike(search_filter),
                models.Chemical.regulatory_body.ilike(search_filter)
            )
        )
    return query.order_by(models.Chemical.risk_level.desc(), models.Chemical.name.asc()).offset(skip).limit(limit).all()

def create_chemical(db: Session, chemical: schemas.ChemicalCreate):
    db_chemical = models.Chemical(
        name=chemical.name,
        cas_number=chemical.cas_number,
        synonyms=chemical.synonyms,
        category=chemical.category,
        regulatory_status=chemical.regulatory_status,
        regulatory_body=chemical.regulatory_body,
        risk_level=chemical.risk_level,
        health_risks=chemical.health_risks,
        regulatory_limit=chemical.regulatory_limit,
        description=chemical.description,
        source_url=chemical.source_url
    )
    db.add(db_chemical)
    db.commit()
    db.refresh(db_chemical)
    return db_chemical

def delete_chemical(db: Session, chemical_id: int):
    db_chemical = get_chemical(db, chemical_id)
    if db_chemical:
        db.delete(db_chemical)
        db.commit()
        return True
    return False


# --- Product CRUD ---
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100, search: str = None, category: str = None):
    query = db.query(models.Product)
    if category and category != "All":
        query = query.filter(models.Product.category.ilike(category))
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.Product.name.ilike(search_filter),
                models.Product.brand.ilike(search_filter),
                models.Product.ingredients_text.ilike(search_filter)
            )
        )
    return query.order_by(models.Product.created_at.desc()).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate, risk_score: int):
    db_product = models.Product(
        name=product.name,
        brand=product.brand,
        category=product.category,
        ingredients_text=product.ingredients_text,
        risk_score=risk_score
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False
