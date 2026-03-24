#!/usr/bin/env python3
"""
Solve math-based CAPTCHAs (e.g., "3 + 5 = ?", "12 - 7")
"""

import argparse
import sys
import re
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("Install: pip install pytesseract pillow")
    print("Also install Tesseract OCR system package")
    sys.exit(1)


def solve_math_captcha(image_path, preprocess=True):
    """
    Extract and solve math expression from CAPTCHA.
    
    Args:
        image_path: Path to CAPTCHA image
        preprocess: Apply image preprocessing
    
    Returns:
        dict: {"expression": str, "answer": int/float, "success": bool}
    """
    try:
        # Load and preprocess image
        img = Image.open(image_path)
        
        if preprocess:
            # Convert to grayscale and enhance
            img = img.convert('L')
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
        
        # OCR with digit whitelist
        text = pytesseract.image_to_string(
            img, 
            config="--psm 7 -c tessedit_char_whitelist=0123456789+-x*/= "
        )
        
        # Clean text
        text = text.strip().replace("x", "*").replace("X", "*")
        
        # Extract math expression
        # Match patterns like "3 + 5", "12-7", "8*2", etc.
        pattern = r'(\d+)\s*([+\-*/])\s*(\d+)'
        match = re.search(pattern, text)
        
        if not match:
            return {
                "expression": text,
                "answer": None,
                "success": False,
                "error": "Could not parse math expression"
            }
        
        num1, operator, num2 = match.groups()
        num1, num2 = int(num1), int(num2)
        
        # Calculate
        if operator == '+':
            answer = num1 + num2
        elif operator == '-':
            answer = num1 - num2
        elif operator == '*':
            answer = num1 * num2
        elif operator == '/':
            answer = num1 / num2 if num2 != 0 else None
        else:
            answer = None
        
        expression = f"{num1} {operator} {num2}"
        
        return {
            "expression": expression,
            "answer": answer,
            "success": answer is not None,
            "raw_text": text
        }
    
    except Exception as e:
        return {
            "expression": "",
            "answer": None,
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Solve math CAPTCHA")
    parser.add_argument("image", help="Path to CAPTCHA image")
    parser.add_argument("--no-preprocess", action="store_true", 
                       help="Skip preprocessing")
    
    args = parser.parse_args()
    
    result = solve_math_captcha(args.image, preprocess=not args.no_preprocess)
    
    if result["success"]:
        print(f"Expression: {result['expression']}")
        print(f"Answer: {result['answer']}")
    else:
        print(f"Failed: {result.get('error', 'Unknown error')}")
        print(f"Raw OCR: {result.get('raw_text', 'N/A')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
