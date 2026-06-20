import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app import models, schemas

# Noise words to strip when cleaning ingredients for matching
NOISE_PATTERN = re.compile(
    r"\b(preservative[s]?|color[s]?|colour[s]?|stabilizer[s]?|emulsifier[s]?|artificial|natural|identical|flavour[s]?|flavor[s]?|permitted|contains|class\s+(i|ii|1|2)|added|active|inactive|extract|powder|oil|gel|purified|concentrate)\b",
    re.IGNORECASE
)

def clean_ingredient_text(text: str) -> str:
    """
    Cleans an ingredient string to prepare it for matching.
    Lwrs case, removes common noise words, brackets, and extra punctuation.
    """
    if not text:
        return ""
    
    # Lowercase
    cleaned = text.lower().strip()
    
    # Remove text in parentheses/brackets (but extract them first for synonyms, handled in matcher)
    # E.g., "Sodium Benzoate (E211)" -> "Sodium Benzoate"
    # E.g., "Color (Ins 102)" -> "Color"
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", cleaned)
    
    # Remove noise terms
    cleaned = NOISE_PATTERN.sub("", cleaned)
    
    # Replace dashes/special symbols with spaces
    cleaned = re.sub(r"[-_/,.:\+]", " ", cleaned)
    
    # Normalize whitespaces
    cleaned = " ".join(cleaned.split())
    
    return cleaned

def extract_brackets_content(text: str) -> List[str]:
    """
    Extracts text from inside parentheses/brackets to check for INS codes or synonyms.
    E.g. "Sodium Benzoate (E211) (Ins-211)" -> ["E211", "Ins-211"]
    """
    if not text:
        return []
    found = re.findall(r"\[(.*?)\]|\((.*?)\)", text)
    results = []
    for f in found:
        # found is a list of tuples since we have two OR capture groups
        val = f[0] or f[1]
        if val:
            cleaned_val = val.strip().lower()
            # Clean INS prefix if any
            cleaned_val = re.sub(r"\bins\b[- ]?", "", cleaned_val)
            results.append(cleaned_val.strip())
    return results

def analyze_ingredients_list(db: Session, ingredients_raw_text: str, product_category: str) -> Dict[str, Any]:
    """
    Parses a raw ingredient text block, splits it into ingredients,
    matches them against the chemicals DB, and calculates risk score.
    """
    # 1. Split raw text by commas, semicolons, or newlines
    raw_ingredients = []
    # Replace newlines with commas to handle multi-line lists
    normalized_text = ingredients_raw_text.replace("\n", ", ").replace("\r", "")
    # Split by comma or semicolon
    for part in re.split(r"[,;]|\band\b", normalized_text):
        part_str = part.strip()
        if part_str and len(part_str) > 1:
            raw_ingredients.append(part_str)
            
    # Remove duplicates from raw ingredients while preserving order
    seen_raw = set()
    unique_raw_ingredients = []
    for ing in raw_ingredients:
        # Check normalized version for duplication
        norm = ing.lower()
        if norm not in seen_raw:
            seen_raw.add(norm)
            unique_raw_ingredients.append(ing)

    # Fetch all chemicals from DB to check matches
    db_chemicals = db.query(models.Chemical).all()
    
    matched_ingredients: List[schemas.IngredientAnalysisDetail] = []
    unmatched_ingredients: List[str] = []
    
    # Count of risks
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    
    # Keep track of which chemical IDs we have already matched to avoid duplicate penalties
    matched_chemical_ids = set()

    for ing in unique_raw_ingredients:
        cleaned_ing = clean_ingredient_text(ing)
        bracket_synonyms = extract_brackets_content(ing)
        
        match_found = False
        matched_chem = None
        match_type = ""
        
        # Check against each database chemical
        for chem in db_chemicals:
            chem_name_lower = chem.name.lower().strip()
            
            # Prepare chemical synonyms
            chem_synonyms = []
            if chem.synonyms:
                chem_synonyms = [s.strip().lower() for s in chem.synonyms.split(",")]
                # Strip INS prefix if present in synonyms (e.g. "INS 211" -> "211")
                chem_synonyms_normalized = []
                for s in chem_synonyms:
                    chem_synonyms_normalized.append(s)
                    chem_synonyms_normalized.append(re.sub(r"\bins\b[- ]?", "", s).strip())
                chem_synonyms = list(set(chem_synonyms_normalized))

            # 1. Check exact match on name
            if cleaned_ing == chem_name_lower or cleaned_ing == re.sub(r"\bins\b[- ]?", "", chem_name_lower).strip():
                match_found = True
                matched_chem = chem
                match_type = "exact"
                break
                
            # 2. Check exact match on synonyms
            synonym_match = False
            for syn in chem_synonyms:
                if cleaned_ing == syn or syn in bracket_synonyms:
                    synonym_match = True
                    break
            
            if synonym_match:
                match_found = True
                matched_chem = chem
                match_type = "synonym"
                break
                
            # 3. Check substring match
            # Avoid matching too short strings to prevent false positives (e.g. "water" matching "methylparaben" is bad, but "bromate" matching "potassium bromate" is good)
            if len(cleaned_ing) > 3:
                # Chemical name is inside the ingredient string (e.g. "sodium benzoate" in "contains sodium benzoate preservative")
                if chem_name_lower in cleaned_ing:
                    match_found = True
                    matched_chem = chem
                    match_type = "substring"
                    break
                
                # Check if any synonym is inside the ingredient string (e.g. "e211" in "preservative e211")
                for syn in chem_synonyms:
                    if len(syn) > 2 and syn in cleaned_ing:
                        match_found = True
                        matched_chem = chem
                        match_type = "synonym_substring"
                        break

        if match_found and matched_chem:
            # Create response model for chemical
            chem_resp = schemas.ChemicalResponse.from_orm(matched_chem)
            matched_ingredients.append(
                schemas.IngredientAnalysisDetail(
                    ingredient_raw=ing,
                    matched_chemical=chem_resp,
                    match_type=match_type
                )
            )
            
            # Increment counts and track for score calculation (deduct only once per chemical type)
            if matched_chem.id not in matched_chemical_ids:
                matched_chemical_ids.add(matched_chem.id)
                risk_lvl = matched_chem.risk_level.upper()
                if risk_lvl == "HIGH":
                    high_risk_count += 1
                elif risk_lvl == "MEDIUM":
                    medium_risk_count += 1
                elif risk_lvl == "LOW":
                    low_risk_count += 1
        else:
            if cleaned_ing: # only add if it's not empty text after cleaning
                unmatched_ingredients.append(ing)

    # 4. Calculate Risk Score (Starts at 100)
    risk_score = 100
    risk_score -= (high_risk_count * 40)
    risk_score -= (medium_risk_count * 20)
    risk_score -= (low_risk_count * 5)
    
    # Clamp score between 0 and 100
    risk_score = max(0, min(100, risk_score))
    
    # 5. Determine Grade
    if risk_score >= 81:
        grade = "A"
    elif risk_score >= 61:
        grade = "B"
    elif risk_score >= 41:
        grade = "C"
    elif risk_score >= 21:
        grade = "D"
    else:
        grade = "F"
        
    # 6. Generate Summary Text
    if high_risk_count > 0:
        critical_chems = [m.matched_chemical.name for m in matched_ingredients if m.matched_chemical.risk_level.upper() == "HIGH"]
        summary = f"Critical Risk: Contains prohibited or highly toxic chemicals ({', '.join(critical_chems[:2])})."
    elif medium_risk_count > 0:
        restricted_chems = [m.matched_chemical.name for m in matched_ingredients if m.matched_chemical.risk_level.upper() == "MEDIUM"]
        summary = f"Moderate Risk: Contains restricted or warning ingredients ({', '.join(restricted_chems[:2])})."
    elif low_risk_count > 0:
        summary = "Low Risk: No major hazards detected, but contains minor concern ingredients."
    else:
        summary = "Safe: Clean ingredient profile! No prohibited or restricted chemicals detected."

    return {
        "risk_score": risk_score,
        "grade": grade,
        "summary": summary,
        "matched_ingredients": matched_ingredients,
        "unmatched_ingredients": unmatched_ingredients,
        "total_ingredients_count": len(unique_raw_ingredients),
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count
    }
