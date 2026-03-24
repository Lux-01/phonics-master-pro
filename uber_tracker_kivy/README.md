# Uber Distance Tracker - Native Android APK

## 🎯 Overview

This is a **truly native Android app** built with Kivy (Python). It creates a real APK file that runs natively on Android - no HTML, no WebView, no PWA.

## 📱 Features

- ✅ **Native Android APK** - Not a web wrapper
- ✅ **Real-time GPS tracking** - Using Android's native GPS APIs
- ✅ **Background operation** - Continues tracking when app minimized
- ✅ **Offline storage** - SQLite database for trip history
- ✅ **Professional UI** - Material Design-inspired interface
- ✅ **One-tap operation** - Start/stop with single button

## 🔧 Build Options

### Option 1: Buildozer (Recommended)

**Requirements:**
- Linux or macOS (Windows via WSL)
- Python 3.7+
- ~10GB free space

**Steps:**

```bash
# 1. Install buildozer
pip3 install buildozer

# 2. Install Android dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libffi-dev libssl-dev libsqlite3-dev

# 3. Navigate to project
cd uber_tracker_kivy

# 4. Initialize buildozer (first time only)
buildozer init

# 5. Build debug APK
buildozer android debug

# 6. Find APK at:
# ./bin/ubertracker-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

**Build time:** 20-40 minutes (first build, downloads SDK/NDK)

### Option 2: Docker Build (No Local Setup)

**Requirements:**
- Docker installed

**Steps:**

```bash
# 1. Run buildozer in Docker
docker run --rm -v $(pwd):/home/user/hostcwd kivy/buildozer android debug

# 2. APK will be in ./bin/
```

### Option 3: GitHub Actions (Cloud Build)

Create `.github/workflows/build.yml`:

```yaml
name: Build APK

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install buildozer
          sudo apt-get update
          sudo apt-get install -y git zip unzip openjdk-17-jdk
      
      - name: Build APK
        run: buildozer android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: apk
          path: bin/*.apk
```

Push to GitHub and download the APK from Actions tab.

### Option 4: Google Colab (Free Cloud Build)

Use this notebook in Google Colab:

```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Install dependencies
!apt update
!apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libffi-dev libssl-dev

# Install buildozer
!pip3 install buildozer

# Copy your project
!cp -r /content/drive/MyDrive/uber_tracker_kivy /content/
%cd /content/uber_tracker_kivy

# Build APK
!buildozer android debug

# Copy APK back to Drive
!cp bin/*.apk /content/drive/MyDrive/
```

### Option 5: Rent a Build Server

Services that build APKs for you:

1. **Buildozer Cloud** (if available)
2. **AWS EC2** - Rent Ubuntu instance, build, download APK
3. **DigitalOcean Droplet** - $5/month, build APK in cloud

## 📋 Technical Details

### Architecture

```
Kivy (Python UI Framework)
    ↓
Pyjnius (Java bridge)
    ↓
Android SDK/NDK
    ↓
APK (Native Android app)
```

### File Structure

```
uber_tracker_kivy/
├── main.py              # Main application code
├── buildozer.spec       # Build configuration
└── README.md            # This file
```

### Dependencies

- **Kivy** - UI framework
- **Pyjnius** - Access Android Java APIs from Python
- **Plyer** - Platform-independent APIs (GPS, etc.)

### Android Permissions

- `ACCESS_FINE_LOCATION` - Precise GPS
- `ACCESS_COARSE_LOCATION` - Network location
- `INTERNET` - For maps (optional)
- `WAKE_LOCK` - Keep CPU awake while tracking

## 🚀 Installation

### On Android Device

1. Enable "Unknown Sources" in Settings → Security
2. Transfer APK to phone
3. Tap APK to install
4. Grant location permissions when prompted

### Via ADB

```bash
adb install bin/ubertracker-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

## 🎨 Customization

### Change Colors

Edit `main.py`:
```python
# Primary color (blue)
Color(0.153, 0.431, 0.945, 1)  # RGB values 0-1

# Success color (green)
background_color=(0.02, 0.58, 0.31, 1)

# Error color (red)
background_color=(0.882, 0.098, 0, 1)
```

### Change App Name

Edit `buildozer.spec`:
```ini
title = Your App Name
package.name = yourappname
package.domain = com.yourcompany
```

### Add Icon

1. Create `icon.png` (512x512)
2. Add to `buildozer.spec`:
```ini
icon.filename = icon.png
```

## 🔍 How It Works

### GPS Tracking

1. App requests location permissions
2. Uses Android's `LocationManager` via Pyjnius
3. Receives GPS updates every 3 seconds or 10 meters
4. Calculates distance using Haversine formula
5. Stores data in JSON file (can be upgraded to SQLite)

### Distance Calculation

```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c
```

### Data Storage

- Trips stored in `trips.json`
- Each trip has: start_time, end_time, distance, positions[]
- Persists between app restarts

## 🐛 Troubleshooting

### Build fails with "SDK not found"

```bash
# Buildozer will download SDK automatically on first run
# Or specify path:
export ANDROIDSDK=/path/to/android-sdk
export ANDROIDNDK=/path/to/android-ndk
```

### GPS not working

1. Check permissions granted in Android Settings
2. Ensure GPS is enabled
3. Test outdoors (GPS doesn't work well indoors)

### App crashes on start

```bash
# Check logs
buildozer android logcat

# Or via adb
adb logcat | grep python
```

### APK too large

Default Kivy APK is ~50MB. To reduce:
- Use `android.archs = arm64-v8a` (single architecture)
- Remove unused dependencies
- Use release build: `buildozer android release`

## 📊 Comparison: Kivy vs PWA vs React Native

| Feature | Kivy (This) | PWA | React Native |
|---------|-------------|-----|--------------|
| **APK Size** | ~50MB | N/A | ~30MB |
| **Native Performance** | ✅ Yes | ❌ No | ✅ Yes |
| **Background GPS** | ✅ Yes | ⚠️ Limited | ✅ Yes |
| **Offline Storage** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Build Complexity** | Medium | Low | Medium |
| **App Store Ready** | ✅ Yes | ❌ No | ✅ Yes |
| **Code Language** | Python | JavaScript | JavaScript |

## 🎓 Learning Resources

- **Kivy:** https://kivy.org/doc/stable/
- **Buildozer:** https://buildozer.readthedocs.io/
- **Pyjnius:** https://pyjnius.readthedocs.io/
- **Android GPS:** https://developer.android.com/reference/android/location/LocationManager

## 💡 Why Kivy?

**Pros:**
- Python (easier than Java/Kotlin)
- True native APK
- Cross-platform (Android, iOS, Desktop)
- Full Android API access via Pyjnius
- No web technologies

**Cons:**
- Larger APK size
- Slower startup than native Java
- Smaller community than React Native

## 📞 Support

If you need help building:
1. Try Google Colab (Option 4) - easiest, free
2. Use Docker (Option 2) - no local setup
3. Ask on Kivy Discord: https://chat.kivy.org/

---

**Ready to build!** Choose Option 1 (local), Option 2 (Docker), or Option 4 (Google Colab) to get your APK.
