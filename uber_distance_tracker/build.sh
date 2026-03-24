#!/bin/bash

# Uber Distance Tracker - Build Script
# This script builds the Flutter app for Android

echo "=========================================="
echo "Uber Distance Tracker - Build Script"
echo "=========================================="
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not found!"
    echo "Please install Flutter from: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -1)"
echo ""

# Get dependencies
echo "📦 Getting dependencies..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "❌ Failed to get dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Build APK
echo "🔨 Building APK (Release)..."
flutter build apk --release

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Build Successful!"
echo "=========================================="
echo ""
echo "APK Location:"
echo "  build/app/outputs/flutter-apk/app-release.apk"
echo ""
echo "Install on device:"
echo "  flutter install"
echo ""
echo "Or manually transfer the APK to your phone"
echo ""

# Optional: Build App Bundle
echo "📦 Building App Bundle (for Play Store)..."
flutter build appbundle --release

if [ $? -eq 0 ]; then
    echo ""
    echo "AAB Location:"
    echo "  build/app/outputs/bundle/release/app-release.aab"
fi

echo ""
echo "Done! 🎉"
