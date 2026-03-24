#!/usr/bin/env python3
"""
Fingerprint generation utilities for browser stealth
"""

import random
import hashlib
from typing import Dict, Any, List


# Real browser user agents
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Screen resolutions
SCREEN_RESOLUTIONS = [
    {"width": 1920, "height": 1080, "deviceScaleFactor": 1},
    {"width": 1366, "height": 768, "deviceScaleFactor": 1},
    {"width": 1440, "height": 900, "deviceScaleFactor": 2},  # Retina
    {"width": 1536, "height": 864, "deviceScaleFactor": 1},
    {"width": 1280, "height": 720, "deviceScaleFactor": 1},
    {"width": 2560, "height": 1440, "deviceScaleFactor": 1},
    {"width": 1680, "height": 1050, "deviceScaleFactor": 1},
]

# WebGL vendors/renderers
WEBGL_FINGERPRINTS = [
    {"vendor": "Google Inc.", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"vendor": "Google Inc.", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"vendor": "Google Inc.", "renderer": "ANGLE (Intel, Intel(R) Iris(TM) Plus Graphics 640 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"vendor": "Apple Inc.", "renderer": "Apple GPU"},
]


def generate_fingerprint(seed: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a consistent browser fingerprint.
    
    Args:
        seed: Optional seed for reproducible fingerprints
    
    Returns:
        Dictionary with fingerprint attributes
    """
    if seed:
        random.seed(seed)
    
    ua = random.choice(USER_AGENTS)
    screen = random.choice(SCREEN_RESOLUTIONS)
    webgl = random.choice(WEBGL_FINGERPRINTS)
    
    # Generate consistent hardware specs
    hardware_concurrency = random.choice([2, 4, 8, 16])
    device_memory = random.choice([4, 8, 16, 32])
    
    fingerprint = {
        "user_agent": ua,
        "viewport": {
            "width": screen["width"],
            "height": screen["height"],
            "device_scale_factor": screen["deviceScaleFactor"]
        },
        "webgl": webgl,
        "hardware_concurrency": hardware_concurrency,
        "device_memory": device_memory,
        "languages": ["en-US", "en"],
        "platform": "Win32" if "Windows" in ua else "MacIntel",
        "color_depth": 24,
        "pixel_ratio": screen["deviceScaleFactor"],
    }
    
    # Generate fingerprint hash
    fp_string = f"{ua}{screen['width']}{screen['height']}{webgl['renderer']}"
    fingerprint["hash"] = hashlib.md5(fp_string.encode()).hexdigest()[:16]
    
    return fingerprint


def get_chrome_version(ua: str) -> str:
    """Extract Chrome version from UA string."""
    import re
    match = re.search(r'Chrome/(\d+\.\d+\.\d+\.\d+)', ua)
    return match.group(1) if match else "120.0.0.0"


def generate_navigator_props(fingerprint: Dict) -> str:
    """Generate JavaScript to override navigator properties."""
    return f"""
    Object.defineProperty(navigator, 'userAgent', {{
        get: () => '{fingerprint['user_agent']}'
    }});
    Object.defineProperty(navigator, 'platform', {{
        get: () => '{fingerprint['platform']}'
    }});
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {fingerprint['hardware_concurrency']}
    }});
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => {fingerprint['device_memory']}
    }});
    Object.defineProperty(navigator, 'languages', {{
        get: () => {str(fingerprint['languages'])}
    }});
    """
