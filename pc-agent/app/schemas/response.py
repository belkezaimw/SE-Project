"""Response schemas for API endpoints."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class ComponentResponse(BaseModel):
    """Response schema for a single component."""
    id: int
    component_type: str
    name: str
    manufacturer: Optional[str]
    model: Optional[str]
    price_dzd: float
    condition: str
    in_stock: bool
    source_platform: str
    seller_location: Optional[str]
    specs: Optional[Dict[str, Any]]
    benchmark_score: Optional[float]
    
    class Config:
        from_attributes = True


class BuildComponentDetail(BaseModel):
    """Detailed component in a build."""
    component: ComponentResponse
    reason: str = Field(..., description="Why this component was selected")
    alternatives: List[ComponentResponse] = Field(default_factory=list)


class CompatibilityIssue(BaseModel):
    """Compatibility issue between components."""
    severity: str = Field(..., description="critical, warning, or info")
    component_ids: List[int]
    issue_type: str
    description: str
    suggestion: Optional[str] = None


class BuildRecommendation(BaseModel):
    """Complete PC build recommendation."""
    build_id: Optional[int] = None
    
    # Components
    cpu: BuildComponentDetail
    gpu: BuildComponentDetail
    motherboard: BuildComponentDetail
    ram: BuildComponentDetail
    storage: BuildComponentDetail
    psu: BuildComponentDetail
    case: Optional[BuildComponentDetail] = None
    cooling: Optional[BuildComponentDetail] = None
    
    # Pricing
    total_price_dzd: float
    budget_dzd: float
    budget_utilization: float = Field(..., description="Percentage of budget used")
    
    # Scores
    overall_score: float = Field(..., ge=0, le=100)
    compatibility_score: float = Field(..., ge=0, le=100)
    value_score: float = Field(..., ge=0, le=100)
    performance_score: float = Field(..., ge=0, le=100)
    
    # Analysis
    compatibility_issues: List[CompatibilityIssue] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    
    # Metadata
    use_case: str
    locale: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI explanation
    explanation: str = Field(..., description="Natural language explanation of the build")


class ComponentListResponse(BaseModel):
    """Paginated list of components."""
    components: List[ComponentResponse]
    total: int
    limit: int
    offset: int


class CompatibilityCheckResponse(BaseModel):
    """Response for compatibility check."""
    compatible: bool
    compatibility_score: float = Field(..., ge=0, le=100)
    issues: List[CompatibilityIssue]
    recommendations: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    redis: str
    llm: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None

