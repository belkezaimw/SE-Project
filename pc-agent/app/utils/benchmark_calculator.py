"""Calculate benchmark scores for components."""
from typing import Dict, Optional, Any


# Base performance scores for common components (simplified - in production, use actual benchmark data)
CPU_SCORES = {
    # Intel
    "i9": {"base": 90, "gaming": 85, "productivity": 95, "ai": 80},
    "i7": {"base": 75, "gaming": 80, "productivity": 85, "ai": 70},
    "i5": {"base": 60, "gaming": 70, "productivity": 70, "ai": 55},
    "i3": {"base": 40, "gaming": 50, "productivity": 50, "ai": 35},
    # AMD
    "ryzen 9": {"base": 92, "gaming": 88, "productivity": 98, "ai": 85},
    "ryzen 7": {"base": 78, "gaming": 82, "productivity": 88, "ai": 75},
    "ryzen 5": {"base": 65, "gaming": 72, "productivity": 75, "ai": 60},
    "ryzen 3": {"base": 45, "gaming": 55, "productivity": 55, "ai": 40},
}

GPU_SCORES = {
    # NVIDIA RTX
    "rtx 4090": {"base": 100, "gaming": 100, "productivity": 95, "ai": 100},
    "rtx 4080": {"base": 90, "gaming": 95, "productivity": 90, "ai": 95},
    "rtx 4070": {"base": 75, "gaming": 85, "productivity": 75, "ai": 80},
    "rtx 4060": {"base": 60, "gaming": 70, "productivity": 60, "ai": 65},
    "rtx 3090": {"base": 95, "gaming": 95, "productivity": 90, "ai": 98},
    "rtx 3080": {"base": 85, "gaming": 90, "productivity": 85, "ai": 90},
    "rtx 3070": {"base": 70, "gaming": 80, "productivity": 70, "ai": 75},
    "rtx 3060": {"base": 55, "gaming": 65, "productivity": 55, "ai": 60},
    # NVIDIA GTX
    "gtx 1660": {"base": 40, "gaming": 50, "productivity": 35, "ai": 30},
    "gtx 1650": {"base": 30, "gaming": 40, "productivity": 25, "ai": 20},
    # AMD RX
    "rx 7900": {"base": 88, "gaming": 92, "productivity": 85, "ai": 75},
    "rx 7800": {"base": 75, "gaming": 82, "productivity": 70, "ai": 60},
    "rx 7700": {"base": 65, "gaming": 72, "productivity": 60, "ai": 50},
    "rx 6600": {"base": 50, "gaming": 60, "productivity": 45, "ai": 35},
    "rx 6500": {"base": 35, "gaming": 45, "productivity": 30, "ai": 25},
}


def calculate_cpu_scores(name: str, specs: Dict[str, Any]) -> Dict[str, float]:
    """Calculate CPU benchmark scores."""
    name_lower = name.lower()
    
    # Find matching CPU tier
    base_score = 50.0
    gaming_score = 50.0
    productivity_score = 50.0
    ai_score = 45.0
    
    for key, scores in CPU_SCORES.items():
        if key in name_lower:
            base_score = scores["base"]
            gaming_score = scores["gaming"]
            productivity_score = scores["productivity"]
            ai_score = scores["ai"]
            break
    
    # Adjust based on specs
    cores = specs.get("cores", 0)
    threads = specs.get("threads", 0)
    clock = specs.get("base_clock_ghz", 0)
    
    if cores > 0:
        # More cores = better for productivity and AI
        productivity_score += min(cores * 2, 20)
        ai_score += min(cores * 1.5, 15)
    
    if clock > 0:
        # Higher clock = better for gaming
        gaming_score += min((clock - 3.0) * 10, 15)
    
    # Cap scores at 100
    return {
        "benchmark_score": min(base_score, 100.0),
        "gaming_score": min(gaming_score, 100.0),
        "productivity_score": min(productivity_score, 100.0),
        "ai_score": min(ai_score, 100.0),
    }


def calculate_gpu_scores(name: str, specs: Dict[str, Any]) -> Dict[str, float]:
    """Calculate GPU benchmark scores."""
    name_lower = name.lower()
    
    # Find matching GPU model
    base_score = 40.0
    gaming_score = 45.0
    productivity_score = 40.0
    ai_score = 35.0
    
    for key, scores in GPU_SCORES.items():
        if key in name_lower:
            base_score = scores["base"]
            gaming_score = scores["gaming"]
            productivity_score = scores["productivity"]
            ai_score = scores["ai"]
            break
    
    # Adjust based on VRAM (important for AI)
    vram = specs.get("vram_gb", 0)
    if vram >= 24:
        ai_score += 20
    elif vram >= 16:
        ai_score += 15
    elif vram >= 12:
        ai_score += 10
    elif vram >= 8:
        ai_score += 5
    
    # Adjust based on memory type
    if specs.get("memory_type") == "GDDR6X":
        gaming_score += 5
        ai_score += 5
    
    # Cap scores at 100
    return {
        "benchmark_score": min(base_score, 100.0),
        "gaming_score": min(gaming_score, 100.0),
        "productivity_score": min(productivity_score, 100.0),
        "ai_score": min(ai_score, 100.0),
    }


def calculate_ram_scores(name: str, specs: Dict[str, Any]) -> Dict[str, float]:
    """Calculate RAM benchmark scores."""
    capacity = specs.get("capacity_gb", 0)
    speed = specs.get("ram_speed", 0)
    ram_type = specs.get("ram_type", "")
    
    # Base score on capacity
    base_score = min(capacity / 32 * 100, 100.0)
    
    # Speed bonus
    if ram_type == "DDR5":
        base_score += 10
    elif ram_type == "DDR4" and speed >= 3600:
        base_score += 5
    
    # Productivity benefits from more RAM
    productivity_score = min(capacity / 16 * 100, 100.0)
    
    # AI benefits from more RAM
    ai_score = min(capacity / 32 * 100, 100.0)
    
    return {
        "benchmark_score": min(base_score, 100.0),
        "gaming_score": min(base_score * 0.3, 100.0),  # RAM less important for gaming
        "productivity_score": min(productivity_score, 100.0),
        "ai_score": min(ai_score, 100.0),
    }


def calculate_storage_scores(name: str, specs: Dict[str, Any]) -> Dict[str, float]:
    """Calculate storage benchmark scores."""
    capacity = specs.get("capacity_gb", 0)
    storage_type = specs.get("type", "")
    
    # Base score on type
    if "NVMe" in storage_type:
        base_score = 80.0
    elif "SSD" in storage_type:
        base_score = 60.0
    else:
        base_score = 40.0
    
    # Capacity bonus
    if capacity >= 2000:  # 2TB+
        base_score += 10
    elif capacity >= 1000:  # 1TB+
        base_score += 5
    
    return {
        "benchmark_score": min(base_score, 100.0),
        "gaming_score": min(base_score * 0.8, 100.0),
        "productivity_score": min(base_score, 100.0),
        "ai_score": min(base_score * 0.7, 100.0),
    }


def calculate_psu_scores(name: str, specs: Dict[str, Any]) -> Dict[str, float]:
    """Calculate PSU benchmark scores."""
    wattage = specs.get("wattage", 0)
    efficiency = specs.get("efficiency", "")
    
    # Base score on wattage (more is generally better, but with diminishing returns)
    if wattage >= 1000:
        base_score = 90.0
    elif wattage >= 750:
        base_score = 80.0
    elif wattage >= 650:
        base_score = 70.0
    elif wattage >= 550:
        base_score = 60.0
    else:
        base_score = 50.0
    
    # Efficiency bonus
    if "Titanium" in efficiency:
        base_score += 10
    elif "Platinum" in efficiency:
        base_score += 8
    elif "Gold" in efficiency:
        base_score += 5
    elif "Bronze" in efficiency:
        base_score += 2
    
    return {
        "benchmark_score": min(base_score, 100.0),
        "gaming_score": min(base_score, 100.0),
        "productivity_score": min(base_score, 100.0),
        "ai_score": min(base_score, 100.0),
    }


def calculate_benchmark_scores(component_type: str, name: str, specs: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate benchmark scores for a component.
    
    Args:
        component_type: Type of component
        name: Component name
        specs: Component specifications
        
    Returns:
        Dictionary with benchmark_score, gaming_score, productivity_score, ai_score
    """
    calculators = {
        "cpu": calculate_cpu_scores,
        "gpu": calculate_gpu_scores,
        "ram": calculate_ram_scores,
        "storage": calculate_storage_scores,
        "psu": calculate_psu_scores,
    }
    
    calculator = calculators.get(component_type.lower())
    if calculator:
        return calculator(name, specs)
    
    # Default scores for unknown components
    return {
        "benchmark_score": 50.0,
        "gaming_score": 50.0,
        "productivity_score": 50.0,
        "ai_score": 50.0,
    }

