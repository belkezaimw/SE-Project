"""Initialize database with tables and seed data."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import engine, Base, SessionLocal
from app.db.models import Component, ComponentType, Condition, CompatibilityRule
import structlog

logger = structlog.get_logger()


def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def seed_compatibility_rules():
    """Seed basic compatibility rules."""
    logger.info("Seeding compatibility rules...")
    
    db = SessionLocal()
    
    try:
        rules = [
            {
                "component_type_1": ComponentType.CPU,
                "component_type_2": ComponentType.MOTHERBOARD,
                "rule_type": "socket_match",
                "rule_logic": {
                    "field_1": "socket_type",
                    "field_2": "socket_type",
                    "operator": "equals"
                },
                "description": "CPU and Motherboard must have matching socket types"
            },
            {
                "component_type_1": ComponentType.RAM,
                "component_type_2": ComponentType.MOTHERBOARD,
                "rule_type": "ram_type_match",
                "rule_logic": {
                    "field_1": "ram_type",
                    "field_2": "ram_type",
                    "operator": "equals"
                },
                "description": "RAM and Motherboard must support the same RAM type (DDR4/DDR5)"
            },
            {
                "component_type_1": ComponentType.PSU,
                "component_type_2": ComponentType.GPU,
                "rule_type": "power_requirement",
                "rule_logic": {
                    "psu_field": "wattage",
                    "component_field": "tdp_watts",
                    "operator": "greater_than",
                    "multiplier": 1.3
                },
                "description": "PSU wattage must be 30% higher than total system TDP"
            },
            {
                "component_type_1": ComponentType.MOTHERBOARD,
                "component_type_2": ComponentType.CASE,
                "rule_type": "form_factor_match",
                "rule_logic": {
                    "field_1": "form_factor",
                    "field_2": "form_factor",
                    "operator": "compatible"
                },
                "description": "Motherboard form factor must fit in case"
            }
        ]
        
        for rule_data in rules:
            rule = CompatibilityRule(**rule_data)
            db.add(rule)
        
        db.commit()
        logger.info(f"Seeded {len(rules)} compatibility rules")
        
    except Exception as e:
        logger.error(f"Error seeding compatibility rules: {str(e)}")
        db.rollback()
    finally:
        db.close()


def seed_sample_components():
    """Seed sample components for testing."""
    logger.info("Seeding sample components...")
    
    db = SessionLocal()
    
    try:
        sample_components = [
            # Sample GPUs
            {
                "component_type": ComponentType.GPU,
                "name": "NVIDIA RTX 4060 Ti 8GB",
                "manufacturer": "NVIDIA",
                "model": "RTX 4060 Ti",
                "price_dzd": 85000,
                "condition": Condition.NEW,
                "in_stock": True,
                "source_platform": "ouedkniss",
                "seller_location": "Alger",
                "specs": {"vram": "8GB", "memory_type": "GDDR6"},
                "benchmark_score": 75,
                "gaming_score": 80,
                "productivity_score": 70,
                "ai_score": 75,
                "tdp_watts": 160
            },
            {
                "component_type": ComponentType.GPU,
                "name": "AMD RX 6700 XT 12GB",
                "manufacturer": "AMD",
                "model": "RX 6700 XT",
                "price_dzd": 72000,
                "condition": Condition.USED,
                "in_stock": True,
                "source_platform": "ouedkniss",
                "seller_location": "Oran",
                "specs": {"vram": "12GB", "memory_type": "GDDR6"},
                "benchmark_score": 72,
                "gaming_score": 78,
                "productivity_score": 68,
                "ai_score": 70,
                "tdp_watts": 230
            },
            # Sample CPUs
            {
                "component_type": ComponentType.CPU,
                "name": "AMD Ryzen 5 5600X",
                "manufacturer": "AMD",
                "model": "Ryzen 5 5600X",
                "price_dzd": 35000,
                "condition": Condition.NEW,
                "in_stock": True,
                "source_platform": "ouedkniss",
                "seller_location": "Alger",
                "specs": {"cores": 6, "threads": 12, "base_clock": "3.7GHz"},
                "benchmark_score": 70,
                "gaming_score": 75,
                "productivity_score": 72,
                "ai_score": 68,
                "socket_type": "AM4",
                "tdp_watts": 65
            },
            {
                "component_type": ComponentType.CPU,
                "name": "Intel Core i5-12400F",
                "manufacturer": "Intel",
                "model": "i5-12400F",
                "price_dzd": 32000,
                "condition": Condition.NEW,
                "in_stock": True,
                "source_platform": "ouedkniss",
                "seller_location": "Constantine",
                "specs": {"cores": 6, "threads": 12, "base_clock": "2.5GHz"},
                "benchmark_score": 72,
                "gaming_score": 76,
                "productivity_score": 74,
                "ai_score": 70,
                "socket_type": "LGA1700",
                "tdp_watts": 65
            }
        ]
        
        for comp_data in sample_components:
            component = Component(**comp_data)
            db.add(component)
        
        db.commit()
        logger.info(f"Seeded {len(sample_components)} sample components")
        
    except Exception as e:
        logger.error(f"Error seeding sample components: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting database initialization...")
    create_tables()
    seed_compatibility_rules()
    seed_sample_components()
    logger.info("Database initialization completed!")

