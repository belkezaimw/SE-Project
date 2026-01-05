"""Celery tasks for web scraping."""
from typing import List
import structlog
from sqlalchemy.orm import Session
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.scrapers.ouedkniss_scraper import OuedknissScraper
from app.db.database import SessionLocal
from app.db.models import Component, ComponentType, Condition
from app.core.cache import invalidate_cache
from app.utils.name_parser import parse_component_name
from app.utils.spec_extractor import extract_specs
from app.utils.benchmark_calculator import calculate_benchmark_scores

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.scraper_tasks.scrape_all_components")
def scrape_all_components():
    """
    Scrape all component types from Ouedkniss.
    Scheduled to run daily.
    """
    logger.info("Starting daily component scraping")
    
    scraper = OuedknissScraper()
    component_types = ["gpu", "cpu", "motherboard", "ram", "storage", "psu", "case", "cooling"]
    
    total_scraped = 0
    
    for comp_type in component_types:
        try:
            count = scrape_component_type(comp_type, max_pages=10)
            total_scraped += count
            logger.info(f"Scraped {count} {comp_type} components")
        except Exception as e:
            logger.error(f"Error scraping {comp_type}: {str(e)}")
    
    # Invalidate component cache
    invalidate_cache("components")
    
    logger.info(f"Daily scraping completed. Total: {total_scraped} components")
    return {"total_scraped": total_scraped}


def scrape_component_type(component_type: str, max_pages: int = 5) -> int:
    """
    Scrape a specific component type and save to database.
    
    Args:
        component_type: Type of component to scrape
        max_pages: Maximum pages to scrape
        
    Returns:
        Number of components scraped
    """
    scraper = OuedknissScraper()
    db = SessionLocal()
    
    try:
        # Scrape components
        components_data = scraper.scrape_category(component_type, max_pages=max_pages)
        
        saved_count = 0
        
        for comp_data in components_data:
            try:
                # Check if component already exists (by name and price)
                existing = db.query(Component).filter(
                    Component.name == comp_data["name"],
                    Component.price_dzd == comp_data["price_dzd"]
                ).first()
                
                # Parse component name to extract manufacturer and model
                name_data = parse_component_name(comp_data["name"], comp_data["component_type"])
                
                # Extract specifications
                description = comp_data.get("description", "")
                specs = extract_specs(comp_data["component_type"], comp_data["name"], description)
                
                # Calculate benchmark scores
                scores = calculate_benchmark_scores(
                    comp_data["component_type"],
                    comp_data["name"],
                    specs
                )
                
                # Extract compatibility data from specs
                socket_type = specs.get("socket_type")
                ram_type = specs.get("ram_type")
                ram_speed = specs.get("ram_speed")
                tdp_watts = specs.get("tdp_watts")
                form_factor = specs.get("form_factor")
                
                if existing:
                    # Update existing component
                    existing.in_stock = True
                    existing.last_scraped_at = datetime.utcnow()
                    existing.price_dzd = comp_data["price_dzd"]
                    existing.manufacturer = name_data.get("manufacturer") or existing.manufacturer
                    existing.model = name_data.get("model") or existing.model
                    existing.specs = specs or existing.specs
                    existing.benchmark_score = scores.get("benchmark_score") or existing.benchmark_score
                    existing.gaming_score = scores.get("gaming_score") or existing.gaming_score
                    existing.productivity_score = scores.get("productivity_score") or existing.productivity_score
                    existing.ai_score = scores.get("ai_score") or existing.ai_score
                    if socket_type:
                        existing.socket_type = socket_type
                    if ram_type:
                        existing.ram_type = ram_type
                    if ram_speed:
                        existing.ram_speed = ram_speed
                    if tdp_watts:
                        existing.tdp_watts = tdp_watts
                    if form_factor:
                        existing.form_factor = form_factor
                else:
                    # Create new component
                    component = Component(
                        component_type=ComponentType(comp_data["component_type"]),
                        name=comp_data["name"],
                        manufacturer=name_data.get("manufacturer"),
                        model=name_data.get("model"),
                        price_dzd=comp_data["price_dzd"],
                        original_price=comp_data.get("original_price"),
                        condition=Condition(comp_data.get("condition", "new")),
                        in_stock=True,
                        source_url=comp_data.get("source_url"),
                        source_platform=comp_data.get("source_platform", "ouedkniss"),
                        seller_location=comp_data.get("seller_location"),
                        specs=specs,
                        benchmark_score=scores.get("benchmark_score"),
                        gaming_score=scores.get("gaming_score"),
                        productivity_score=scores.get("productivity_score"),
                        ai_score=scores.get("ai_score"),
                        socket_type=socket_type,
                        ram_type=ram_type,
                        ram_speed=ram_speed,
                        tdp_watts=tdp_watts,
                        form_factor=form_factor,
                        last_scraped_at=datetime.utcnow()
                    )
                    db.add(component)
                    saved_count += 1
                
                db.commit()
                
            except Exception as e:
                logger.error(f"Error saving component: {str(e)}")
                db.rollback()
                continue
        
        logger.info(f"Saved {saved_count} new {component_type} components")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error in scrape_component_type: {str(e)}")
        return 0
    finally:
        db.close()


@celery_app.task(name="app.tasks.scraper_tasks.update_component_prices")
def update_component_prices():
    """
    Update prices for existing components.
    Scheduled to run hourly.
    """
    logger.info("Starting hourly price update")
    
    # Quick scrape of first page for each category to update prices
    component_types = ["gpu", "cpu", "motherboard", "ram", "storage", "psu"]
    
    total_updated = 0
    
    for comp_type in component_types:
        try:
            count = scrape_component_type(comp_type, max_pages=2)
            total_updated += count
        except Exception as e:
            logger.error(f"Error updating {comp_type} prices: {str(e)}")
    
    # Invalidate cache
    invalidate_cache("components")
    
    logger.info(f"Price update completed. Updated: {total_updated}")
    return {"total_updated": total_updated}


@celery_app.task(name="app.tasks.scraper_tasks.mark_out_of_stock")
def mark_out_of_stock():
    """
    Mark components as out of stock if not seen in recent scrapes.
    """
    db = SessionLocal()
    
    try:
        # Mark components not scraped in last 48 hours as out of stock
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=48)
        
        updated = db.query(Component).filter(
            Component.last_scraped_at < cutoff,
            Component.in_stock == True
        ).update({"in_stock": False})
        
        db.commit()
        
        logger.info(f"Marked {updated} components as out of stock")
        return {"marked_out_of_stock": updated}
        
    except Exception as e:
        logger.error(f"Error marking out of stock: {str(e)}")
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

