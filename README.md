# PhonicsMaster Pro

A beautiful, interactive phonics learning app for Samsung Fold 6 and other Android devices.

## Features

- **Interactive Lessons**: Progressive phonics curriculum from single letters to complex words
- **S Pen Support**: Practice letter tracing with stroke validation and feedback
- **Fold 6 Optimized**: Adaptive layouts for folded (cover screen) and unfolded (tablet) modes
- **Audio Learning**: High-quality pronunciation guides and word sounds
- **Progress Tracking**: Detailed stats, streaks, achievements, and skill breakdowns
- **Gamification**: Stars, badges, and rewards to keep learners engaged
- **Dyslexia-Friendly**: OpenDyslexic font, high contrast modes, and accessibility features
- **Offline-First**: Core lessons work without internet connection

## Screenshots

- Splash Screen with animated mascot
- Home Dashboard with progress overview
- Lesson Screen with interactive steps
- Practice Mode with word building
- Letter Tracing with S Pen support
- Library with lesson browser
- Progress Dashboard with stats
- Settings for customization

## Prerequisites

- Flutter 3.19+ (SDK >=3.0.0 <4.0.0)
- Android Studio or VS Code with Flutter extension
- Android SDK (API 34+ for Fold 6 features)
- Git

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phonics_app
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Generate Hive adapters** (if needed)
   ```bash
   flutter pub run build_runner build
   ```

## Build

### Debug Build
```bash
flutter build apk --debug
```

### Release Build
```bash
flutter build apk --release
```

### App Bundle (for Play Store)
```bash
flutter build appbundle
```

## Run

### On Emulator
```bash
flutter emulators --launch <emulator-id>
flutter run
```

### On Physical Device
```bash
flutter devices
flutter run -d <device-id>
```

## Samsung Fold 6 Testing

### Emulator Setup
1. Open Android Studio → Device Manager
2. Create Device → Phone → "Galaxy Z Fold 5" (closest available)
3. Or use Foldable emulator with hinge sensor simulation

### Physical Device Testing
- Test both folded (cover screen) and unfolded (main screen) states
- Verify S Pen functionality on unfolded mode
- Check layout transitions during fold/unfold
- Test multi-window mode

### Fold States
- **Folded**: Cover screen layout with large touch targets
- **Unfolded**: Full tablet experience with S Pen tracing
- **Flex Mode**: Supported for hands-free learning

## Project Structure

```
lib/
├── core/
│   └── theme/
│       └── app_theme.dart          # App-wide theming
├── data/
│   ├── models/                      # Data models
│   │   ├── lesson.dart
│   │   ├── phonics_letter.dart
│   │   ├── user_progress.dart
│   │   └── word_tile.dart
│   ├── repositories/                # Data access layer
│   │   ├── audio_repository.dart
│   │   ├── lesson_repository.dart
│   │   └── progress_repository.dart
│   └── services/                    # Business logic
│       ├── audio_service.dart
│       └── database_service.dart
├── presentation/
│   ├── providers/                   # Riverpod state management
│   │   ├── audio_provider.dart
│   │   ├── lesson_provider.dart
│   │   └── settings_provider.dart
│   ├── screens/                   # UI screens
│   │   ├── splash_screen.dart
│   │   ├── home_screen.dart
│   │   ├── lesson_screen.dart
│   │   ├── practice_screen.dart
│   │   ├── letter_tracing_screen.dart
│   │   ├── library_screen.dart
│   │   ├── progress_screen.dart
│   │   └── settings_screen.dart
│   └── widgets/                   # Reusable components
│       ├── letter_card.dart
│       └── progress_bar.dart
└── main.dart                      # Entry point
```

## Dependencies

- **flutter_riverpod**: State management
- **just_audio + audio_service**: Audio playback
- **hive**: Local database
- **rive**: Animations
- **confetti**: Celebration effects
- **google_fonts**: Typography
- **speech_to_text**: Pronunciation practice
- **firebase_core + analytics + crashlytics**: Analytics and crash reporting

## Curriculum Levels

1. **Level 1**: Single Letters (Ages 4-5) - 26 letters and sounds
2. **Level 2**: CVC Words (Ages 5-6) - Consonant-Vowel-Consonant patterns
3. **Level 3**: Digraphs (Ages 6-7) - sh, ch, th, wh, ph, long vowels
4. **Level 4**: Advanced (Ages 7-8) - Trigraphs, silent letters, multi-syllable words

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or feature requests, please open an issue on the repository.

---

Built with ❤️ using Flutter and Riverpod
