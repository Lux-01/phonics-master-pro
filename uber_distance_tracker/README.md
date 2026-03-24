# Uber Distance Tracker

A professional, simple Android app for Uber drivers to track kilometers traveled per trip. Features a floating overlay widget so drivers can see their navigation app while tracking distance.

## Features

✅ **One-Tap Operation** - Start/stop tracking with a single button  
✅ **Floating Overlay** - Widget stays visible over other apps (maps, etc.)  
✅ **Background Tracking** - Continues even when phone is locked  
✅ **Professional UI** - Clean, modern Material Design 3  
✅ **Trip History** - View all past trips with details  
✅ **Distance Stats** - Total distance and trip count  
✅ **Offline First** - All data stored locally on device  
✅ **Battery Optimized** - Efficient GPS usage

## Screenshots

- Main screen with stats cards
- Active trip display with live distance
- Trip history list
- Detailed trip view
- Floating overlay widget (visible over maps)

## Technical Details

**Framework:** Flutter 3.x  
**Platform:** Android (API 21+)  
**Architecture:** Foreground Service + Overlay Window  
**Database:** SQLite (local storage)  
**Location:** GPS with 10-meter accuracy  
**Permissions:** Location (foreground + background), Overlay, Notifications

## Building the App

### Prerequisites

1. Install Flutter SDK (3.0 or higher)
2. Install Android Studio with Android SDK
3. Set up Android emulator or connect physical device

### Build Steps

```bash
# 1. Navigate to project directory
cd uber_distance_tracker

# 2. Get dependencies
flutter pub get

# 3. Build APK (for testing)
flutter build apk --release

# 4. Build App Bundle (for Play Store)
flutter build appbundle --release
```

### Output Location

- APK: `build/app/outputs/flutter-apk/app-release.apk`
- AAB: `build/app/outputs/bundle/release/app-release.aab`

## Installation

### Method 1: Direct APK Install
1. Transfer `app-release.apk` to Android phone
2. Enable "Install from Unknown Sources" in Settings
3. Tap APK file to install

### Method 2: Play Store (Future)
- Upload AAB to Google Play Console
- Follow Play Store publishing process

## Permissions Required

The app requires these permissions:

1. **Location (Always)** - To track distance while driving
2. **Display over other apps** - For floating overlay widget
3. **Notifications** - To show foreground service notification

## Usage Guide

### First Launch
1. Open app
2. Grant location permissions (Allow all the time)
3. Grant overlay permission (for floating button)
4. Grant notification permission

### Starting a Trip
1. Tap green "START TRIP" button
2. Floating widget appears (can be moved)
3. Drive normally with your map app
4. Distance updates automatically

### During Trip
- Floating widget shows live distance
- Widget stays on top of all apps
- Drag widget to reposition if needed
- App continues tracking even if phone locked

### Ending a Trip
1. Tap red "STOP TRIP" button (in app or floating widget)
2. Trip is saved automatically
3. View trip details in history

### Viewing History
- Main screen shows recent trips
- Tap any trip for detailed view
- See start/end times, duration, distance

## Architecture

```
lib/
├── main.dart                 # App entry point
├── models/
│   └── session.dart          # Trip data model
├── services/
│   ├── database_service.dart # SQLite storage
│   └── location_service.dart # GPS tracking
├── screens/
│   ├── home_screen.dart      # Main UI
│   └── session_detail_screen.dart # Trip details
└── overlay/
    └── overlay_widget.dart   # Floating button
```

## Key Features Explained

### Background Location Tracking
- Uses Android Foreground Service
- Notification shows "Tracking your trip..."
- Service cannot be killed by system
- GPS updates every 10 meters moved

### Floating Overlay Widget
- Stays visible over all apps
- Shows current distance
- One-tap start/stop
- Draggable to any position
- Semi-transparent design

### Distance Calculation
- Haversine formula for accuracy
- Filters GPS noise (5m minimum)
- Updates every 10 meters
- Handles GPS signal loss gracefully

## Customization

### Colors
Edit `lib/main.dart` theme:
```dart
Color(0xFF276EF1)  // Primary blue
Color(0xFF05944F)  // Success green
Color(0xFFE11900)  // Error red
```

### Distance Units
Edit `lib/screens/home_screen.dart`:
```dart
// Change km to miles
return '${(km * 0.621371).toStringAsFixed(2)} mi';
```

### Update Frequency
Edit `lib/services/location_service.dart`:
```dart
distanceFilter: 10,  // Change from 10 to 5 meters
```

## Troubleshooting

### App not tracking
- Check location permissions (must be "Allow all the time")
- Ensure GPS is enabled
- Disable battery optimization for app

### Overlay not showing
- Grant "Display over other apps" permission
- Restart app after granting permission

### Distance inaccurate
- GPS works best outdoors
- Tall buildings can affect accuracy
- Wait for GPS lock before starting

### App stops tracking
- Don't swipe away from recents
- Battery saver may kill app
- Add to "Don't optimize" list

## Privacy

- All data stored locally on device
- No internet connection required
- No data sent to servers
- Location history never leaves phone

## License

MIT License - Free for personal and commercial use

## Support

For issues or feature requests, contact the developer.

---

**Built with Flutter ❤️**
