"""API routes for PC build recommendation system."""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
import structlog
import json
import re

from app.db.database import get_db
from app.db.models import Component, ComponentType
from app.schemas.request import BuildRequest, ComponentQuery, CompatibilityCheckRequest
from app.schemas.response import (
    BuildRecommendation,
    ComponentListResponse,
    ComponentResponse,
    CompatibilityCheckResponse,
    HealthResponse,
    ErrorResponse
)
from app.agent.pc_agent import PCBuildAgent
from app.core.cache import cached, cache
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

# Initialize agent (singleton)
_agent_instance = None


def get_agent() -> PCBuildAgent:
    """Get or create agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PCBuildAgent()
    return _agent_instance


def detect_locale(accept_language: Optional[str] = Header(None)) -> str:
    """Detect locale from Accept-Language header."""
    if not accept_language:
        return settings.DEFAULT_LOCALE

    # Parse Accept-Language header
    languages = accept_language.lower().split(",")
    for lang in languages:
        lang_code = lang.split(";")[0].strip()[:2]
        if lang_code in settings.SUPPORTED_LOCALES:
            return lang_code

    return settings.DEFAULT_LOCALE


@router.post(
    "/recommend",
    response_model=BuildRecommendation,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def recommend_pc_build(
    request: BuildRequest,
    db: Session = Depends(get_db),
    agent: PCBuildAgent = Depends(get_agent)
):
    """
    Generate a PC build recommendation based on budget and use case.

    This endpoint uses an LLM-powered agent to intelligently select and
    validate PC components from the Algerian market.
    """
    try:
        logger.info(
            f"Build request: {request.budget_dzd} DZD, {request.use_case}, locale: {request.locale}"
        )

        # Generate recommendation using agent
        result = agent.recommend_build(
            budget_dzd=request.budget_dzd,
            use_case=request.use_case.value,
            locale=request.locale.value,
            preferences=request.preferences
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to generate recommendation")
            )

        # Parse agent output and construct BuildRecommendation response
        from app.parsers.agent_response_parser import parse_agent_response
        
        parsed_response = parse_agent_response(
            agent_output=result.get("recommendation", ""),
            budget_dzd=request.budget_dzd,
            use_case=request.use_case.value,
            locale=request.locale.value,
            db_session=db
        )
        
        if parsed_response:
            return parsed_response
        else:
            # Fallback: return error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse agent response"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in recommend_pc_build: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/components",
    response_model=ComponentListResponse
)
@cached(prefix="components", ttl=1800)  # Cache for 30 minutes
async def list_components(
    query: ComponentQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    List available PC components with filtering and pagination.
    """
    try:
        # Build query
        db_query = db.query(Component)

        if query.component_type:
            db_query = db_query.filter(Component.component_type == query.component_type)

        if query.search_term:
            search = f"%{query.search_term}%"
            db_query = db_query.filter(Component.name.ilike(search))

        if query.min_price_dzd:
            db_query = db_query.filter(Component.price_dzd >= query.min_price_dzd)

        if query.max_price_dzd:
            db_query = db_query.filter(Component.price_dzd <= query.max_price_dzd)

        if query.condition:
            db_query = db_query.filter(Component.condition == query.condition)

        if query.manufacturer:
            db_query = db_query.filter(Component.manufacturer == query.manufacturer)

        if query.in_stock_only:
            db_query = db_query.filter(Component.in_stock == True)

        # Get total count
        total = db_query.count()

        # Apply pagination
        components = db_query.offset(query.offset).limit(query.limit).all()

        return ComponentListResponse(
            components=[ComponentResponse.model_validate(c) for c in components],
            total=total,
            limit=query.limit,
            offset=query.offset
        )

    except Exception as e:
        logger.error(f"Error listing components: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/compatibility/check",
    response_model=CompatibilityCheckResponse
)
async def check_component_compatibility(
    request: CompatibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check compatibility between selected components.
    """
    try:
        from app.agent.tools import check_compatibility

        # Use the tool directly
        result_str = check_compatibility.invoke({"component_ids": request.component_ids})

        # Parse result (simplified - in production, parse properly)
        # TODO: Properly parse the tool output
        return CompatibilityCheckResponse(
            compatible=True,
            compatibility_score=100.0,
            issues=[],
            recommendations=[]
        )

    except Exception as e:
        logger.error(f"Error checking compatibility: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for monitoring.
    """
    health = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "llm": "unknown"
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health["database"] = "healthy"
    except Exception as e:
        health["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    # Check Redis
    try:
        if cache.redis_client:
            cache.redis_client.ping()
            health["redis"] = "healthy"
        else:
            health["redis"] = "disabled"
    except Exception as e:
        health["redis"] = f"unhealthy: {str(e)}"

    # Check LLM (basic check)
    try:
        agent = get_agent()
        health["llm"] = f"healthy ({settings.LLM_PROVIDER})"
    except Exception as e:
        health["llm"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    return HealthResponse(**health)
