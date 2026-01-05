"""SQLAlchemy models for hardware catalog."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.database import Base


class ComponentType(str, enum.Enum):
    """Hardware component types."""
    CPU = "cpu"
    GPU = "gpu"
    MOTHERBOARD = "motherboard"
    RAM = "ram"
    STORAGE = "storage"
    PSU = "psu"
    CASE = "case"
    COOLING = "cooling"


class Condition(str, enum.Enum):
    """Component condition."""
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"


class Component(Base):
    """Hardware component model."""
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    component_type = Column(SQLEnum(ComponentType), nullable=False, index=True)
    
    # Basic info
    name = Column(String(500), nullable=False, index=True)
    manufacturer = Column(String(100), index=True)
    model = Column(String(200), index=True)
    
    # Pricing (in DZD)
    price_dzd = Column(Float, nullable=False, index=True)
    original_price = Column(String(100))  # Original scraped price string
    
    # Availability
    condition = Column(SQLEnum(Condition), default=Condition.NEW, index=True)
    in_stock = Column(Boolean, default=True, index=True)
    stock_quantity = Column(Integer, default=0)
    
    # Source
    source_url = Column(Text)
    source_platform = Column(String(100), index=True)  # ouedkniss, local_retailer, etc.
    seller_name = Column(String(200))
    seller_location = Column(String(200))  # Wilaya in Algeria
    
    # Specifications (JSON for flexibility)
    specs = Column(JSON)  # Store detailed specs as JSON
    
    # Performance benchmarks
    benchmark_score = Column(Float)  # Overall performance score
    gaming_score = Column(Float)
    productivity_score = Column(Float)
    ai_score = Column(Float)
    
    # Compatibility data
    socket_type = Column(String(50))  # For CPU/Motherboard
    chipset = Column(String(50))  # For Motherboard
    ram_type = Column(String(20))  # DDR4, DDR5, etc.
    ram_speed = Column(Integer)  # MHz
    tdp_watts = Column(Integer)  # Power consumption
    pcie_slots = Column(String(100))  # For motherboards
    form_factor = Column(String(50))  # ATX, mATX, ITX, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_scraped_at = Column(DateTime(timezone=True))
    
    # Relationships
    translations = relationship("ComponentTranslation", back_populates="component", cascade="all, delete-orphan")


class ComponentTranslation(Base):
    """Multilingual translations for components."""
    __tablename__ = "component_translations"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    
    locale = Column(String(5), nullable=False, index=True)  # ar, fr, en
    
    # Translated fields
    name = Column(String(500))
    description = Column(Text)
    features = Column(Text)  # Bullet points or JSON
    
    component = relationship("Component", back_populates="translations")


class CompatibilityRule(Base):
    """Compatibility rules between components."""
    __tablename__ = "compatibility_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    component_type_1 = Column(SQLEnum(ComponentType), nullable=False)
    component_type_2 = Column(SQLEnum(ComponentType), nullable=False)
    
    rule_type = Column(String(50), nullable=False)  # socket_match, power_requirement, etc.
    rule_logic = Column(JSON)  # Store rule logic as JSON
    
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BuildConfiguration(Base):
    """Saved PC build configurations."""
    __tablename__ = "build_configurations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Build metadata
    name = Column(String(200))
    use_case = Column(String(100), index=True)  # gaming, productivity, ai, etc.
    budget_dzd = Column(Float, nullable=False)
    total_price_dzd = Column(Float)
    
    # Components (store IDs as JSON)
    components = Column(JSON)  # {"cpu": 123, "gpu": 456, ...}
    
    # Performance scores
    overall_score = Column(Float)
    compatibility_score = Column(Float)
    value_score = Column(Float)
    
    # User preferences
    locale = Column(String(5), default="fr")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

