"""Request schemas for API endpoints."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum


class UseCase(str, Enum):
    """PC use case types."""
    GAMING = "gaming"
    PRODUCTIVITY = "productivity"
    AI_ML = "ai_ml"
    CONTENT_CREATION = "content_creation"
    GENERAL = "general"
    MIXED = "mixed"


class Locale(str, Enum):
    """Supported locales."""
    ARABIC = "ar"
    FRENCH = "fr"
    ENGLISH = "en"


class ComponentPreference(BaseModel):
    """User preferences for specific components."""
    prefer_new: bool = True
    prefer_used: bool = True
    brands: Optional[List[str]] = None
    exclude_brands: Optional[List[str]] = None
    min_warranty_months: Optional[int] = None


class BuildRequest(BaseModel):
    """Request schema for PC build recommendation."""
    budget_dzd: float = Field(..., gt=0, description="Budget in Algerian Dinar")
    use_case: UseCase = Field(..., description="Primary use case for the PC")
    locale: Locale = Field(default=Locale.FRENCH, description="Preferred language")
    
    # Optional preferences
    wilaya: Optional[str] = Field(None, description="Preferred wilaya for local pickup")
    preferences: Optional[Dict[str, ComponentPreference]] = Field(
        default_factory=dict,
        description="Component-specific preferences"
    )
    
    # Performance priorities (0-10 scale)
    gaming_priority: int = Field(default=5, ge=0, le=10)
    productivity_priority: int = Field(default=5, ge=0, le=10)
    ai_priority: int = Field(default=5, ge=0, le=10)
    
    # Constraints
    max_power_consumption_watts: Optional[int] = None
    form_factor: Optional[str] = None  # ATX, mATX, ITX
    
    @field_validator('budget_dzd')
    @classmethod
    def validate_budget(cls, v):
        if v < 30000:  
            raise ValueError("Budget too low for a complete PC build")
        if v > 10000000: 
            raise ValueError("Budget exceeds reasonable limits")
        return v


class ComponentQuery(BaseModel):
    component_type: Optional[str] = None
    search_term: Optional[str] = None
    min_price_dzd: Optional[float] = None
    max_price_dzd: Optional[float] = None
    condition: Optional[str] = None
    manufacturer: Optional[str] = None
    in_stock_only: bool = True
    locale: Locale = Field(default=Locale.FRENCH)
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0)


class CompatibilityCheckRequest(BaseModel):
    component_ids: List[int] = Field(..., min_length=2, description="List of component IDs to check")
    locale: Locale = Field(default=Locale.FRENCH)

