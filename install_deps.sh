#!/bin/bash
# Install dependencies using --break-system-packages
# WARNING: This bypasses the externally-managed-environment check

set -e

echo "Installing Python packages (using --break-system-packages)..."
echo "WARNING: This modifies the system Python environment"
echo ""

python3 -m pip install --break-system-packages pillow pytesseract SpeechRecognition openai-whisper requests numpy opencv-python-headless pydub playwright playwright-stealth fake-useragent

echo ""
echo "Installing Playwright browsers..."
python3 -m playwright install chromium

echo ""
echo "=========================================="
echo "System packages still needed (run with sudo):"
echo "  sudo apt-get install -y tesseract-ocr ffmpeg"
echo "=========================================="
echo ""
echo "Python packages installed successfully!"
