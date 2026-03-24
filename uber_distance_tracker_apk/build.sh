#!/bin/bash

# Uber Distance Tracker APK Builder
# This script attempts to build the APK if Android SDK is available

echo "=========================================="
echo "Uber Distance Tracker - APK Builder"
echo "=========================================="
echo ""

# Check for Android SDK
if [ -z "$ANDROID_SDK_ROOT" ] && [ -z "$ANDROID_HOME" ]; then
    echo "⚠️  Android SDK not found!"
    echo ""
    echo "To build the APK, you need:"
    echo "1. Android Studio installed"
    echo "2. ANDROID_SDK_ROOT environment variable set"
    echo ""
    echo "Quick alternatives:"
    echo ""
    echo "Option 1 - Use PWA (Easiest):"
    echo "  Just open index.html in a browser on Android"
    echo "  Tap 'Add to Home Screen'"
    echo "  Works like a native app!"
    echo ""
    echo "Option 2 - Online Builder (2 minutes):"
    echo "  1. Go to https://www.pwabuilder.com/"
    echo "  2. Upload the index.html file"
    echo "  3. Download Android APK"
    echo ""
    echo "Option 3 - Install Android Studio:"
    echo "  1. Download from https://developer.android.com/studio"
    echo "  2. Open the 'android' folder in Android Studio"
    echo "  3. Build → Build APK"
    echo ""
    exit 1
fi

# Check for gradle
cd android

if [ ! -f "gradlew" ]; then
    echo "⚠️  Gradle wrapper not found!"
    echo "Please open this project in Android Studio first"
    echo "to initialize the Gradle wrapper."
    exit 1
fi

# Build
echo "🔨 Building APK..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "APK location:"
    echo "  android/app/build/outputs/apk/debug/app-debug.apk"
    echo ""
    echo "Install on device:"
    echo "  adb install android/app/build/outputs/apk/debug/app-debug.apk"
    echo ""
else
    echo ""
    echo "❌ Build failed!"
    echo "Please check the error messages above."
    exit 1
fi
