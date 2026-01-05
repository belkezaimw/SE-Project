"""LangChain tools for the PC build agent."""
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, case
import structlog

from app.db.models import Component, ComponentType, Condition
from app.db.database import SessionLocal

logger = structlog.get_logger()


@tool
def get_parts(
    component_type: str,
    max_price_dzd: Optional[float] = None,
    min_benchmark_score: Optional[float] = None,
    condition: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    Query the database for PC components matching criteria.
    
    Args:
        component_type: Type of component (cpu, gpu, motherboard, ram, storage, psu, case, cooling)
        max_price_dzd: Maximum price in Algerian Dinar
        min_benchmark_score: Minimum benchmark score
        condition: Component condition (new, used, refurbished)
        limit: Maximum number of results
        
    Returns:
        JSON string with matching components
    """
    db = SessionLocal()
    try:
        # Validate component type
        try:
            component_type_enum = ComponentType(component_type.lower())
        except ValueError:
            return f"Error: Invalid component type: {component_type}. Valid types: {[ct.value for ct in ComponentType]}"
        
        query = db.query(Component).filter(
            Component.component_type == component_type_enum,
            Component.in_stock == True
        )
        
        if max_price_dzd:
            query = query.filter(Component.price_dzd <= max_price_dzd)
        
        if min_benchmark_score:
            query = query.filter(Component.benchmark_score >= min_benchmark_score)
        
        if condition:
            try:
                condition_enum = Condition(condition.lower())
                query = query.filter(Component.condition == condition_enum)
            except ValueError:
                logger.warning(f"Invalid condition: {condition}")
        
        # Order by value (performance per DZD) with null/zero safety
        query = query.filter(
            Component.benchmark_score.isnot(None),
            Component.price_dzd > 0
        ).order_by(
            (Component.benchmark_score / Component.price_dzd).desc()
        )
        
        components = query.limit(limit).all()
        
        results = []
        for comp in components:
            results.append({
                "id": comp.id,
                "name": comp.name,
                "price_dzd": comp.price_dzd,
                "condition": comp.condition.value,
                "benchmark_score": comp.benchmark_score,
                "specs": comp.specs,
                "location": comp.seller_location,
            })
        
        logger.info(f"Found {len(results)} {component_type} components")
        return str(results)
        
    except Exception as e:
        logger.error(f"Error querying parts: {str(e)}")
        return f"Error: {str(e)}"
    finally:
        db.close()


@tool
def check_compatibility(component_ids: List[int]) -> str:
    """
    Check compatibility between selected components.
    
    Args:
        component_ids: List of component IDs to check
        
    Returns:
        JSON string with compatibility analysis
    """
    db = SessionLocal()
    try:
        components = db.query(Component).filter(
            Component.id.in_(component_ids)
        ).all()
        
        if len(components) != len(component_ids):
            return "Error: Some component IDs not found"
        
        # Build component map
        comp_map = {comp.component_type.value: comp for comp in components}
        
        issues = []
        compatible = True
        
        # Check CPU-Motherboard socket compatibility
        if "cpu" in comp_map and "motherboard" in comp_map:
            cpu = comp_map["cpu"]
            mobo = comp_map["motherboard"]
            
            if cpu.socket_type and mobo.socket_type:
                if cpu.socket_type != mobo.socket_type:
                    issues.append({
                        "severity": "critical",
                        "type": "socket_mismatch",
                        "description": f"CPU socket {cpu.socket_type} incompatible with motherboard socket {mobo.socket_type}"
                    })
                    compatible = False
        
        # Check RAM compatibility
        if "ram" in comp_map and "motherboard" in comp_map:
            ram = comp_map["ram"]
            mobo = comp_map["motherboard"]
            
            if ram.ram_type and mobo.ram_type:
                if ram.ram_type != mobo.ram_type:
                    issues.append({
                        "severity": "critical",
                        "type": "ram_type_mismatch",
                        "description": f"RAM type {ram.ram_type} incompatible with motherboard {mobo.ram_type}"
                    })
                    compatible = False
        
        # Check PSU wattage
        if "psu" in comp_map:
            psu = comp_map["psu"]
            total_tdp = sum(
                comp.tdp_watts or 0 
                for comp in components 
                if comp.component_type != ComponentType.PSU
            )
            
            psu_wattage = psu.specs.get("wattage", 0) if psu.specs else 0
            recommended_wattage = total_tdp * 1.3  # 30% headroom
            
            if psu_wattage < recommended_wattage:
                issues.append({
                    "severity": "warning",
                    "type": "insufficient_psu",
                    "description": f"PSU {psu_wattage}W may be insufficient. Recommended: {recommended_wattage:.0f}W"
                })
        
        # Check form factor compatibility
        if "motherboard" in comp_map and "case" in comp_map:
            mobo = comp_map["motherboard"]
            case = comp_map["case"]
            
            if mobo.form_factor and case.form_factor:
                # Simplified check - in reality, need more complex logic
                if mobo.form_factor not in case.form_factor:
                    issues.append({
                        "severity": "critical",
                        "type": "form_factor_mismatch",
                        "description": f"Motherboard {mobo.form_factor} may not fit in {case.form_factor} case"
                    })
                    compatible = False
        
        result = {
            "compatible": compatible,
            "compatibility_score": 100 if compatible else (50 if issues else 100),
            "issues": issues,
            "total_tdp_watts": sum(comp.tdp_watts or 0 for comp in components)
        }
        
        logger.info(f"Compatibility check: {compatible}, {len(issues)} issues")
        return str(result)
        
    except Exception as e:
        logger.error(f"Error checking compatibility: {str(e)}")
        return f"Error: {str(e)}"
    finally:
        db.close()


@tool
def normalize_price(price_str: str, source_currency: str = "DZD") -> str:
    """
    Normalize price to DZD.

    Args:
        price_str: Price string to normalize
        source_currency: Source currency (DZD, USD, EUR)

    Returns:
        Normalized price in DZD as string
    """
    from app.core.config import settings
    import re

    try:
        # Extract numeric value
        price_str = price_str.replace(",", "").replace(" ", "")
        match = re.search(r"(\d+(?:\.\d+)?)", price_str)

        if not match:
            return "Error: Could not extract price"

        price = float(match.group(1))

        # Convert to DZD
        if source_currency == "USD":
            price_dzd = price * settings.USD_TO_DZD_RATE
        elif source_currency == "EUR":
            price_dzd = price * settings.EUR_TO_DZD_RATE
        else:
            price_dzd = price

        return str(price_dzd)

    except Exception as e:
        logger.error(f"Error normalizing price: {str(e)}")
        return f"Error: {str(e)}"


@tool
def rate_performance(component_ids: List[int], use_case: str) -> str:
    """
    Rate the performance of a build for a specific use case.

    Args:
        component_ids: List of component IDs in the build
        use_case: Use case to rate for (gaming, productivity, ai_ml, etc.)

    Returns:
        JSON string with performance ratings
    """
    db = SessionLocal()
    try:
        components = db.query(Component).filter(
            Component.id.in_(component_ids)
        ).all()

        comp_map = {comp.component_type.value: comp for comp in components}

        # Calculate use-case specific scores
        scores = {
            "gaming": 0,
            "productivity": 0,
            "ai_ml": 0,
            "overall": 0
        }

        # GPU heavily influences gaming and AI
        if "gpu" in comp_map:
            gpu = comp_map["gpu"]
            scores["gaming"] += (gpu.gaming_score or 0) * 0.6
            scores["ai_ml"] += (gpu.ai_score or 0) * 0.7
            scores["productivity"] += (gpu.productivity_score or 0) * 0.3

        # CPU influences all workloads
        if "cpu" in comp_map:
            cpu = comp_map["cpu"]
            scores["gaming"] += (cpu.gaming_score or 0) * 0.3
            scores["ai_ml"] += (cpu.ai_score or 0) * 0.2
            scores["productivity"] += (cpu.productivity_score or 0) * 0.5

        # RAM influences productivity and AI
        if "ram" in comp_map:
            ram = comp_map["ram"]
            ram_capacity = ram.specs.get("capacity_gb", 0) if ram.specs else 0
            ram_score = min(ram_capacity / 32 * 100, 100)  # Normalize to 32GB
            scores["productivity"] += ram_score * 0.2
            scores["ai_ml"] += ram_score * 0.1

        # Calculate overall score
        scores["overall"] = (
            scores["gaming"] * 0.33 +
            scores["productivity"] * 0.33 +
            scores["ai_ml"] * 0.34
        )

        # Get use-case specific score
        use_case_score = scores.get(use_case, scores["overall"])

        result = {
            "use_case": use_case,
            "use_case_score": use_case_score,
            "all_scores": scores,
            "rating": "excellent" if use_case_score >= 80 else "good" if use_case_score >= 60 else "fair"
        }

        logger.info(f"Performance rating for {use_case}: {use_case_score:.1f}")
        return str(result)

    except Exception as e:
        logger.error(f"Error rating performance: {str(e)}")
        return f"Error: {str(e)}"
    finally:
        db.close()

