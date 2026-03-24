---
name: captcha-solver
description: Solve image and audio CAPTCHAs using free tools. Use when encountering text-based image CAPTCHAs, math CAPTCHAs, simple puzzle CAPTCHAs, or audio CAPTCHAs. Supports OCR with Tesseract, audio transcription with Whisper, and preprocessing for distorted text. Works on local images, URLs, or browser screenshots.
---

# CAPTCHA Solver

Solve common CAPTCHA types using free, local tools.

## Quick Start

### Image CAPTCHAs

**Text/Number CAPTCHAs:**
```python
from scripts import solve_image_captcha
result = solve_image_captcha("captcha.png")
print(result["text"])  # Extracted text
```

**With preprocessing (for distorted text):**
```python
result = solve_image_captcha(
    "captcha.png", 
    preprocess=True,
    enhance=True
)
```

**Math CAPTCHAs ("3 + 5 = ?"):**
```python
from scripts import solve_math_captcha
result = solve_math_captcha("math_captcha.png")
print(result["answer"])  # Computed result
```

### Audio CAPTCHAs

```python
from scripts import solve_audio_captcha
result = solve_audio_captcha("captcha.mp3")
print(result["text"])  # Transcribed text
```

**From URL:**
```python
result = solve_audio_captcha("https://site.com/captcha.mp3", from_url=True)
```

## Advanced Usage

### Browser Integration

Use with stealth-browser skill to capture and solve CAPTCHAs:

```python
# 1. Navigate to page with CAPTCHA
# 2. Screenshot the CAPTCHA element
# 3. Solve it
from scripts import solve_image_captcha
result = solve_image_captcha("/tmp/captcha_screenshot.png")
```

### Custom Preprocessing

For challenging CAPTCHAs, adjust preprocessing:

```python
result = solve_image_captcha(
    "hard_captcha.png",
    preprocess=True,
    threshold=150,      # Binarization threshold (0-255)
    denoise=True,       # Remove noise
    resize_factor=2     # Upscale 2x before OCR
)
```

## Supported Formats

**Images:** PNG, JPG, JPEG, GIF, BMP, WebP
**Audio:** MP3, WAV, OGG, FLAC, M4A

## Dependencies

Install required packages:
```bash
pip install pytesseract pillow SpeechRecognition openai-whisper requests numpy opencv-python-headless
```

Install Tesseract OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

## Limitations

- **Image CAPTCHAs:** Works best on text/number CAPTCHAs. Complex puzzles, image grids ("select all cars"), or advanced distortions may fail.
- **Audio CAPTCHAs:** Requires clear audio. Background noise or heavy distortion reduces accuracy.
- **reCAPTCHA/hCaptcha:** These enterprise CAPTCHAs require different strategies. See stealth-browser skill for handling approaches.

## CLI Usage

```bash
# Image CAPTCHA
python3 scripts/solve_image_captcha.py captcha.png

# Audio CAPTCHA
python3 scripts/solve_audio_captcha.py captcha.mp3

# Math CAPTCHA
python3 scripts/solve_math_captcha.py math.png
```
