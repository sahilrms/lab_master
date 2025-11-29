from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from enum import Enum
from app.models.test import TestType

class ParameterType(str, Enum):
    NUMERIC = "numeric"
    TEXT = "text"
    SELECT = "select"
    BOOLEAN = "boolean"
    
class ParameterConfig(BaseModel):
    """Configuration for a single test parameter."""
    name: str = Field(..., description="Name of the parameter (e.g., 'Hemoglobin')")
    code: str = Field(..., description="Short code for the parameter (e.g., 'HGB')")
    type: ParameterType = Field(..., description="Type of the parameter")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., 'g/dL')")
    
    # For numeric parameters
    min_value: Optional[float] = Field(None, description="Minimum valid value")
    max_value: Optional[float] = Field(None, description="Maximum valid value")
    
    # For select parameters
    options: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="For SELECT type, list of {value: str, label: str} options"
    )
    
    # Display and validation
    required: bool = Field(True, description="Whether this parameter is required")
    default_value: Optional[Any] = Field(None, description="Default value for this parameter")
    description: Optional[str] = Field(None, description="Description of what this parameter measures")
    
    # For results interpretation
    reference_range: Optional[Dict[str, Any]] = Field(
        None,
        description="Reference range for this parameter (can be age/gender specific)"
    )

class TestTypeBase(BaseModel):
    """Base schema for test type configuration."""
    name: str = Field(..., max_length=100, description="Name of the test type")
    code: str = Field(..., max_length=50, description="Short code for the test type")
    description: Optional[str] = Field(None, description="Detailed description of the test")
    category: Optional[str] = Field(None, description="Test category (e.g., 'Hematology')")
    test_type: TestType = Field(..., description="Type of test from the main TestType enum")
    
    # Test parameters
    parameters: List[ParameterConfig] = Field(..., description="List of test parameters")
    sample_requirements: List[str] = Field(
        default_factory=list, 
        description="List of required samples (e.g., ['Blood', 'Urine'])"
    )
    
    # Metadata
    tat_hours: Optional[int] = Field(
        None, 
        description="Expected turnaround time in hours"
    )
    is_active: bool = Field(True, description="Whether this test type is active")
    
    @validator('code')
    def code_must_be_uppercase(cls, v):
        return v.upper()

class TestTypeCreate(TestTypeBase):
    pass

class TestTypeUpdate(BaseModel):
    """Schema for updating a test type configuration."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    parameters: Optional[List[ParameterConfig]] = None
    sample_requirements: Optional[List[str]] = None
    tat_hours: Optional[int] = None
    is_active: Optional[bool] = None

class TestTypeInDB(TestTypeBase):
    """Test type configuration as stored in the database."""
    id: int
    
    class Config:
        orm_mode = True

# Example test types for initialization
SAMPLE_TEST_TYPES = [
    {
        "name": "Complete Blood Count (CBC)",
        "code": "CBC",
        "description": "A complete blood count (CBC) is a blood test used to evaluate your overall health and detect a wide range of disorders.",
        "category": "Hematology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Blood"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "White Blood Cells",
                "code": "WBC",
                "type": ParameterType.NUMERIC,
                "unit": "10^3/μL",
                "min_value": 0,
                "max_value": 100,
                "reference_range": {
                    "male": {"min": 4.5, "max": 11.0},
                    "female": {"min": 4.5, "max": 11.0},
                    "child": {"min": 5.0, "max": 15.5}
                }
            },
            {
                "name": "Hemoglobin",
                "code": "HGB",
                "type": ParameterType.NUMERIC,
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
                "type": ParameterType.NUMERIC,
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
                "type": ParameterType.NUMERIC,
                "unit": "10^3/μL",
                "min_value": 0,
                "max_value": 2000,
                "reference_range": {"min": 150, "max": 450}
            }
        ]
    },
    {
        "name": "Thyroid Profile (T3, T4, TSH)",
        "code": "THYROID",
        "description": "Thyroid function tests help diagnose thyroid disorders.",
        "category": "Endocrinology",
        "test_type": TestType.BLOOD_TEST,
        "sample_requirements": ["Serum"],
        "tat_hours": 48,
        "parameters": [
            {
                "name": "Triiodothyronine (T3)",
                "code": "T3",
                "type": ParameterType.NUMERIC,
                "unit": "ng/dL",
                "reference_range": {"min": 80, "max": 200}
            },
            {
                "name": "Thyroxine (T4)",
                "code": "T4",
                "type": ParameterType.NUMERIC,
                "unit": "μg/dL",
                "reference_range": {"min": 4.6, "max": 12.0}
            },
            {
                "name": "Thyroid Stimulating Hormone",
                "code": "TSH",
                "type": ParameterType.NUMERIC,
                "unit": "μIU/mL",
                "reference_range": {"min": 0.4, "max": 4.0}
            }
        ]
    },
    {
        "name": "Urine Routine Examination",
        "code": "URINE_RT",
        "description": "Routine urine examination to detect and manage a wide range of disorders.",
        "category": "Pathology",
        "test_type": TestType.URINE_TEST,
        "sample_requirements": ["Urine"],
        "tat_hours": 24,
        "parameters": [
            {
                "name": "Color",
                "code": "COLOR",
                "type": ParameterType.TEXT,
                "reference_range": {"value": "Pale Yellow"}
            },
            {
                "name": "Appearance",
                "code": "APPEARANCE",
                "type": ParameterType.TEXT,
                "reference_range": {"value": "Clear"}
            },
            {
                "name": "pH",
                "code": "PH",
                "type": ParameterType.NUMERIC,
                "reference_range": {"min": 4.5, "max": 8.0}
            },
            {
                "name": "Specific Gravity",
                "code": "SG",
                "type": ParameterType.NUMERIC,
                "reference_range": {"min": 1.003, "max": 1.030}
            },
            {
                "name": "Protein",
                "code": "PROTEIN",
                "type": ParameterType.SELECT,
                "options": [
                    {"value": "NEGATIVE", "label": "Negative"},
                    {"value": "TRACE", "label": "Trace"},
                    {"value": "1+", "label": "1+"},
                    {"value": "2+", "label": "2+"},
                    {"value": "3+", "label": "3+"},
                    {"value": "4+", "label": "4+"}
                ],
                "reference_range": {"value": "NEGATIVE"}
            },
            {
                "name": "Glucose",
                "code": "GLUCOSE",
                "type": ParameterType.SELECT,
                "options": [
                    {"value": "NEGATIVE", "label": "Negative"},
                    {"value": "TRACE", "label": "Trace"},
                    {"value": "1+", "label": "1+"},
                    {"value": "2+", "label": "2+"},
                    {"value": "3+", "label": "3+"},
                    {"value": "4+", "label": "4+"}
                ],
                "reference_range": {"value": "NEGATIVE"}
            },
            {
                "name": "Ketones",
                "code": "KETONES",
                "type": ParameterType.SELECT,
                "options": [
                    {"value": "NEGATIVE", "label": "Negative"},
                    {"value": "TRACE", "label": "Trace"},
                    {"value": "1+", "label": "1+"},
                    {"value": "2+", "label": "2+"},
                    {"value": "3+", "label": "3+"}
                ],
                "reference_range": {"value": "NEGATIVE"}
            },
            {
                "name": "Blood",
                "code": "BLOOD",
                "type": ParameterType.SELECT,
                "options": [
                    {"value": "NEGATIVE", "label": "Negative"},
                    {"value": "TRACE", "label": "Trace"},
                    {"value": "1+", "label": "1+"},
                    {"value": "2+", "label": "2+"},
                    {"value": "3+", "label": "3+"}
                ],
                "reference_range": {"value": "NEGATIVE"}
            }
        ]
    }
]
