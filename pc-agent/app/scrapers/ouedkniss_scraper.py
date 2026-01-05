"""Ouedkniss.dz scraper for PC components."""
import re
import time
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
import requests
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class OuedknissScraper:
    """Scraper for Ouedkniss.dz marketplace."""
    
    BASE_URL = settings.OUEDKNISS_BASE_URL
    HEADERS = {
        "User-Agent": settings.SCRAPER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-DZ,fr;q=0.9,ar-DZ;q=0.8,ar;q=0.7,en;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    
    # Category mappings for PC components
    CATEGORIES = {
        "gpu": "informatique/composants-pc/cartes-graphiques",
        "cpu": "informatique/composants-pc/processeurs",
        "motherboard": "informatique/composants-pc/cartes-meres",
        "ram": "informatique/composants-pc/memoires-ram",
        "storage": "informatique/composants-pc/disques-durs-ssd",
        "psu": "informatique/composants-pc/alimentations",
        "case": "informatique/composants-pc/boitiers",
        "cooling": "informatique/composants-pc/refroidissement",
    }
    
    def __init__(self):
        """Initialize scraper."""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def scrape_category(
        self, 
        component_type: str, 
        max_pages: int = 5,
        wilaya: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape a component category from Ouedkniss.
        
        Args:
            component_type: Type of component (gpu, cpu, etc.)
            max_pages: Maximum number of pages to scrape
            wilaya: Filter by wilaya (optional)
            
        Returns:
            List of component dictionaries
        """
        if component_type not in self.CATEGORIES:
            logger.error(f"Unknown component type: {component_type}")
            return []
        
        category_path = self.CATEGORIES[component_type]
        components = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.BASE_URL}/{category_path}?page={page}"
                if wilaya:
                    url += f"&wilaya={wilaya}"
                
                logger.info(f"Scraping {component_type} page {page}: {url}")
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                page_components = self._parse_listing_page(response.text, component_type)
                components.extend(page_components)
                
                logger.info(f"Found {len(page_components)} components on page {page}")
                
                # Respect rate limiting
                time.sleep(settings.SCRAPER_DELAY_SECONDS)
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {str(e)}")
                continue
        
        logger.info(f"Total {component_type} components scraped: {len(components)}")
        return components
    
    def _parse_listing_page(self, html: str, component_type: str) -> List[Dict[str, Any]]:
        """Parse a listing page and extract component data."""
        soup = BeautifulSoup(html, "html.parser")
        components = []
        
        # Try multiple selector patterns for Ouedkniss
        # Common patterns: article tags, divs with specific classes
        selectors = [
            "article",
            ".announce-card",
            ".listing-card",
            ".classified-card",
            ".item-card",
            "[data-id]",
            ".product-item",
        ]
        
        listings = []
        for selector in selectors:
            listings = soup.select(selector)
            if listings:
                logger.debug(f"Found listings using selector: {selector}")
                break
        
        if not listings:
            # Fallback: try to find any link that might be a listing
            listings = soup.select("a[href*='/store/'], a[href*='/annonce/']")
        
        for listing in listings:
            try:
                component = self._parse_listing_item(listing, component_type)
                if component:
                    components.append(component)
            except Exception as e:
                logger.warning(f"Error parsing listing: {str(e)}")
                continue
        
        return components
    
    def _parse_listing_item(self, listing, component_type: str) -> Optional[Dict[str, Any]]:
        """Parse a single listing item."""
        try:
            # Extract title - try multiple selectors
            title_elem = listing.select_one(
                ".title, .announce-title, h2, h3, h4, .name, [data-title], .product-title"
            )
            if not title_elem:
                # Try getting text from the listing itself
                title = listing.get_text(strip=True)[:200]  # Limit length
                if not title or len(title) < 5:
                    return None
            else:
                title = title_elem.get_text(strip=True)
            
            # Extract price - try multiple selectors
            price_elem = listing.select_one(
                ".price, .announce-price, .prix, [data-price], .product-price, .amount"
            )
            if not price_elem:
                # Try to find price in text
                price_text = None
                listing_text = listing.get_text()
                price_match = re.search(r'(\d+[\s,\.]*\d*)\s*(?:DA|DZD|د\.ج)', listing_text, re.IGNORECASE)
                if price_match:
                    price_text = price_match.group(0)
            else:
                price_text = price_elem.get_text(strip=True)
            
            if not price_text:
                return None
            
            price_dzd = self._extract_price_dzd(price_text)
            if not price_dzd or price_dzd <= 0:
                return None
            
            # Extract location
            location_elem = listing.select_one(
                ".location, .wilaya, .localisation, .city, [data-location]"
            )
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract URL
            link_elem = listing.select_one("a[href]")
            if not link_elem:
                # If listing itself is a link
                if listing.name == "a" and listing.get("href"):
                    link_elem = listing
                else:
                    link_elem = listing.find_parent("a")
            
            url = None
            if link_elem:
                url = link_elem.get("href")
                if url and not url.startswith("http"):
                    url = f"{self.BASE_URL}{url}" if url.startswith("/") else f"{self.BASE_URL}/{url}"
            
            # Extract condition (new/used)
            condition_text = listing.get_text().lower()
            condition = "used" if any(word in condition_text for word in ["occasion", "used", "مستعمل", "usagé"]) else "new"
            
            # Extract description if available
            desc_elem = listing.select_one(".description, .desc, .details, .summary")
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            return {
                "name": title,
                "price_dzd": price_dzd,
                "original_price": price_text,
                "condition": condition,
                "seller_location": location,
                "source_url": url,
                "source_platform": "ouedkniss",
                "component_type": component_type,
                "description": description,
            }
            
        except Exception as e:
            logger.warning(f"Error parsing item: {str(e)}")
            return None
    
    def _extract_price_dzd(self, price_text: str) -> Optional[float]:
        """Extract numeric price in DZD from price string."""
        # Remove common currency symbols and text
        price_text = price_text.replace("DA", "").replace("DZD", "").replace("د.ج", "")
        price_text = price_text.replace(",", "").replace(" ", "")
        
        # Extract numeric value
        match = re.search(r"(\d+(?:\.\d+)?)", price_text)
        if match:
            return float(match.group(1))
        return None

