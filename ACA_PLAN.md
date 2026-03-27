# PhonicsMaster Pro - ACA Planning Document

## Research Summary Applied
- **Methodology:** SATPIN order (S-A-T-P-I-N first)
- **Platform:** Flutter (Android APK primary)
- **Audio:** Regional packs (AU, NZ, USA)
- **Animations:** Lottie JSON + custom animal sprites
- **Design:** Glassmorphism + Neumorphism (2025 trends)
- **Gamification:** Streaks + mastery stars + progress tracking

---

## Step 1: Requirements Analysis

### Problem Statement
Build a phonics education app that teaches children to read using proper synthetic phonics methodology (SATPIN order), with engaging animations, games, and progress tracking.

### Inputs
- Child's region (AU/NZ/USA)
- Child's name (for personalization)
- Touch inputs (letter taps, word building)
- Audio playback requests

### Expected Outputs
- Phonics lessons in SATPIN order
- CVC word blending exercises
- Progress reports (stars per letter, streaks)
- Fun animations and rewards
- APK file for Android

### Constraints
- Must work offline (audio files bundled)
- Target Android SDK 21+ (Android 5.0+)
- No Firebase dependencies (previous build failures)
- Local storage for progress only
- Clean, distraction-free UI for 4-6 year olds

### Success Criteria
- Complete SATPIN → CKERHMD → GOU... progression
- Working CVC word builder (sat, pin, pat, tin, pan)
- Audio plays correctly for selected region
- Animations smooth at 30fps
- Progress persists across sessions
- APK < 50MB

---

## Step 2: Architecture Design

### Module Structure
```
lib/
├── main.dart                     # App entry
├── models/
│   ├── phonics_data.dart         # SATPIN curriculum data
│   ├── letter_model.dart         # Letter with metadata
│   ├── word_model.dart           # CVC word structure
│   └── progress_model.dart       # User progress tracking
├── screens/
│   ├── splash_screen.dart        # Logo + region selector
│   ├── letter_lesson_screen.dart # Single letter lesson
│   ├── word_builder_screen.dart  # CVC word building
│   ├── game_screen.dart          # Mini games
│   └── progress_screen.dart      # Stars + streaks
├── widgets/
│   ├── letter_card.dart          # Animated letter tile
│   ├── animal_mascot.dart        # Growing companion
│   ├── progress_badge.dart       # Star/streak display
│   ├── audio_button.dart         # Sound play button
│   └── word_slot.dart            # CVC drop zone
├── services/
│   ├── audio_service.dart        # TTS/playback manager
│   ├── storage_service.dart      # SharedPreferences wrapper
│   ├── animation_service.dart    # Lottie controller
│   └── progress_service.dart     # Learning tracker
├── games/
│   ├── letter_match_game.dart    # Memory game
│   ├── sound_sort_game.dart      # Sort by sound
│   └── word_chain_game.dart      # Build word chains
└── data/
    ├── satpin_phases.dart        # Phase definitions
    ├── cvc_words.dart            # SATPIN-compatible words
    └── animal_sounds.dart        # Letter-animal mappings
```

### Key Data Structures
```dart
// Letter with phases
class Letter {
  final String char;
  final String name;
  final int phase;
  final List<String> words;
  final Animal animal;
  final bool isVowel;
}

// Phase definition
class Phase {
  final int number;
  final List<Letter> letters;
  final List<String> trickyWords;
}

// CVC Word
class CVCWord {
  final String word;
  final String image;
  final String soundPath;
}

// Progress
class UserProgress {
  final String region;
  final Map<String, int> letterStars;  // letter -> 1-3
  final int currentStreakDays;
  final DateTime lastPractice;
  final List<String> masteredWords;
}
```

---

## Step 3: Data Flow

### Lesson Flow
1. User selects a letter or "Continue"
2. Screen loads with:
   - Letter displayed (animated)
   - Animal mascot visible
   - Audio buttons (letter sound, name, example words)
   - Progress indicator (stars earned)
3. User taps letter → hears sound
4. User swipes → next/previous letter
5. Complete → star earned, mascot grows
6. Save progress to local storage

### Word Builder Flow
1. Display CVC word picture
2. Three slots for C-V-C
3. Draggable letters at bottom
4. User drags letters to slots
5. "Sound it out" button plays each phoneme
6. "Blend" button plays full word
7. Correct → celebration animation

### Game Flow
1. Select game type
2. Load game data (randomized)
3. Track score in real-time
4. Show progress bar
5. End → stars earned, return to menu

---

## Step 4: Edge Cases

### Empty Inputs
- No stored region → show region selector
- No stored name → default to "Friend"
- No progress → start from Phase 1, Letter S

### Invalid States
- Audio file missing → show "🔈" icon disabled
- Corrupted progress → reset gracefully, backup to "sat"

### Large Data
- >100 CVC words → lazy load by phase
- Animation cache >50MB → purge old animations

### API Failures (if any)
- No network needed (offline design)
- External resources (images) → local fallbacks

### Rate Limits
- N/A (offline app)

### Timeouts
- Audio seek timeout → restart audio
- Animation load timeout → show static image

---

## Step 5: Tool Constraints

### Flutter Constraints
- Android min SDK 21 (Android 5.0)
- iOS 12+ compatibility (future)
- Package size <50MB preferred

### Audio Packages
- `audioplayers` (MIT, well-maintained)
  - Supports: WAV, MP3, OGG
  - Android: MediaPlayer
  - Limitation: iOS requires manual file path setup

### Animation Packages
- `lottie` (Apache 2.0)
  - Renders After Effects JSON
  - Android native (LottieAndroid)
  - Performance: GPU-accelerated
  - Limitation: Complex animations = larger files

### State Management
- `Provider` + `ChangeNotifier`
  - Simple, Flutter-native
  - No external dependencies
  - Scoped to widget tree

### Storage
- `shared_preferences`
  - Simple key-value
  - Async read/write
  - JSON encode/decode for complex objects

---

## Step 6: Error Handling

### Audio Errors
- File not found → log, disable button
- Playback error → retry once, then skip
- Permission denied (Android 6+) → request permission

### Animation Errors
- JSON parse error → show static PNG
- Memory pressure → dispose old animations
- Render failure → fallback to simple tween

### Storage Errors
- Read error → return default progress
- Write error → retry 3x, then log
- Disk full → show warning, allow continue without save

### Navigation Errors
- Unknown route → return to home
- Back button on first screen → confirm exit

### Input Validation
- Region: validate against list ["au", "nz", "us"]
- Name: max 20 chars, alphanumeric + spaces
- Progress: clamp stars 0-3, streak >= 0

---

## Step 7: Testing Plan

### Happy Path Tests
1. **Launch → Splash → Select AU → Home**
   - App opens, splash shows 2s
   - Region selector displays 3 options
   - Tap AU → navigate to home
   - AU audio set active

2. **Complete Letter S Lesson**
   - Tap letter S card
   - Hear "sss" sound
   - Hear "sun" example
   - Earn 3 stars
   - Mascot grows animation
   - Progress saved

3. **Build "sat" Word**
   - Navigate to Word Builder
   - Drag S, A, T to slots
   - Tap "sound it out" → hear each
   - Tap "blend" → hear "sat"
   - Success confetti animation

### Edge Case Tests
4. **No Region Stored**
   - Fresh install → force region select
   - Cannot skip
   - Stores selection

5. **Corrupted Progress**
   - Edit prefs to invalid JSON
   - Launch app → progress resets
   - Default to Phase 1 S
   - Log error

6. **Missing Audio File**
   - Delete assets/audio/au/s.mp3
   - Tap S letter
   - Button shows disabled state
   - No crash

### Performance Tests
7. **Rapid Navigation**
   - Tap 20 letters in 10 seconds
   - No memory leak
   - Animation smooth

8. **Large Word List**
   - Load 100 CVC words
   - Scroll smoothly
   - No jank

### Device Tests
9. **Android 5.0 (API 21)**
   - App launches
   - Audio plays
   - Animations work

10. **Low Memory Device**
    - Background 10 apps
    - App still launches
    - Animations degrade gracefully

---

## Implementation Phases

### Phase 1: Core (Week 1)
- [ ] Project setup (Flutter, dependencies)
- [ ] Splash screen + region selector
- [ ] Audio service (3 region support)
- [ ] Letter model + SATPIN data
- [ ] Basic letter lesson screen

### Phase 2: Learning (Week 2)
- [ ] All Phase 1 letters (S,A,T,P,I,N)
- [ ] CVC word builder
- [ ] Progress service + storage
- [ ] Stars + streaks

### Phase 3: Games (Week 3)
- [ ] Letter match game
- [ ] Sound sort game
- [ ] Mascot growth system
- [ ] Progress screen

### Phase 4: Polish (Week 4)
- [ ] Lottie animations
- [ ] Custom animal graphics
- [ ] Glassmorphism UI
- [ ] APK build + test

---

## File Assets Required

### Audio (per region)
```
assets/audio/{region}/
├── letters/
│   ├── s.mp3
│   ├── a.mp3
│   ├── ... all 26
├── words/
│   ├── sat.mp3
│   ├── pin.mp3
│   ├── ... all CVC
└── ui/
    ├── success.mp3
    ├── star.mp3
    └── mascot.mp3
```

### Images
```
assets/images/
├── animals/
│   ├── snake.png (S)
│   ├── ant.png (A)
│   ├── ... for SATPIN
├── words/
│   ├── sat.jpg
│   ├── pin.jpg
│   └── ...
└── ui/
    ├── mascot_base.png
    ├── mascot_stage2.png
    ├── mascot_stage3.png
    └── star_full.png, star_empty.png
```

### Animations
```
assets/animations/
├── letter_pop.json       # Letter tap animation
├── star_burst.json       # Success reward
├── mascot_eat.json       # Mascot growth
└── confetti.json         # Word built correctly
```

---

## Build Commands

### Development
```bash
flutter run --debug
```

### APK Release
```bash
# Build release APK
flutter build apk --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### App Bundle (Play Store)
```bash
flutter build appbundle --release
```

### Size Optimization
```yaml
# android/app/build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

---

## ACA Checkpoint: Planning Complete ✓
- Requirements analyzed
- Architecture designed
- Data flow mapped
- Edge cases identified
- Tools validated
- Error handling planned
- Testing strategy defined

Ready for implementation.
