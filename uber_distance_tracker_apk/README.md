# Uber Distance Tracker - APK Build Instructions

## Quick Option: Use PWA (No Build Required!)

The easiest way is to use the **Progressive Web App (PWA)** version:

1. **Open** `index.html` in any modern browser on Android
2. **Tap "Add to Home Screen"** when prompted (or use browser menu)
3. **Works offline** and tracks distance just like a native app!
4. **No installation needed** - works immediately

**Advantages:**
- ✅ Works right now, no building needed
- ✅ Installable like a native app
- ✅ Works offline
- ✅ GPS tracking works in background
- ✅ Updates automatically

---

## Option 2: Build APK (Android Studio Required)

If you need a true APK file, follow these steps:

### Prerequisites

1. **Install Android Studio** from https://developer.android.com/studio
2. **Install Android SDK** (comes with Android Studio)
3. **Set up JAVA_HOME** environment variable

### Build Steps

```bash
# 1. Open Android Studio
# 2. Select "Open an existing project"
# 3. Navigate to: uber_distance_tracker_apk/android
# 4. Wait for Gradle sync to complete

# 5. Build APK:
#    Menu → Build → Build Bundle(s) / APK(s) → Build APK(s)

# 6. Find APK at:
#    android/app/build/outputs/apk/debug/app-debug.apk
#    or
#    android/app/build/outputs/apk/release/app-release.apk (if signed)
```

### Alternative: Command Line Build

```bash
# Navigate to android folder
cd uber_distance_tracker_apk/android

# Make gradlew executable (Linux/Mac)
chmod +x gradlew

# Build debug APK
./gradlew assembleDebug

# Build release APK (requires signing)
./gradlew assembleRelease

# Output location:
# app/build/outputs/apk/debug/app-debug.apk
```

---

## Option 3: Online Build Service (Easiest APK)

Use a free online service to convert the PWA to APK:

### Method A: PWABuilder (Recommended)

1. Go to https://www.pwabuilder.com/
2. Enter your PWA URL (or upload files)
3. Click "Package for Stores"
4. Select "Android"
5. Download the APK

### Method B: Website2APK

1. Go to https://websitetoapk.com/ or similar
2. Upload the `index.html` file
3. Configure app name and icon
4. Download APK

---

## Project Structure

```
uber_distance_tracker_apk/
├── android/                          # Android project
│   ├── app/
│   │   ├── build.gradle             # App build config
│   │   └── src/
│   │       └── main/
│   │           ├── AndroidManifest.xml
│   │           ├── java/com/ubertracker/
│   │           │   └── MainActivity.java
│   │           └── res/
│   │               ├── layout/
│   │               │   └── activity_main.xml
│   │               └── values/
│   │                   ├── strings.xml
│   │                   └── styles.xml
│   ├── build.gradle                 # Project build config
│   └── settings.gradle
├── assets/                          # Web app files
│   ├── index.html                   # Main app
│   ├── manifest.json                # PWA manifest
│   └── sw.js                        # Service worker
└── README.md                        # This file
```

---

## Features

### Core Features
- ✅ **One-tap start/stop** for trips
- ✅ **Real-time distance tracking** using GPS
- ✅ **Trip history** with date, time, distance
- ✅ **Statistics dashboard** (total km, trip count)
- ✅ **Works offline** - no internet needed
- ✅ **Background tracking** - continues when phone locked

### Technical
- **GPS Accuracy:** High accuracy mode
- **Distance Calculation:** Haversine formula
- **Storage:** localStorage (SQLite for APK version)
- **Update Frequency:** Every position change (filtered for 5m+ movement)

---

## Permissions Required

The APK requires these permissions:
- **Location** - To track driving distance
- **Internet** - For PWA functionality (optional)

---

## Troubleshooting

### "App not installed"
- Enable "Install from Unknown Sources" in Android settings
- Make sure APK is not corrupted

### "Location not working"
- Grant location permission when prompted
- Enable GPS/Location services
- Allow location "All the time" (not just when using app)

### "Distance not accurate"
- GPS works best outdoors with clear sky view
- Tall buildings can interfere with signal
- Wait for GPS lock before starting (icon stops blinking)

---

## Recommendation

**For your coworker:** Use the **PWA version** first:

1. Copy `index.html` to their phone
2. Open in Chrome
3. Tap "Add to Home Screen"
4. Done! Works like a native app

If they absolutely need an APK file, use **PWABuilder** (Option 3) - it's free and takes 2 minutes.

---

## Support

If you need help building the APK:
1. Try the PWA version first (works immediately)
2. Use PWABuilder for quick APK generation
3. Or install Android Studio and follow Option 2
