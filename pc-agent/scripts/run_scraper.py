"""Manual script to run Ouedkniss scraper."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from app.scrapers.ouedkniss_scraper import OuedknissScraper
from app.db.database import SessionLocal
from app.db.models import Component, ComponentType, Condition
import structlog

logger = structlog.get_logger()


def scrape_and_save(component_type: str, max_pages: int = 5, wilaya: str = None):
    """
    Scrape components and save to database.
    
    Args:
        component_type: Type of component to scrape
        max_pages: Maximum number of pages to scrape
        wilaya: Filter by wilaya (optional)
    """
    logger.info(f"Starting scrape for {component_type}, max_pages={max_pages}")
    
    scraper = OuedknissScraper()
    db = SessionLocal()
    
    try:
        # Scrape components
        components_data = scraper.scrape_category(
            component_type=component_type,
            max_pages=max_pages,
            wilaya=wilaya
        )
        
        logger.info(f"Scraped {len(components_data)} components")
        
        saved_count = 0
        updated_count = 0
        
        for comp_data in components_data:
            try:
                # Check if component already exists
                existing = db.query(Component).filter(
                    Component.name == comp_data["name"],
                    Component.source_url == comp_data.get("source_url")
                ).first()
                
                if existing:
                    # Update existing component
                    existing.price_dzd = comp_data["price_dzd"]
                    existing.in_stock = True
                    existing.last_scraped_at = db.func.now()
                    updated_count += 1
                else:
                    # Create new component
                    component = Component(
                        component_type=ComponentType(comp_data["component_type"]),
                        name=comp_data["name"],
                        price_dzd=comp_data["price_dzd"],
                        original_price=comp_data.get("original_price"),
                        condition=Condition(comp_data.get("condition", "new")),
                        in_stock=True,
                        source_url=comp_data.get("source_url"),
                        source_platform=comp_data.get("source_platform", "ouedkniss"),
                        seller_location=comp_data.get("seller_location"),
                        last_scraped_at=db.func.now()
                    )
                    db.add(component)
                    saved_count += 1
                
                db.commit()
                
            except Exception as e:
                logger.error(f"Error saving component: {str(e)}")
                db.rollback()
                continue
        
        logger.info(f"Saved {saved_count} new components, updated {updated_count} existing")
        return saved_count, updated_count
        
    except Exception as e:
        logger.error(f"Error in scrape_and_save: {str(e)}")
        return 0, 0
    finally:
        db.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Scrape PC components from Ouedkniss")
    parser.add_argument(
        "component_type",
        choices=["gpu", "cpu", "motherboard", "ram", "storage", "psu", "case", "cooling", "all"],
        help="Type of component to scrape"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Maximum number of pages to scrape (default: 5)"
    )
    parser.add_argument(
        "--wilaya",
        type=str,
        default=None,
        help="Filter by wilaya (optional)"
    )
    
    args = parser.parse_args()
    
    if args.component_type == "all":
        component_types = ["gpu", "cpu", "motherboard", "ram", "storage", "psu", "case", "cooling"]
        total_saved = 0
        total_updated = 0
        
        for comp_type in component_types:
            saved, updated = scrape_and_save(comp_type, args.pages, args.wilaya)
            total_saved += saved
            total_updated += updated
        
        logger.info(f"Total: {total_saved} saved, {total_updated} updated")
    else:
        saved, updated = scrape_and_save(args.component_type, args.pages, args.wilaya)
        logger.info(f"Results: {saved} saved, {updated} updated")


if __name__ == "__main__":
    main()

