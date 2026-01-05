"""Parse component names to extract manufacturer and model."""
import re
from typing import Dict, Optional, Tuple

# Common manufacturers
MANUFACTURERS = {
    # CPU
    "intel": "Intel",
    "amd": "AMD",
    "ryzen": "AMD",
    "core": "Intel",
    "pentium": "Intel",
    "celeron": "Intel",
    "threadripper": "AMD",
    "epyc": "AMD",
    
    # GPU
    "nvidia": "NVIDIA",
    "geforce": "NVIDIA",
    "rtx": "NVIDIA",
    "gtx": "NVIDIA",
    "gt": "NVIDIA",
    "amd": "AMD",
    "radeon": "AMD",
    "rx": "AMD",
    
    # Motherboard
    "asus": "ASUS",
    "msi": "MSI",
    "gigabyte": "Gigabyte",
    "asus": "ASUS",
    "asrock": "ASRock",
    "evga": "EVGA",
    "biostar": "Biostar",
    
    # RAM
    "corsair": "Corsair",
    "g.skill": "G.Skill",
    "kingston": "Kingston",
    "crucial": "Crucial",
    "samsung": "Samsung",
    "hyperx": "HyperX",
    "team": "Team Group",
    "patriot": "Patriot",
    
    # Storage
    "samsung": "Samsung",
    "western digital": "Western Digital",
    "wd": "Western Digital",
    "seagate": "Seagate",
    "crucial": "Crucial",
    "intel": "Intel",
    "kingston": "Kingston",
    "sandisk": "SanDisk",
    "adata": "ADATA",
    
    # PSU
    "corsair": "Corsair",
    "seasonic": "Seasonic",
    "evga": "EVGA",
    "be quiet": "be quiet!",
    "cooler master": "Cooler Master",
    "thermaltake": "Thermaltake",
    "antec": "Antec",
    
    # Case
    "nzxt": "NZXT",
    "fractal design": "Fractal Design",
    "corsair": "Corsair",
    "cooler master": "Cooler Master",
    "lian li": "Lian Li",
    "phanteks": "Phanteks",
    "be quiet": "be quiet!",
}


def parse_component_name(name: str, component_type: str) -> Dict[str, Optional[str]]:
    """
    Parse component name to extract manufacturer and model.
    
    Args:
        name: Component name/title
        component_type: Type of component (cpu, gpu, etc.)
        
    Returns:
        Dictionary with manufacturer and model
    """
    if not name:
        return {"manufacturer": None, "model": None}
    
    name_lower = name.lower()
    manufacturer = None
    model = None
    
    # Try to find manufacturer
    for key, value in MANUFACTURERS.items():
        if key in name_lower:
            manufacturer = value
            break
    
    # Extract model number (common patterns)
    # For CPUs: Intel Core i5-12400, AMD Ryzen 5 5600X
    # For GPUs: RTX 3060, RX 6600 XT
    # For RAM: DDR4-3200, DDR5-6000
    # For Storage: 970 EVO, SN850
    
    if component_type == "cpu":
        # Pattern: Intel Core i5-12400, AMD Ryzen 5 5600X
        cpu_pattern = r'(?:Intel|AMD|Ryzen|Core|Pentium|Celeron|Threadripper|EPYC)\s+([A-Za-z0-9\-\s]+)'
        match = re.search(cpu_pattern, name, re.IGNORECASE)
        if match:
            model = match.group(1).strip()
    
    elif component_type == "gpu":
        # Pattern: RTX 3060, GTX 1660, RX 6600 XT
        gpu_pattern = r'(?:RTX|GTX|GT|RX|Radeon|GeForce)\s*([0-9]+(?:\s*[A-Z]+)?)'
        match = re.search(gpu_pattern, name, re.IGNORECASE)
        if match:
            model = match.group(1).strip()
    
    elif component_type == "motherboard":
        # Pattern: B550, X570, Z690, etc.
        mobo_pattern = r'([A-Z][0-9]+[A-Z]?[0-9]*)'
        match = re.search(mobo_pattern, name)
        if match:
            model = match.group(1)
    
    elif component_type == "ram":
        # Pattern: DDR4-3200, DDR5-6000
        ram_pattern = r'DDR[45][\-\s]*([0-9]+)'
        match = re.search(ram_pattern, name, re.IGNORECASE)
        if match:
            model = f"DDR{name_lower.count('ddr5') > 0 and '5' or '4'}-{match.group(1)}"
    
    elif component_type == "storage":
        # Pattern: 970 EVO, SN850, etc.
        storage_pattern = r'([A-Z0-9]+\s*[A-Z0-9]+)'
        match = re.search(storage_pattern, name)
        if match:
            model = match.group(1).strip()
    
    # If no specific pattern matched, try to extract model from name
    if not model:
        # Remove common words and extract remaining
        words = name.split()
        filtered = [w for w in words if w.lower() not in ['new', 'used', 'occasion', 'dzd', 'da', 'algeria']]
        if len(filtered) > 1:
            model = ' '.join(filtered[1:3])  # Take 2-3 words after first
    
    return {
        "manufacturer": manufacturer,
        "model": model or name[:100]  # Fallback to truncated name
    }

