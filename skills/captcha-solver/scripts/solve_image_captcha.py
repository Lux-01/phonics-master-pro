#!/usr/bin/env python3
"""
Solve image-based text CAPTCHAs using OCR.
Supports preprocessing for distorted text.
"""

import argparse
import sys
import os
import re
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
    import pytesseract
    import numpy as np
    import cv2
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install: pip install pytesseract pillow numpy opencv-python-headless")
    print("Also install Tesseract OCR system package")
    sys.exit(1)


def preprocess_image(img_path, threshold=150, denoise=True, resize_factor=1):
    """
    Preprocess CAPTCHA image for better OCR.
    
    Args:
        img_path: Path to image file
        threshold: Binarization threshold (0-255)
        denoise: Apply noise reduction
        resize_factor: Upscale factor before OCR
    
    Returns:
        PIL.Image: Processed image
    """
    # Load image
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Could not load image: {img_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # Denoise if requested
    if denoise:
        binary = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
    
    # Resize if requested
    if resize_factor > 1:
        height, width = binary.shape
        binary = cv2.resize(binary, (width * resize_factor, height * resize_factor), 
                           interpolation=cv2.INTER_CUBIC)
    
    # Convert back to PIL
    pil_img = Image.fromarray(binary)
    
    return pil_img


def solve_image_captcha(image_path, preprocess=True, enhance=True, 
                        threshold=150, denoise=True, resize_factor=2,
                        ocr_config="--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    """
    Solve image CAPTCHA using OCR.
    
    Args:
        image_path: Path to CAPTCHA image
        preprocess: Apply image preprocessing
        enhance: Apply contrast enhancement
        threshold: Binarization threshold
        denoise: Remove noise
        resize_factor: Upscale factor
        ocr_config: Tesseract OCR configuration
    
    Returns:
        dict: {"text": str, "confidence": float, "success": bool}
    """
    try:
        if preprocess:
            img = preprocess_image(image_path, threshold, denoise, resize_factor)
        else:
            img = Image.open(image_path)
        
        if enhance:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
        
        # Run OCR
        text = pytesseract.image_to_string(img, config=ocr_config)
        
        # Clean result
        text = text.strip().replace(" ", "").replace("\n", "")
        
        # Get confidence
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        confidences = [int(c) for c in data["conf"] if int(c) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "text": text,
            "confidence": avg_confidence,
            "success": len(text) > 0,
            "method": "tesseract_ocr"
        }
    
    except Exception as e:
        return {
            "text": "",
            "confidence": 0,
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Solve image CAPTCHA")
    parser.add_argument("image", help="Path to CAPTCHA image")
    parser.add_argument("--no-preprocess", action="store_true", help="Skip preprocessing")
    parser.add_argument("--threshold", type=int, default=150, help="Binarization threshold")
    parser.add_argument("--resize", type=int, default=2, help="Resize factor")
    
    args = parser.parse_args()
    
    result = solve_image_captcha(
        args.image,
        preprocess=not args.no_preprocess,
        threshold=args.threshold,
        resize_factor=args.resize
    )
    
    if result["success"]:
        print(f"CAPTCHA text: {result['text']}")
        print(f"Confidence: {result['confidence']:.1f}%")
    else:
        print(f"Failed to solve CAPTCHA: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
