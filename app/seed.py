from sqlalchemy.orm import Session
from app import models

INITIAL_CHEMICALS = [
    # --- FSSAI FOOD ADDITIVES (PROHIBITED) ---
    {
        "name": "Potassium Bromate",
        "cas_number": "7758-01-2",
        "synonyms": "E924, E-924, bromated flour",
        "category": "Food",
        "regulatory_status": "Prohibited",
        "regulatory_body": "FSSAI",
        "risk_level": "High",
        "health_risks": "Class 2B carcinogen, kidney toxicity, thyroid disruption, oxidative stress.",
        "regulatory_limit": "Banned in food/bakery products since 2016.",
        "description": "Historically used as a flour improver to strengthen dough and allow higher rising. Banned in India, EU, UK, Canada, and China due to cancer risks.",
        "source_url": "https://www.fssai.gov.in/"
    },
    {
        "name": "Potassium Iodate",
        "cas_number": "7758-05-6",
        "synonyms": "iodate of potash",
        "category": "Food",
        "regulatory_status": "Prohibited",
        "regulatory_body": "FSSAI",
        "risk_level": "High",
        "health_risks": "May lead to thyroid gland dysfunction, iodine overload, and thyroiditis.",
        "regulatory_limit": "Banned as a flour treatment agent in bakery products (2016).",
        "description": "Previously used as a dough conditioner. Prohibited in bakery items to protect thyroid health, though still permitted in iodized salt at specific levels.",
        "source_url": "https://www.fssai.gov.in/"
    },
    {
        "name": "Rhodamine B",
        "cas_number": "81-88-9",
        "synonyms": "D&C Red No. 19, basic violet 10",
        "category": "Food",
        "regulatory_status": "Prohibited",
        "regulatory_body": "FSSAI",
        "risk_level": "High",
        "health_risks": "Carcinogenic, mutagenic, severe skin and eye irritant, liver and kidney damage.",
        "regulatory_limit": "Strictly prohibited in all food products. Zero tolerance.",
        "description": "An industrial synthetic dye commonly used for dyeing paper and leather. Frequently found illegally added to street foods like cotton candy (budhiya ka baal), chili powder, and sweets for vibrant red coloring.",
        "source_url": "https://www.fssai.gov.in/"
    },
    {
        "name": "Metanil Yellow",
        "cas_number": "587-98-4",
        "synonyms": "Acid Yellow 36",
        "category": "Food",
        "regulatory_status": "Prohibited",
        "regulatory_body": "FSSAI",
        "risk_level": "High",
        "health_risks": "Neurotoxic, testicular damage, degenerative changes in liver and kidneys, carcinogenic properties.",
        "regulatory_limit": "Strictly prohibited in all food products.",
        "description": "A non-permitted food dye widely used in textiles. Often adulterated in turmeric (haldi) powder, ladoos, biryani, and pulses (dal) to enhance yellow appearance.",
        "source_url": "https://www.fssai.gov.in/"
    },
    # --- FSSAI FOOD ADDITIVES (RESTRICTED) ---
    {
        "name": "Sodium Benzoate",
        "cas_number": "532-32-1",
        "synonyms": "E211, E-211, benzoate of soda",
        "category": "Food",
        "regulatory_status": "Restricted",
        "regulatory_body": "FSSAI",
        "risk_level": "Medium",
        "health_risks": "Can form Benzene (a class 1 carcinogen) when combined with Vitamin C (Ascorbic Acid). Linked to hyperactivity/ADHD in children.",
        "regulatory_limit": "Max 600 ppm in carbonated beverages; limits vary from 120-1000 ppm by food category.",
        "description": "A widely used food preservative to prevent mold, yeast, and bacterial growth. Commonly found in carbonated soft drinks, pickles, jams, and salad dressings.",
        "source_url": "https://www.fssai.gov.in/"
    },
    {
        "name": "Aspartame",
        "cas_number": "22839-47-0",
        "synonyms": "E951, E-951, NutraSweet, Equal",
        "category": "Food",
        "regulatory_status": "Restricted",
        "regulatory_body": "FSSAI",
        "risk_level": "Medium",
        "health_risks": "Warning required for Phenylketonurics (contains phenylalanine). Possible carcinogen (IARC Group 2B). High intake linked to headaches and mood changes.",
        "regulatory_limit": "Max 700 ppm in carbonated water/beverages; requires mandatory warning label: 'CONTAINS ASPARTAME. NOT RECOMMENDED FOR CHILDREN.'",
        "description": "An artificial low-calorie sweetener about 200 times sweeter than sucrose. Widely used in diet sodas, sugar-free chewing gum, and sugar substitute packets.",
        "source_url": "https://www.fssai.gov.in/"
    },
    {
        "name": "Acesulfame Potassium",
        "cas_number": "55589-62-3",
        "synonyms": "E950, E-950, Acesulfame K, Ace K",
        "category": "Food",
        "regulatory_status": "Restricted",
        "regulatory_body": "FSSAI",
        "risk_level": "Medium",
        "health_risks": "Potential impact on metabolic health, gut microbiome alterations.",
        "regulatory_limit": "Max 600 ppm in beverages. Requires warning labels: 'CONTAINS ACESULFAME POTASSIUM'.",
        "description": "A calorie-free sugar substitute often blended with aspartame or sucralose to mask bitter aftertastes.",
        "source_url": "https://www.fssai.gov.in/"
    },
    {
        "name": "BHA (Butylated Hydroxyanisole)",
        "cas_number": "25013-16-5",
        "synonyms": "E320, E-320",
        "category": "Food",
        "regulatory_status": "Restricted",
        "regulatory_body": "FSSAI",
        "risk_level": "Medium",
        "health_risks": "Endocrine disruptor, estrogenic mimic, anticipated human carcinogen based on animal studies.",
        "regulatory_limit": "Max 200 ppm individually or in combination with BHT in edible oils and fats.",
        "description": "A synthetic antioxidant used to preserve fats and oils in food and cosmetics, preventing them from turning rancid.",
        "source_url": "https://www.fssai.gov.in/"
    },
    {
        "name": "BHT (Butylated Hydroxytoluene)",
        "cas_number": "128-37-0",
        "synonyms": "E321, E-321",
        "category": "Food",
        "regulatory_status": "Restricted",
        "regulatory_body": "FSSAI",
        "risk_level": "Medium",
        "health_risks": "Endocrine disruptor, liver and kidney enlargement in animal studies, potential allergen.",
        "regulatory_limit": "Max 200 ppm individually or combined with BHA in fats, oils, and breakfast cereals.",
        "description": "A synthetic phenolic antioxidant closely related to BHA. Used to maintain freshness, texture, and flavor in processed foods.",
        "source_url": "https://www.fssai.gov.in/"
    },
    # --- CDSCO COSMETIC INGREDIENTS (PROHIBITED) ---
    {
        "name": "Formaldehyde",
        "cas_number": "50-00-0",
        "synonyms": "formalin, methanal, formic aldehyde",
        "category": "Cosmetics",
        "regulatory_status": "Prohibited",
        "regulatory_body": "CDSCO",
        "risk_level": "High",
        "health_risks": "Known human carcinogen (nasopharyngeal cancer), severe contact allergen, asthmatic trigger.",
        "regulatory_limit": "Banned in general cosmetics. Allowed up to 5% in nail hardeners with warning label.",
        "description": "A strong-smelling gas used as a preservative. Banned in leave-on cosmetics in India/EU due to carcinogenicity, though formaldehdye-releasing preservatives (like DMDM hydantoin) are still restrictedly allowed.",
        "source_url": "https://cdsco.gov.in/"
    },
    {
        "name": "Mercury",
        "cas_number": "7439-97-6",
        "synonyms": "mercuric oxide, calomel, quicksilver",
        "category": "Cosmetics",
        "regulatory_status": "Prohibited",
        "regulatory_body": "CDSCO",
        "risk_level": "High",
        "health_risks": "Kidney damage, nervous system disorders, skin peeling, hyperpigmentation, depression/irritability.",
        "regulatory_limit": "Prohibited in general cosmetics. Traces allowed under 1 ppm.",
        "description": "Heavy metal historically added to skin lightening creams and soaps to inhibit melanin production. Strongly prohibited globally under the Minamata Convention.",
        "source_url": "https://cdsco.gov.in/"
    },
    {
        "name": "Isobutylparaben",
        "cas_number": "4247-02-3",
        "synonyms": "isobutyl p-hydroxybenzoate",
        "category": "Cosmetics",
        "regulatory_status": "Prohibited",
        "regulatory_body": "CDSCO",
        "risk_level": "High",
        "health_risks": "Endocrine disruptor, mimics estrogen, reproductive toxicity.",
        "regulatory_limit": "Banned in cosmetics under India's Drugs and Cosmetics Rules (aligned with EU ban).",
        "description": "A long-chain paraben used as an antimicrobial preservative. Prohibited due to concerns over high estrogenic potency and absorption through skin.",
        "source_url": "https://cdsco.gov.in/"
    },
    {
        "name": "Isopropylparaben",
        "cas_number": "4191-73-5",
        "synonyms": "isopropyl p-hydroxybenzoate",
        "category": "Cosmetics",
        "regulatory_status": "Prohibited",
        "regulatory_body": "CDSCO",
        "risk_level": "High",
        "health_risks": "Endocrine disruptor, estrogenic mimic, potential link to hormone-sensitive cancers.",
        "regulatory_limit": "Banned in cosmetics in India.",
        "description": "An ester of p-hydroxybenzoic acid used as a preservative. Banned due to safety concerns regarding reproductive and developmental toxicity.",
        "source_url": "https://cdsco.gov.in/"
    },
    # --- CDSCO COSMETIC INGREDIENTS (RESTRICTED) ---
    {
        "name": "Triclosan",
        "cas_number": "3380-34-5",
        "synonyms": "Irgasan, DP300",
        "category": "Cosmetics",
        "regulatory_status": "Restricted",
        "regulatory_body": "CDSCO",
        "risk_level": "Medium",
        "health_risks": "Thyroid hormone disruption, bioaccumulative, contributes to antibiotic resistance, aquatic toxicant.",
        "regulatory_limit": "Max concentration 0.3% in mouthwashes, hand soaps, shower gels, and deodorants.",
        "description": "An antibacterial and antifungal agent. Limits are strictly enforced due to its persistent nature and endocrine disrupting profile.",
        "source_url": "https://cdsco.gov.in/"
    },
    {
        "name": "p-Phenylenediamine",
        "cas_number": "106-50-3",
        "synonyms": "PPD, 1,4-benzenediamine",
        "category": "Cosmetics",
        "regulatory_status": "Restricted",
        "regulatory_body": "CDSCO",
        "risk_level": "High",
        "health_risks": "Extreme contact allergen, anaphylaxis risk, kidney failure in poisoning cases, bladder cancer risk in hair stylists.",
        "regulatory_limit": "Max concentration 2.0% in hair dyes after dilution. Warning label mandatory: 'Can cause allergic reactions.'",
        "description": "An organic compound essential for permanent hair dyes. Known as one of the most potent contact allergens.",
        "source_url": "https://cdsco.gov.in/"
    },
    {
        "name": "Methylparaben",
        "cas_number": "99-76-3",
        "synonyms": "E218, E-218, methyl p-hydroxybenzoate",
        "category": "Cosmetics",
        "regulatory_status": "Restricted",
        "regulatory_body": "CDSCO",
        "risk_level": "Low",
        "health_risks": "Weak estrogenic activity, skin irritation in high concentrations.",
        "regulatory_limit": "Max 0.4% (as acid) for single ester; Max 0.8% for mixtures of parabens.",
        "description": "A short-chain paraben preservative. Considered safe at low concentrations, though consumers frequently avoid it due to overall paraben concerns.",
        "source_url": "https://cdsco.gov.in/"
    },
    {
        "name": "Ethylparaben",
        "cas_number": "120-47-8",
        "synonyms": "E214, E-214, ethyl p-hydroxybenzoate",
        "category": "Cosmetics",
        "regulatory_status": "Restricted",
        "regulatory_body": "CDSCO",
        "risk_level": "Low",
        "health_risks": "Weak estrogenic activity.",
        "regulatory_limit": "Max 0.4% for single ester; Max 0.8% for mixtures of parabens.",
        "description": "A widely used paraben preservative to extend shelf life in makeup, lotions, and shampoos.",
        "source_url": "https://cdsco.gov.in/"
    }
]

INITIAL_PRODUCTS = [
    {
        "name": "Atta White Sandwich Bread",
        "brand": "Britannia Premium",
        "category": "Food",
        "ingredients_text": "Wheat Flour (Atta 60%), Refined Wheat Flour (Maida), Sugar, Yeast, Iodized Salt, Preservative (Sodium Benzoate E211), Flour Treatment Agent (Potassium Bromate E924), Gluten, Soya Flour, Water",
        "risk_score": 40  # 100 - 40 (Potassium Bromate) - 20 (Sodium Benzoate) = 40 (Grade D)
    },
    {
        "name": "Daily Brightness Glow Cream",
        "brand": "Fair Glow",
        "category": "Cosmetics",
        "ingredients_text": "Water, Palmitic Acid, Stearic Acid, Niacinamide, Glycerin, Preservative (Isopropylparaben), Methylparaben, Perfume, Titanium Dioxide, Disodium EDTA",
        "risk_score": 35  # 100 - 40 (Isopropylparaben) - 20 (Triclosan or similar, wait: Methylparaben is low risk - 5) -> 55 (Grade C/D)
    },
    {
        "name": "Natural Almond Honey Oats Muesli",
        "brand": "Organic Harvest",
        "category": "Food",
        "ingredients_text": "Whole Grain Oats, Rolled Oats, Almonds, Honey, Chia Seeds, Real Vanilla Extract, Raisins, Pumpkin Seeds, Flax Seeds",
        "risk_score": 100  # Clean! (Grade A)
    },
    {
        "name": "Super Charcoal Face Polish",
        "brand": "Nox Cleansing",
        "category": "Cosmetics",
        "ingredients_text": "Aqua, Charcoal Powder, Glycerin, Antibacterial Triclosan (0.3%), Preservative (Formaldehyde), Cellulose Gum, Fragrance, Benzyl Alcohol",
        "risk_score": 40  # 100 - 40 (Formaldehyde) - 20 (Triclosan) = 40 (Grade D)
    },
    {
        "name": "Dark Brown Permanent Hair Color",
        "brand": "Glossy Lockes",
        "category": "Cosmetics",
        "ingredients_text": "Aqua, Cetearyl Alcohol, Ethanolamine, p-Phenylenediamine (PPD 2.0%), Resorcinol, Sodium Sulfite, Erythorbic Acid, EDTA, Fragrance, Coconut Oil",
        "risk_score": 60  # 100 - 40 (PPD is high risk) = 60 (Grade C)
    }
]

def seed_database(db: Session, force: bool = False):
    """
    Seeds the database with initial FSSAI/CDSCO chemicals and demo products.
    """
    # 1. Handle force reset if requested
    if force:
        db.query(models.Chemical).delete()
        db.query(models.Product).delete()
        db.commit()

    # 2. Check if chemicals already exist (only seed if empty)
    existing_chemicals_count = db.query(models.Chemical).count()
    if existing_chemicals_count == 0:
        print("Seeding initial chemicals...")
        for chem_data in INITIAL_CHEMICALS:
            db_chem = models.Chemical(**chem_data)
            db.add(db_chem)
        db.commit()
        print(f"Successfully seeded {len(INITIAL_CHEMICALS)} chemicals.")
    else:
        print(f"Chemicals table already has {existing_chemicals_count} items. Skipping chemical seeding.")

    # 3. Check if products already exist
    existing_products_count = db.query(models.Product).count()
    if existing_products_count == 0:
        print("Seeding initial products...")
        for prod_data in INITIAL_PRODUCTS:
            db_prod = models.Product(**prod_data)
            db.add(db_prod)
        db.commit()
        print(f"Successfully seeded {len(INITIAL_PRODUCTS)} products.")
    else:
        print(f"Products table already has {existing_products_count} items. Skipping product seeding.")
