"""Extract component specifications from names and descriptions."""
import re
from typing import Dict, Optional, Any


def extract_cpu_specs(name: str, description: str = "") -> Dict[str, Any]:
    """Extract CPU specifications."""
    text = f"{name} {description}".lower()
    specs = {}
    
    # Socket type
    sockets = {
        "lga1700": "LGA1700",
        "lga1200": "LGA1200",
        "lga1151": "LGA1151",
        "am5": "AM5",
        "am4": "AM4",
        "am3": "AM3+",
    }
    for key, value in sockets.items():
        if key in text:
            specs["socket_type"] = value
            break
    
    # Core count
    core_match = re.search(r'(\d+)\s*(?:core|cores)', text)
    if core_match:
        specs["cores"] = int(core_match.group(1))
    
    # Thread count
    thread_match = re.search(r'(\d+)\s*(?:thread|threads)', text)
    if thread_match:
        specs["threads"] = int(thread_match.group(1))
    
    # Clock speed
    ghz_match = re.search(r'(\d+\.?\d*)\s*ghz', text)
    if ghz_match:
        specs["base_clock_ghz"] = float(ghz_match.group(1))
    
    # TDP
    tdp_match = re.search(r'(\d+)\s*w(?:atts?)?', text)
    if tdp_match:
        specs["tdp_watts"] = int(tdp_match.group(1))
    
    return specs


def extract_gpu_specs(name: str, description: str = "") -> Dict[str, Any]:
    """Extract GPU specifications."""
    text = f"{name} {description}".lower()
    specs = {}
    
    # VRAM
    vram_patterns = [
        r'(\d+)\s*gb\s*vram',
        r'(\d+)\s*gb\s*gddr',
        r'(\d+)\s*go',  # French: gigaoctets
    ]
    for pattern in vram_patterns:
        match = re.search(pattern, text)
        if match:
            specs["vram_gb"] = int(match.group(1))
            break
    
    # Memory type
    if "gddr6" in text or "gd6" in text:
        specs["memory_type"] = "GDDR6"
    elif "gddr6x" in text:
        specs["memory_type"] = "GDDR6X"
    elif "gddr5" in text:
        specs["memory_type"] = "GDDR5"
    
    # TDP
    tdp_match = re.search(r'(\d+)\s*w(?:atts?)?', text)
    if tdp_match:
        specs["tdp_watts"] = int(tdp_match.group(1))
    
    return specs


def extract_motherboard_specs(name: str, description: str = "") -> Dict[str, Any]:
    """Extract motherboard specifications."""
    text = f"{name} {description}".lower()
    specs = {}
    
    # Socket type
    sockets = {
        "lga1700": "LGA1700",
        "lga1200": "LGA1200",
        "lga1151": "LGA1151",
        "am5": "AM5",
        "am4": "AM4",
    }
    for key, value in sockets.items():
        if key in text:
            specs["socket_type"] = value
            break
    
    # Chipset
    chipsets = ["b550", "x570", "b650", "x670", "z690", "z790", "b660", "h610"]
    for chipset in chipsets:
        if chipset in text:
            specs["chipset"] = chipset.upper()
            break
    
    # RAM type
    if "ddr5" in text:
        specs["ram_type"] = "DDR5"
    elif "ddr4" in text:
        specs["ram_type"] = "DDR4"
    elif "ddr3" in text:
        specs["ram_type"] = "DDR3"
    
    # RAM speed
    ram_speed_match = re.search(r'(\d+)\s*mhz', text)
    if ram_speed_match:
        specs["ram_speed"] = int(ram_speed_match.group(1))
    
    # Form factor
    form_factors = {
        "atx": "ATX",
        "matx": "mATX",
        "micro atx": "mATX",
        "itx": "ITX",
        "mini itx": "ITX",
    }
    for key, value in form_factors.items():
        if key in text:
            specs["form_factor"] = value
            break
    
    return specs


def extract_ram_specs(name: str, description: str = "") -> Dict[str, Any]:
    """Extract RAM specifications."""
    text = f"{name} {description}".lower()
    specs = {}
    
    # Capacity
    capacity_match = re.search(r'(\d+)\s*gb', text)
    if capacity_match:
        specs["capacity_gb"] = int(capacity_match.group(1))
    
    # RAM type
    if "ddr5" in text:
        specs["ram_type"] = "DDR5"
    elif "ddr4" in text:
        specs["ram_type"] = "DDR4"
    elif "ddr3" in text:
        specs["ram_type"] = "DDR3"
    
    # Speed
    speed_match = re.search(r'(\d+)\s*mhz', text)
    if speed_match:
        specs["ram_speed"] = int(speed_match.group(1))
    else:
        # Try DDR4-3200 format
        ddr_match = re.search(r'ddr[45][\-\s]*(\d+)', text)
        if ddr_match:
            specs["ram_speed"] = int(ddr_match.group(1))
    
    return specs


def extract_storage_specs(name: str, description: str = "") -> Dict[str, Any]:
    """Extract storage specifications."""
    text = f"{name} {description}".lower()
    specs = {}
    
    # Capacity
    capacity_match = re.search(r'(\d+)\s*(?:gb|tb)', text)
    if capacity_match:
        capacity = int(capacity_match.group(1))
        if "tb" in text:
            capacity *= 1000
        specs["capacity_gb"] = capacity
    
    # Type
    if "nvme" in text or "m.2" in text or "pcie" in text:
        specs["type"] = "NVMe SSD"
    elif "ssd" in text:
        specs["type"] = "SSD"
    elif "hdd" in text or "hard drive" in text:
        specs["type"] = "HDD"
    
    # Interface
    if "sata" in text:
        specs["interface"] = "SATA"
    elif "nvme" in text or "m.2" in text:
        specs["interface"] = "NVMe"
    
    return specs


def extract_psu_specs(name: str, description: str = "") -> Dict[str, Any]:
    """Extract PSU specifications."""
    text = f"{name} {description}".lower()
    specs = {}
    
    # Wattage
    wattage_match = re.search(r'(\d+)\s*w(?:atts?)?', text)
    if wattage_match:
        specs["wattage"] = int(wattage_match.group(1))
    
    # Efficiency rating
    if "80+ titanium" in text:
        specs["efficiency"] = "80+ Titanium"
    elif "80+ platinum" in text:
        specs["efficiency"] = "80+ Platinum"
    elif "80+ gold" in text:
        specs["efficiency"] = "80+ Gold"
    elif "80+ bronze" in text:
        specs["efficiency"] = "80+ Bronze"
    elif "80+ silver" in text:
        specs["efficiency"] = "80+ Silver"
    elif "80+" in text:
        specs["efficiency"] = "80+"
    
    return specs


def extract_case_specs(name: str, description: str = "") -> Dict[str, Any]:
    """Extract case specifications."""
    text = f"{name} {description}".lower()
    specs = {}
    
    # Form factor support
    form_factors = []
    if "atx" in text:
        form_factors.append("ATX")
    if "matx" in text or "micro atx" in text:
        form_factors.append("mATX")
    if "itx" in text or "mini itx" in text:
        form_factors.append("ITX")
    
    if form_factors:
        specs["form_factor"] = form_factors
    
    return specs


def extract_specs(component_type: str, name: str, description: str = "") -> Dict[str, Any]:
    """
    Extract specifications based on component type.
    
    Args:
        component_type: Type of component
        name: Component name
        description: Component description (optional)
        
    Returns:
        Dictionary of extracted specifications
    """
    extractors = {
        "cpu": extract_cpu_specs,
        "gpu": extract_gpu_specs,
        "motherboard": extract_motherboard_specs,
        "ram": extract_ram_specs,
        "storage": extract_storage_specs,
        "psu": extract_psu_specs,
        "case": extract_case_specs,
    }
    
    extractor = extractors.get(component_type.lower())
    if extractor:
        return extractor(name, description)
    
    return {}

