# Build Locally

## Quick Start

```bash
cd phonics_app
chmod +x build_apk.sh
./build_apk.sh
```

## Prerequisites

### 1. Install Flutter

**macOS:**
```bash
brew install flutter
```

**Windows:**
Download from [flutter.dev](https://docs.flutter.dev/get-started/install/windows)

**Linux:**
```bash
sudo snap install flutter --classic
```

### 2. Install Android Studio

- Download from [developer.android.com/studio](https://developer.android.com/studio)
- Install Android SDK (API 34+ for Fold 6 features)
- Accept licenses: `flutter doctor --android-licenses`

### 3. Verify Setup

```bash
flutter doctor
```

All green checkmarks = ready to build.

## Build Steps

### Option 1: Use the build script

```bash
cd phonics_app
chmod +x build_apk.sh
./build_apk.sh
```

### Option 2: Manual build

```bash
cd phonics_app

# Get dependencies
flutter pub get

# Generate code (Hive adapters, etc.)
flutter pub run build_runner build --delete-conflicting-outputs

# Build release APK
flutter build apk --release
```

## Output

APK location:
```
build/app/outputs/flutter-apk/app-release.apk
```

## Install to Device

### Via Flutter:
```bash
flutter install
```

### Or manually:
1. Enable "Developer Options" on your Android device
2. Enable "USB Debugging"
3. Connect via USB
4. Copy APK to device and install

## Troubleshooting

### No Android SDK found
```bash
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/platform-tools
```

### Build fails on dependencies
```bash
flutter clean
flutter pub get
```

### Code generation issues
```bash
flutter pub run build_runner clean
flutter pub run build_runner build --delete-conflicting-outputs
```

## Samsung Fold 6 Testing

To test fold/unfold behaviors:

1. **Physical Device**: Just install and use
2. **Emulator**: 
   - Android Studio → Device Manager
   - Create device → Phone → "Galaxy Z Fold 5"
   - Use emulator toolbar to simulate hinge angle

## Build Variants

### Debug (faster, larger)
```bash
flutter build apk --debug
```

### Release (optimized, smaller)
```bash
flutter build apk --release
```

### App Bundle (for Play Store)
```bash
flutter build appbundle
```
