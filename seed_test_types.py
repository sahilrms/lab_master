import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

from app.db.base import Base, engine, get_async_session
from app.models.test_type import TestTypeConfig
from app.models.test import TestType
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# Sample test types data
SAMPLE_TEST_TYPES = [
    # 1. Complete Blood Count (CBC)
    {
        "name": "Complete Blood Count (CBC)",
        "code": "CBC",
        "description": "Evaluates overall health and detects a variety of disorders including anemia, infection, and leukemia.",
        "category": "Hematology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Blood"],
        "tat_hours": 4,
        "parameters": [
            {
                "name": "White Blood Cells",
                "code": "WBC",
                "type": "numeric",
                "unit": "10^3/μL",
                "min_value": 0,
                "max_value": 100,
                "reference_range": {
                    "adult": {"min": 4.5, "max": 11.0},
                    "child": {"min": 5.0, "max": 15.5}
                }
            },
            {
                "name": "Hemoglobin",
                "code": "HGB",
                "type": "numeric",
                "unit": "g/dL",
                "min_value": 0,
                "max_value": 30,
                "reference_range": {
                    "male": {"min": 13.5, "max": 17.5},
                    "female": {"min": 12.0, "max": 15.5}
                }
            },
            {
                "name": "Hematocrit",
                "code": "HCT",
                "type": "numeric",
                "unit": "%",
                "min_value": 0,
                "max_value": 100,
                "reference_range": {
                    "male": {"min": 38.8, "max": 50.0},
                    "female": {"min": 34.9, "max": 44.5}
                }
            },
            {
                "name": "Platelets",
                "code": "PLT",
                "type": "numeric",
                "unit": "10^3/μL",
                "min_value": 0,
                "max_value": 2000,
                "reference_range": {"min": 150, "max": 450}
            }
        ]
    },
    
    # 2. Basic Metabolic Panel (BMP)
    {
        "name": "Basic Metabolic Panel",
        "code": "BMP",
        "description": "Measures glucose, kidney function, and electrolyte/fluid balance.",
        "category": "Chemistry",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 4,
        "parameters": [
            {
                "name": "Glucose",
                "code": "GLU",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 70, "max": 99}
            },
            {
                "name": "Calcium",
                "code": "CA",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 8.5, "max": 10.2}
            },
            {
                "name": "Sodium",
                "code": "NA",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 135, "max": 145}
            },
            {
                "name": "Potassium",
                "code": "K",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 3.5, "max": 5.2}
            },
            {
                "name": "CO2",
                "code": "CO2",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 23, "max": 29}
            },
            {
                "name": "Chloride",
                "code": "CL",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 96, "max": 106}
            },
            {
                "name": "Blood Urea Nitrogen",
                "code": "BUN",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 7, "max": 20}
            },
            {
                "name": "Creatinine",
                "code": "CREAT",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {
                    "male": {"min": 0.7, "max": 1.3},
                    "female": {"min": 0.6, "max": 1.1}
                }
            }
        ]
    },
    
    # 3. Comprehensive Metabolic Panel (CMP)
    {
        "name": "Comprehensive Metabolic Panel",
        "code": "CMP",
        "description": "Includes all BMP tests plus liver function tests and protein levels.",
        "category": "Chemistry",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 6,
        "parameters": [
            # Includes all BMP parameters plus:
            {
                "name": "Total Protein",
                "code": "TP",
                "type": "numeric",
                "unit": "g/dL",
                "reference_range": {"min": 6.0, "max": 8.3}
            },
            {
                "name": "Albumin",
                "code": "ALB",
                "type": "numeric",
                "unit": "g/dL",
                "reference_range": {"min": 3.4, "max": 5.4}
            },
            {
                "name": "Alkaline Phosphatase",
                "code": "ALP",
                "type": "numeric",
                "unit": "U/L",
                "reference_range": {"min": 44, "max": 147}
            },
            {
                "name": "Alanine Aminotransferase",
                "code": "ALT",
                "type": "numeric",
                "unit": "U/L",
                "reference_range": {
                    "male": {"min": 7, "max": 55},
                    "female": {"min": 7, "max": 45}
                }
            },
            {
                "name": "Aspartate Aminotransferase",
                "code": "AST",
                "type": "numeric",
                "unit": "U/L",
                "reference_range": {
                    "male": {"min": 8, "max": 48},
                    "female": {"min": 8, "max": 43}
                }
            },
            {
                "name": "Bilirubin, Total",
                "code": "TBIL",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 0.1, "max": 1.2}
            }
        ]
    },
    
    # 4. Lipid Panel
    {
        "name": "Lipid Panel",
        "code": "LIPID",
        "description": "Measures cholesterol and triglycerides to assess cardiovascular risk.",
        "category": "Chemistry",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Total Cholesterol",
                "code": "CHOL",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 125, "max": 200}
            },
            {
                "name": "HDL Cholesterol",
                "code": "HDL",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 40, "max": 60}
            },
            {
                "name": "LDL Cholesterol",
                "code": "LDL",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 0, "max": 100}
            },
            {
                "name": "Triglycerides",
                "code": "TRIG",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 0, "max": 149}
            }
        ]
    },
    
    # 5. Thyroid Function Tests
    {
        "name": "Thyroid Function Tests",
        "code": "THYROID",
        "description": "Measures thyroid hormone levels to assess thyroid function.",
        "category": "Endocrinology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Thyroid Stimulating Hormone",
                "code": "TSH",
                "type": "numeric",
                "unit": "μIU/mL",
                "reference_range": {"min": 0.4, "max": 4.0}
            },
            {
                "name": "Free Thyroxine",
                "code": "FT4",
                "type": "numeric",
                "unit": "ng/dL",
                "reference_range": {"min": 0.8, "max": 1.8}
            },
            {
                "name": "Free Triiodothyronine",
                "code": "FT3",
                "type": "numeric",
                "unit": "pg/mL",
                "reference_range": {"min": 2.3, "max": 4.2}
            }
        ]
    },
    
    # 6. Hemoglobin A1c
    {
        "name": "Hemoglobin A1c",
        "code": "HBA1C",
        "description": "Measures average blood glucose levels over the past 2-3 months.",
        "category": "Diabetes",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Whole Blood"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Hemoglobin A1c",
                "code": "HBA1C",
                "type": "numeric",
                "unit": "%",
                "reference_range": {"min": 4.0, "max": 5.6}
            }
        ]
    },
    
    # 7. Urinalysis
    {
        "name": "Urinalysis",
        "code": "UA",
        "description": "Analyzes physical, chemical, and microscopic properties of urine.",
        "category": "Urinalysis",
        "test_type": TestType.URINE_TEST,
        "sample_requirements": ["Urine"],
        "tat_hours": 4,
        "parameters": [
            {
                "name": "Color",
                "code": "COLOR",
                "type": "text",
                "reference_range": {"value": "Yellow"}
            },
            {
                "name": "Appearance",
                "code": "APPEARANCE",
                "type": "text",
                "reference_range": {"value": "Clear"}
            },
            {
                "name": "Specific Gravity",
                "code": "SPGR",
                "type": "numeric",
                "reference_range": {"min": 1.005, "max": 1.030}
            },
            {
                "name": "pH",
                "code": "PH",
                "type": "numeric",
                "reference_range": {"min": 4.5, "max": 8.0}
            },
            {
                "name": "Protein",
                "code": "PRO",
                "type": "select",
                "options": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
                "reference_range": {"value": "Negative"}
            },
            {
                "name": "Glucose",
                "code": "GLU",
                "type": "select",
                "options": ["Negative", "Trace", "1+", "2+", "3+", "4+"],
                "reference_range": {"value": "Negative"}
            },
            {
                "name": "Ketones",
                "code": "KET",
                "type": "select",
                "options": ["Negative", "Trace", "1+", "2+", "3+"],
                "reference_range": {"value": "Negative"}
            },
            {
                "name": "Blood",
                "code": "BLOOD",
                "type": "select",
                "options": ["Negative", "Trace", "1+", "2+", "3+"],
                "reference_range": {"value": "Negative"}
            },
            {
                "name": "Leukocyte Esterase",
                "code": "LEUK",
                "type": "select",
                "options": ["Negative", "Trace", "1+", "2+", "3+"],
                "reference_range": {"value": "Negative"}
            }
        ]
    },
    
    # 8. Liver Function Tests (LFT)
    {
        "name": "Liver Function Tests",
        "code": "LFT",
        "description": "Assesses liver function and detects liver damage.",
        "category": "Hepatology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Albumin",
                "code": "ALB",
                "type": "numeric",
                "unit": "g/dL",
                "reference_range": {"min": 3.4, "max": 5.4}
            },
            {
                "name": "Total Protein",
                "code": "TP",
                "type": "numeric",
                "unit": "g/dL",
                "reference_range": {"min": 6.0, "max": 8.3}
            },
            {
                "name": "Alkaline Phosphatase",
                "code": "ALP",
                "type": "numeric",
                "unit": "U/L",
                "reference_range": {"min": 44, "max": 147}
            },
            {
                "name": "Alanine Aminotransferase",
                "code": "ALT",
                "type": "numeric",
                "unit": "U/L",
                "reference_range": {
                    "male": {"min": 7, "max": 55},
                    "female": {"min": 7, "max": 45}
                }
            },
            {
                "name": "Aspartate Aminotransferase",
                "code": "AST",
                "type": "numeric",
                "unit": "U/L",
                "reference_range": {
                    "male": {"min": 8, "max": 48},
                    "female": {"min": 8, "max": 43}
                }
            },
            {
                "name": "Bilirubin, Total",
                "code": "TBIL",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 0.1, "max": 1.2}
            },
            {
                "name": "Bilirubin, Direct",
                "code": "DBIL",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 0.0, "max": 0.3}
            }
        ]
    },
    
    # 9. Renal Function Tests (RFT)
    {
        "name": "Renal Function Tests",
        "code": "RFT",
        "description": "Evaluates kidney function and detects kidney disease.",
        "category": "Nephrology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Blood Urea Nitrogen",
                "code": "BUN",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 7, "max": 20}
            },
            {
                "name": "Creatinine",
                "code": "CREAT",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {
                    "male": {"min": 0.7, "max": 1.3},
                    "female": {"min": 0.6, "max": 1.1}
                }
            },
            {
                "name": "eGFR",
                "code": "EGFR",
                "type": "numeric",
                "unit": "mL/min/1.73m²",
                "reference_range": {"min": 90, "max": 120}
            },
            {
                "name": "Sodium",
                "code": "NA",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 135, "max": 145}
            },
            {
                "name": "Potassium",
                "code": "K",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 3.5, "max": 5.2}
            },
            {
                "name": "Chloride",
                "code": "CL",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 96, "max": 106}
            },
            {
                "name": "Carbon Dioxide",
                "code": "CO2",
                "type": "numeric",
                "unit": "mmol/L",
                "reference_range": {"min": 23, "max": 29}
            }
        ]
    },
    
    # 10. Coagulation Panel
    {
        "name": "Coagulation Panel",
        "code": "COAG",
        "description": "Measures blood clotting ability and screens for bleeding disorders.",
        "category": "Hematology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Plasma"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Prothrombin Time",
                "code": "PT",
                "type": "numeric",
                "unit": "seconds",
                "reference_range": {"min": 11.0, "max": 13.5}
            },
            {
                "name": "INR",
                "code": "INR",
                "type": "numeric",
                "reference_range": {"min": 0.9, "max": 1.1}
            },
            {
                "name": "Activated Partial Thromboplastin Time",
                "code": "APTT",
                "type": "numeric",
                "unit": "seconds",
                "reference_range": {"min": 25, "max": 35}
            },
            {
                "name": "Fibrinogen",
                "code": "FIB",
                "type": "numeric",
                "unit": "mg/dL",
                "reference_range": {"min": 200, "max": 400}
            }
        ]
    },
    
    # 11. Iron Studies
    {
        "name": "Iron Studies",
        "code": "IRON",
        "description": "Measures iron levels and metabolism to diagnose anemia and iron overload.",
        "category": "Hematology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Iron",
                "code": "IRON",
                "type": "numeric",
                "unit": "μg/dL",
                "reference_range": {
                    "male": {"min": 65, "max": 175},
                    "female": {"min": 50, "max": 170}
                }
            },
            {
                "name": "Total Iron Binding Capacity",
                "code": "TIBC",
                "type": "numeric",
                "unit": "μg/dL",
                "reference_range": {"min": 240, "max": 450}
            },
            {
                "name": "Transferrin Saturation",
                "code": "TRANSAT",
                "type": "numeric",
                "unit": "%",
                "reference_range": {"min": 20, "max": 50}
            },
            {
                "name": "Ferritin",
                "code": "FERR",
                "type": "numeric",
                "unit": "ng/mL",
                "reference_range": {
                    "male": {"min": 30, "max": 400},
                    "female": {"min": 15, "max": 150}
                }
            }
        ]
    },
    
    # 12. Vitamin B12 and Folate
    {
        "name": "Vitamin B12 and Folate",
        "code": "B12FOL",
        "description": "Measures levels of vitamin B12 and folic acid to diagnose deficiencies.",
        "category": "Chemistry",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 48,
        "parameters": [
            {
                "name": "Vitamin B12",
                "code": "B12",
                "type": "numeric",
                "unit": "pg/mL",
                "reference_range": {"min": 200, "max": 900}
            },
            {
                "name": "Folate",
                "code": "FOL",
                "type": "numeric",
                "unit": "ng/mL",
                "reference_range": {"min": 3.0, "max": 17.0}
            }
        ]
    },
    
    # 13. C-Reactive Protein (CRP)
    {
        "name": "C-Reactive Protein",
        "code": "CRP",
        "description": "Measures inflammation in the body.",
        "category": "Immunology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "C-Reactive Protein",
                "code": "CRP",
                "type": "numeric",
                "unit": "mg/L",
                "reference_range": {"min": 0, "max": 10}
            }
        ]
    },
    
    # 14. Rheumatoid Factor
    {
        "name": "Rheumatoid Factor",
        "code": "RF",
        "description": "Detects rheumatoid factor, an antibody associated with rheumatoid arthritis.",
        "category": "Immunology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 48,
        "parameters": [
            {
                "name": "Rheumatoid Factor",
                "code": "RF",
                "type": "numeric",
                "unit": "IU/mL",
                "reference_range": {"min": 0, "max": 14}
            }
        ]
    },
    
    # 15. PSA (Prostate-Specific Antigen)
    {
        "name": "Prostate-Specific Antigen",
        "code": "PSA",
        "description": "Screens for prostate cancer and monitors treatment.",
        "category": "Oncology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 48,
        "parameters": [
            {
                "name": "Total PSA",
                "code": "PSA",
                "type": "numeric",
                "unit": "ng/mL",
                "reference_range": {"min": 0, "max": 4.0}
            }
        ]
    },
    
    # 16. D-Dimer
    {
        "name": "D-Dimer",
        "code": "DDIMER",
        "description": "Helps rule out blood clotting disorders like DVT and PE.",
        "category": "Hematology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Plasma"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "D-Dimer",
                "code": "DDIMER",
                "type": "numeric",
                "unit": "μg/mL",
                "reference_range": {"min": 0, "max": 0.5}
            }
        ]
    },
    
    # 17. Cardiac Enzymes
    {
        "name": "Cardiac Enzymes",
        "code": "CARDIAC",
        "description": "Measures enzymes released during heart muscle damage.",
        "category": "Cardiology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 2,
        "parameters": [
            {
                "name": "Troponin I",
                "code": "TROP",
                "type": "numeric",
                "unit": "ng/mL",
                "reference_range": {"min": 0, "max": 0.04}
            },
            {
                "name": "CK-MB",
                "code": "CKMB",
                "type": "numeric",
                "unit": "ng/mL",
                "reference_range": {"min": 0, "max": 5.0}
            },
            {
                "name": "Myoglobin",
                "code": "MYO",
                "type": "numeric",
                "unit": "ng/mL",
                "reference_range": {"min": 0, "max": 90}
            }
        ]
    },
    
    # 18. HbA1c (Glycated Hemoglobin)
    {
        "name": "Glycated Hemoglobin",
        "code": "HBA1C",
        "description": "Measures average blood glucose levels over 2-3 months.",
        "category": "Endocrinology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Whole Blood"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Hemoglobin A1c",
                "code": "HBA1C",
                "type": "numeric",
                "unit": "%",
                "reference_range": {"min": 4.0, "max": 5.6}
            }
        ]
    },
    
    # 19. Vitamin D
    {
        "name": "Vitamin D, 25-Hydroxy",
        "code": "VITD",
        "description": "Measures vitamin D levels to detect deficiency or excess.",
        "category": "Chemistry",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 48,
        "parameters": [
            {
                "name": "Vitamin D, 25-Hydroxy",
                "code": "VITD",
                "type": "numeric",
                "unit": "ng/mL",
                "reference_range": {
                    "deficient": {"max": 20},
                    "insufficient": {"min": 20, "max": 29},
                    "sufficient": {"min": 30, "max": 100},
                    "high": {"min": 100}
                }
            }
        ]
    },
    
    # 20. Stool Occult Blood
    {
        "name": "Fecal Occult Blood Test",
        "code": "FOBT",
        "description": "Detects hidden blood in stool, which may indicate colorectal cancer or other conditions.",
        "category": "Gastroenterology",
        "test_type": TestType.STOOL_TEST,
        "sample_requirements": ["Stool"],
        "tat_hours": 72,
        "parameters": [
            {
                "name": "Occult Blood",
                "code": "FOB",
                "type": "select",
                "options": ["Negative", "Positive"],
                "reference_range": {"value": "Negative"}
            }
        ]
    }
]

async def seed_test_types():
    print("Starting to seed test types...")
    start_time = datetime.now()
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create an async session
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    added_count = 0
    skipped_count = 0
    
    async with async_session() as session:
        for test_type_data in SAMPLE_TEST_TYPES:
            # Check if test type with this code already exists
            existing = await session.execute(
                select(TestTypeConfig).where(TestTypeConfig.code == test_type_data["code"])
            )
            if existing.scalars().first():
                print(f"✓ Test type {test_type_data['code']} already exists, skipping...")
                skipped_count += 1
                continue
            
            # Create the test type
            test_type = TestTypeConfig(**test_type_data)
            session.add(test_type)
            print(f"✓ Added test type: {test_type.name} ({test_type.code})")
            added_count += 1
        
        await session.commit()
    
    duration = (datetime.now() - start_time).total_seconds()
    print(f"\nTest type seeding completed in {duration:.2f} seconds!")
    print(f"Added: {added_count}, Skipped: {skipped_count}, Total: {len(SAMPLE_TEST_TYPES)}")

if __name__ == "__main__":
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession
    
    asyncio.run(seed_test_types())