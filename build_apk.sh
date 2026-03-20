#!/bin/bash

# PhonicsMaster Pro - Build Script
# Run this on your local machine with Flutter installed

set -e

echo "=========================================="
echo "PhonicsMaster Pro - APK Builder"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Flutter
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}Error: Flutter not found in PATH${NC}"
    echo "Please install Flutter: https://docs.flutter.dev/get-started/install"
    exit 1
fi

echo -e "${GREEN}✓ Flutter found${NC}"
flutter --version
echo ""

# Doctor check
echo -e "${YELLOW}Running Flutter Doctor...${NC}"
flutter doctor
echo ""

# Get dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
flutter pub get
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Generate code if needed (Hive adapters, Riverpod)
echo -e "${YELLOW}Checking for code generation...${NC}"
if grep -q "build_runner" pubspec.yaml; then
    echo "Running build_runner..."
    flutter pub run build_runner build --delete-conflicting-outputs
    echo -e "${GREEN}✓ Code generated${NC}"
else
    echo "No code generation needed"
fi
echo ""

# Build APK
echo -e "${YELLOW}Building release APK...${NC}"
echo "This may take a few minutes..."
echo ""
flutter build apk --release

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "APK Location:"
echo "  build/app/outputs/flutter-apk/app-release.apk"
echo ""
echo "To install on your device:"
echo "  flutter install"
echo ""
echo "Or manually copy the APK to your Android device"
echo ""
