"""Parse agent response into structured BuildRecommendation."""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from app.schemas.response import (
    BuildRecommendation,
    BuildComponentDetail,
    ComponentResponse,
    CompatibilityIssue,
)
from app.db.database import SessionLocal
from app.db.models import Component

logger = structlog.get_logger()


def parse_agent_response(
    agent_output: str,
    budget_dzd: float,
    use_case: str,
    locale: str,
    db_session
) -> Optional[BuildRecommendation]:
    """
    Parse agent's text response into structured BuildRecommendation.
    
    Args:
        agent_output: Raw text output from agent
        budget_dzd: User's budget
        use_case: Use case
        locale: Locale
        db_session: Database session
        
    Returns:
        BuildRecommendation object or None if parsing fails
    """
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', agent_output, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return _parse_json_response(data, budget_dzd, use_case, locale, db_session)
            except json.JSONDecodeError:
                pass
        
        # Try to extract component IDs from text
        component_ids = _extract_component_ids(agent_output)
        if component_ids:
            return _build_from_component_ids(component_ids, budget_dzd, use_case, locale, db_session)
        
        # Fallback: try to extract component names and search for them
        component_names = _extract_component_names(agent_output)
        if component_names:
            return _build_from_component_names(component_names, budget_dzd, use_case, locale, db_session)
        
        # If all parsing fails, return a basic response with explanation
        logger.warning("Could not parse agent response, returning basic response")
        return _create_fallback_response(agent_output, budget_dzd, use_case, locale)
        
    except Exception as e:
        logger.error(f"Error parsing agent response: {str(e)}")
        return None


def _extract_component_ids(text: str) -> Dict[str, int]:
    """Extract component IDs from agent text."""
    ids = {}
    # Look for patterns like "CPU ID: 123" or "component_id: 456"
    patterns = {
        "cpu": r'(?:cpu|processor).*?id[:\s]+(\d+)',
        "gpu": r'(?:gpu|graphics|video).*?id[:\s]+(\d+)',
        "motherboard": r'(?:motherboard|mobo|mainboard).*?id[:\s]+(\d+)',
        "ram": r'(?:ram|memory).*?id[:\s]+(\d+)',
        "storage": r'(?:storage|ssd|hdd|disk).*?id[:\s]+(\d+)',
        "psu": r'(?:psu|power).*?id[:\s]+(\d+)',
        "case": r'(?:case|chassis).*?id[:\s]+(\d+)',
    }
    
    for comp_type, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ids[comp_type] = int(match.group(1))
    
    return ids


def _extract_component_names(text: str) -> Dict[str, str]:
    """Extract component names from agent text."""
    names = {}
    # Look for patterns like "CPU: Intel i5-12400" or "GPU: RTX 3060"
    patterns = {
        "cpu": r'(?:cpu|processor)[:\s]+([A-Za-z0-9\s\-]+?)(?:\n|,|$)',
        "gpu": r'(?:gpu|graphics|video)[:\s]+([A-Za-z0-9\s\-]+?)(?:\n|,|$)',
        "motherboard": r'(?:motherboard|mobo)[:\s]+([A-Za-z0-9\s\-]+?)(?:\n|,|$)',
        "ram": r'(?:ram|memory)[:\s]+([A-Za-z0-9\s\-]+?)(?:\n|,|$)',
        "storage": r'(?:storage|ssd|hdd)[:\s]+([A-Za-z0-9\s\-]+?)(?:\n|,|$)',
        "psu": r'(?:psu|power)[:\s]+([A-Za-z0-9\s\-]+?)(?:\n|,|$)',
    }
    
    for comp_type, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            names[comp_type] = match.group(1).strip()
    
    return names


def _build_from_component_ids(
    component_ids: Dict[str, int],
    budget_dzd: float,
    use_case: str,
    locale: str,
    db_session
) -> Optional[BuildRecommendation]:
    """Build recommendation from component IDs."""
    components = {}
    total_price = 0.0
    
    for comp_type, comp_id in component_ids.items():
        component = db_session.query(Component).filter(Component.id == comp_id).first()
        if component:
            components[comp_type] = component
            total_price += component.price_dzd
    
    if not components:
        return None
    
    # Build response
    build_components = {}
    for comp_type in ["cpu", "gpu", "motherboard", "ram", "storage", "psu"]:
        if comp_type in components:
            comp = components[comp_type]
            build_components[comp_type] = BuildComponentDetail(
                component=ComponentResponse.model_validate(comp),
                reason=f"Selected based on {use_case} requirements",
                alternatives=[]
            )
    
    # Check compatibility
    comp_ids = list(component_ids.values())
    from app.agent.tools import check_compatibility
    compat_result = check_compatibility.invoke({"component_ids": comp_ids})
    
    compatibility_issues = []
    try:
        compat_data = eval(compat_result) if isinstance(compat_result, str) else compat_result
        if not compat_data.get("compatible", True):
            for issue in compat_data.get("issues", []):
                compatibility_issues.append(
                    CompatibilityIssue(
                        severity=issue.get("severity", "warning"),
                        component_ids=[comp_ids[0]],  # Simplified
                        issue_type=issue.get("type", "unknown"),
                        description=issue.get("description", ""),
                        suggestion=issue.get("suggestion")
                    )
                )
    except:
        pass
    
    return BuildRecommendation(
        **build_components,
        total_price_dzd=total_price,
        budget_dzd=budget_dzd,
        budget_utilization=(total_price / budget_dzd * 100) if budget_dzd > 0 else 0,
        overall_score=75.0,  # Default
        compatibility_score=100.0 if not compatibility_issues else 50.0,
        value_score=80.0,
        performance_score=75.0,
        compatibility_issues=compatibility_issues,
        strengths=[],
        weaknesses=[],
        use_case=use_case,
        locale=locale,
        explanation="Build generated from agent recommendation",
    )


def _build_from_component_names(
    component_names: Dict[str, str],
    budget_dzd: float,
    use_case: str,
    locale: str,
    db_session
) -> Optional[BuildRecommendation]:
    """Build recommendation by searching for component names."""
    # This is a simplified version - in production, use better matching
    components = {}
    
    for comp_type, name in component_names.items():
        # Search for component by name
        component = db_session.query(Component).filter(
            Component.name.ilike(f"%{name}%")
        ).first()
        
        if component:
            components[comp_type] = component
    
    if not components:
        return None
    
    # Similar to _build_from_component_ids
    component_ids = {k: v.id for k, v in components.items()}
    return _build_from_component_ids(component_ids, budget_dzd, use_case, locale, db_session)


def _parse_json_response(
    data: Dict[str, Any],
    budget_dzd: float,
    use_case: str,
    locale: str,
    db_session
) -> Optional[BuildRecommendation]:
    """Parse JSON response from agent."""
    # Extract component IDs or names from JSON
    component_ids = {}
    for key in ["cpu", "gpu", "motherboard", "ram", "storage", "psu"]:
        if key in data:
            comp_data = data[key]
            if isinstance(comp_data, dict):
                if "id" in comp_data:
                    component_ids[key] = comp_data["id"]
    
    if component_ids:
        return _build_from_component_ids(component_ids, budget_dzd, use_case, locale, db_session)
    
    return None


def _create_fallback_response(
    agent_output: str,
    budget_dzd: float,
    use_case: str,
    locale: str
) -> BuildRecommendation:
    """Create a fallback response when parsing fails."""
    return BuildRecommendation(
        cpu=BuildComponentDetail(
            component=ComponentResponse(
                id=0,
                component_type="cpu",
                name="Unknown",
                price_dzd=0,
                condition="new",
                in_stock=False,
                source_platform="unknown",
            ),
            reason="Could not parse agent response",
            alternatives=[]
        ),
        gpu=BuildComponentDetail(
            component=ComponentResponse(
                id=0,
                component_type="gpu",
                name="Unknown",
                price_dzd=0,
                condition="new",
                in_stock=False,
                source_platform="unknown",
            ),
            reason="Could not parse agent response",
            alternatives=[]
        ),
        motherboard=BuildComponentDetail(
            component=ComponentResponse(
                id=0,
                component_type="motherboard",
                name="Unknown",
                price_dzd=0,
                condition="new",
                in_stock=False,
                source_platform="unknown",
            ),
            reason="Could not parse agent response",
            alternatives=[]
        ),
        ram=BuildComponentDetail(
            component=ComponentResponse(
                id=0,
                component_type="ram",
                name="Unknown",
                price_dzd=0,
                condition="new",
                in_stock=False,
                source_platform="unknown",
            ),
            reason="Could not parse agent response",
            alternatives=[]
        ),
        storage=BuildComponentDetail(
            component=ComponentResponse(
                id=0,
                component_type="storage",
                name="Unknown",
                price_dzd=0,
                condition="new",
                in_stock=False,
                source_platform="unknown",
            ),
            reason="Could not parse agent response",
            alternatives=[]
        ),
        psu=BuildComponentDetail(
            component=ComponentResponse(
                id=0,
                component_type="psu",
                name="Unknown",
                price_dzd=0,
                condition="new",
                in_stock=False,
                source_platform="unknown",
            ),
            reason="Could not parse agent response",
            alternatives=[]
        ),
        total_price_dzd=0,
        budget_dzd=budget_dzd,
        budget_utilization=0,
        overall_score=0,
        compatibility_score=0,
        value_score=0,
        performance_score=0,
        compatibility_issues=[],
        strengths=[],
        weaknesses=[],
        use_case=use_case,
        locale=locale,
        explanation=agent_output[:500],  # Use first 500 chars of agent output
    )

