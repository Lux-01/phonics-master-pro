#!/usr/bin/env python3
"""
CAPTCHA Solver Module - Convenience imports
"""

from .solve_image_captcha import solve_image_captcha
from .solve_audio_captcha import solve_audio_captcha
from .solve_math_captcha import solve_math_captcha

__all__ = ["solve_image_captcha", "solve_audio_captcha", "solve_math_captcha"]
