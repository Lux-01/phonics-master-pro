# PhonicsMaster Pro Project Structure

## Overview
A Flutter-based phonics learning app for children, teaching SATPIN methodology with proper CVC word blending.

## Architecture
- **Framework:** Flutter 3.19+
- **Target:** Android APK (minSdk 21)
- **State Management:** Provider + ChangeNotifier
- **Audio:** audioplayers package
- **Storage:** shared_preferences

## File Structure

### Core Files
- `lib/main.dart` - App entry point
- `lib/data/phonics_data.dart` - SATPIN curriculum data

### Services (Business Logic)
- `lib/services/audio_service.dart` - Audio playback
- `lib/services/storage_service.dart` - Local storage
- `lib/services/progress_service.dart` - Progress tracking

### Screens
- `lib/screens/splash_screen.dart` - Region selector
- `lib/screens/home_screen.dart` - Main menu
- `lib/screens/letter_lesson_screen.dart` - Letter lessons
- `lib/screens/word_builder_screen.dart` - CVC word games
- `lib/screens/progress_screen.dart` - Progress tracking

### Assets
- `assets/audio/` - Regional audio files
- `assets/images/` - Images and icons
- `assets/animations/` - Lottie animations

## SATPIN Curriculum
Phase 1: S-A-T-P-I-N (creates 20+ CVC words)
Phase 2: C-K-E-H-R-M-D

## Features
✨ SATPIN synthetic phonics methodology
🎯 Regional audio (AU/NZ/USA)
🧩 Word builder game
📊 Progress tracking with stars
🦜 Growing mascot
🔥 Daily streaks

## Build Instructions

### Development
```bash
flutter pub get
flutter run --debug
```

### APK Build
```bash
flutter build apk --release
```

### App Bundle (Play Store)
```bash
flutter build appbundle --release
```

## Audio Files Required
Place MP3 files in `assets/audio/{region}/

regions: au, nz, us
Format: {letter}.mp3 for sound, {word}.mp3 for words

## Customization
Edit `lib/data/phonics_data.dart` to modify curriculum or add phases.

## Credits
Built with ACA (Autonomous Code Architect) methodology
Research: SATPIN phonics methodology
Languages: Dart/Flutter
