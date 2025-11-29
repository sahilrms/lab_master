from sqlalchemy import Column, Integer, String, JSON, Enum,Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.test import TestType  # Import the existing TestType enum

class TestTypeConfig(Base):
    """
    Model to store configuration for different types of tests.
    This includes test parameters, reference ranges, and other metadata.
    """
    __tablename__ = "test_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "CBC", "T3T4"
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "Hematology", "Biochemistry"
    test_type = Column(Enum(TestType), nullable=False)  # Links to the main TestType enum
    
    # Test parameters and their configurations
    parameters = Column(JSON, nullable=False, default=list)  # List of parameter objects
    sample_requirements = Column(ARRAY(String), nullable=False, default=[])  # e.g., ["Blood", "Serum"]
    
    # Test metadata
    is_active = Column(Boolean, default=True)
    tat_hours = Column(Integer, nullable=True)  # Turnaround time in hours
    
    # Relationships
    tests = relationship("Test", back_populates="test_type_config")

    def __repr__(self):
        return f"<TestTypeConfig {self.name} ({self.code})>"

    @property
    def parameter_names(self):
        """Return list of parameter names for this test type."""
        return [p["name"] for p in self.parameters] if self.parameters else []

    def get_parameter(self, param_name):
        """Get parameter configuration by name."""
        if not self.parameters:
            return None
        return next((p for p in self.parameters if p["name"] == param_name), None)
