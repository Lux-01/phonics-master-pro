import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phonics_master_pro/data/services/database_service.dart';

// Database service provider
final databaseServiceProvider = Provider<DatabaseService>((ref) {
  final service = DatabaseService();
  ref.onDispose(() async {
    await service.closeAll();
  });
  return service;
});

// App settings state
class AppSettings {
  final ThemeMode themeMode;
  final bool dyslexiaMode;
  final double fontSize;
  final bool highContrast;
  final bool reducedMotion;
  final bool soundEffects;
  final double audioVolume;
  final bool autoAdvance;
  final bool showHints;
  final int dailyGoal;
  final String userName;
  final String? userAvatar;
  final bool parentalControls;
  final int? parentPin;
  final int timeLimitMinutes;
  
  const AppSettings({
    this.themeMode = ThemeMode.light,
    this.dyslexiaMode = false,
    this.fontSize = 1.0,
    this.highContrast = false,
    this.reducedMotion = false,
    this.soundEffects = true,
    this.audioVolume = 1.0,
    this.autoAdvance = false,
    this.showHints = true,
    this.dailyGoal = 3,
    this.userName = 'Learner',
    this.userAvatar,
    this.parentalControls = false,
    this.parentPin,
    this.timeLimitMinutes = 60,
  });
  
  AppSettings copyWith({
    ThemeMode? themeMode,
    bool? dyslexiaMode,
    double? fontSize,
    bool? highContrast,
    bool? reducedMotion,
    bool? soundEffects,
    double? audioVolume,
    bool? autoAdvance,
    bool? showHints,
    int? dailyGoal,
    String? userName,
    String? userAvatar,
    bool? parentalControls,
    int? parentPin,
    int? timeLimitMinutes,
  }) {
    return AppSettings(
      themeMode: themeMode ?? this.themeMode,
      dyslexiaMode: dyslexiaMode ?? this.dyslexiaMode,
      fontSize: fontSize ?? this.fontSize,
      highContrast: highContrast ?? this.highContrast,
      reducedMotion: reducedMotion ?? this.reducedMotion,
      soundEffects: soundEffects ?? this.soundEffects,
      audioVolume: audioVolume ?? this.audioVolume,
      autoAdvance: autoAdvance ?? this.autoAdvance,
      showHints: showHints ?? this.showHints,
      dailyGoal: dailyGoal ?? this.dailyGoal,
      userName: userName ?? this.userName,
      userAvatar: userAvatar ?? this.userAvatar,
      parentalControls: parentalControls ?? this.parentalControls,
      parentPin: parentPin ?? this.parentPin,
      timeLimitMinutes: timeLimitMinutes ?? this.timeLimitMinutes,
    );
  }
}

// Settings notifier
class SettingsNotifier extends StateNotifier<AppSettings> {
  final DatabaseService _databaseService;
  
  SettingsNotifier(this._databaseService) : super(const AppSettings()) {
    _loadSettings();
  }
  
  Future<void> _loadSettings() async {
    await _databaseService.init();
    
    final themeMode = await _databaseService.getSetting<int>('theme_mode');
    final dyslexiaMode = await _databaseService.getSetting<bool>('dyslexia_mode');
    final fontSize = await _databaseService.getSetting<double>('font_size');
    final highContrast = await _databaseService.getSetting<bool>('high_contrast');
    final reducedMotion = await _databaseService.getSetting<bool>('reduced_motion');
    final soundEffects = await _databaseService.getSetting<bool>('sound_effects');
    final audioVolume = await _databaseService.getSetting<double>('audio_volume');
    final autoAdvance = await _databaseService.getSetting<bool>('auto_advance');
    final showHints = await _databaseService.getSetting<bool>('show_hints');
    final dailyGoal = await _databaseService.getSetting<int>('daily_goal');
    final userName = await _databaseService.getSetting<String>('user_name');
    final userAvatar = await _databaseService.getSetting<String>('user_avatar');
    final parentalControls = await _databaseService.getSetting<bool>('parental_controls');
    final parentPin = await _databaseService.getSetting<int>('parent_pin');
    final timeLimit = await _databaseService.getSetting<int>('time_limit');
    
    state = AppSettings(
      themeMode: themeMode != null 
          ? ThemeMode.values[themeMode] 
          : ThemeMode.light,
      dyslexiaMode: dyslexiaMode ?? false,
      fontSize: fontSize ?? 1.0,
      highContrast: highContrast ?? false,
      reducedMotion: reducedMotion ?? false,
      soundEffects: soundEffects ?? true,
      audioVolume: audioVolume ?? 1.0,
      autoAdvance: autoAdvance ?? false,
      showHints: showHints ?? true,
      dailyGoal: dailyGoal ?? 3,
      userName: userName ?? 'Learner',
      userAvatar: userAvatar,
      parentalControls: parentalControls ?? false,
      parentPin: parentPin,
      timeLimitMinutes: timeLimit ?? 60,
    );
  }
  
  Future<void> _saveSettings() async {
    await _databaseService.setSetting('theme_mode', state.themeMode.index);
    await _databaseService.setSetting('dyslexia_mode', state.dyslexiaMode);
    await _databaseService.setSetting('font_size', state.fontSize);
    await _databaseService.setSetting('high_contrast', state.highContrast);
    await _databaseService.setSetting('reduced_motion', state.reducedMotion);
    await _databaseService.setSetting('sound_effects', state.soundEffects);
    await _databaseService.setSetting('audio_volume', state.audioVolume);
    await _databaseService.setSetting('auto_advance', state.autoAdvance);
    await _databaseService.setSetting('show_hints', state.showHints);
    await _databaseService.setSetting('daily_goal', state.dailyGoal);
    await _databaseService.setSetting('user_name', state.userName);
    await _databaseService.setSetting('user_avatar', state.userAvatar);
    await _databaseService.setSetting('parental_controls', state.parentalControls);
    await _databaseService.setSetting('parent_pin', state.parentPin);
    await _databaseService.setSetting('time_limit', state.timeLimitMinutes);
  }
  
  // Theme settings
  void setThemeMode(ThemeMode mode) {
    state = state.copyWith(themeMode: mode);
    _saveSettings();
  }
  
  void toggleTheme() {
    final newMode = state.themeMode == ThemeMode.light 
        ? ThemeMode.dark 
        : ThemeMode.light;
    state = state.copyWith(themeMode: newMode);
    _saveSettings();
  }
  
  // Accessibility settings
  void setDyslexiaMode(bool enabled) {
    state = state.copyWith(dyslexiaMode: enabled);
    _saveSettings();
  }
  
  void setFontSize(double size) {
    state = state.copyWith(fontSize: size.clamp(0.8, 1.5));
    _saveSettings();
  }
  
  void setHighContrast(bool enabled) {
    state = state.copyWith(highContrast: enabled);
    _saveSettings();
  }
  
  void setReducedMotion(bool enabled) {
    state = state.copyWith(reducedMotion: enabled);
    _saveSettings();
  }
  
  // Audio settings
  void setSoundEffects(bool enabled) {
    state = state.copyWith(soundEffects: enabled);
    _saveSettings();
  }
  
  void setAudioVolume(double volume) {
    state = state.copyWith(audioVolume: volume.clamp(0.0, 1.0));
    _saveSettings();
  }
  
  // Learning settings
  void setAutoAdvance(bool enabled) {
    state = state.copyWith(autoAdvance: enabled);
    _saveSettings();
  }
  
  void setShowHints(bool enabled) {
    state = state.copyWith(showHints: enabled);
    _saveSettings();
  }
  
  void setDailyGoal(int goal) {
    state = state.copyWith(dailyGoal: goal.clamp(1, 10));
    _saveSettings();
  }
  
  // User profile
  void setUserName(String name) {
    state = state.copyWith(userName: name);
    _saveSettings();
  }
  
  void setUserAvatar(String? avatar) {
    state = state.copyWith(userAvatar: avatar);
    _saveSettings();
  }
  
  // Parental controls
  void setParentalControls(bool enabled) {
    state = state.copyWith(parentalControls: enabled);
    _saveSettings();
  }
  
  void setParentPin(int? pin) {
    state = state.copyWith(parentPin: pin);
    _saveSettings();
  }
  
  void setTimeLimit(int minutes) {
    state = state.copyWith(timeLimitMinutes: minutes.clamp(5, 180));
    _saveSettings();
  }
  
  // Reset all settings
  Future<void> resetToDefaults() async {
    state = const AppSettings();
    await _saveSettings();
  }
}

// Settings provider
final settingsProvider = StateNotifierProvider<SettingsNotifier, AppSettings>(
  (ref) => SettingsNotifier(ref.read(databaseServiceProvider)),
);

// Derived providers for specific settings
final themeModeProvider = Provider<ThemeMode>((ref) {
  return ref.watch(settingsProvider).themeMode;
});

final isDarkModeProvider = Provider<bool>((ref) {
  final themeMode = ref.watch(themeModeProvider);
  return themeMode == ThemeMode.dark;
});

final dyslexiaModeProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).dyslexiaMode;
});

final fontSizeProvider = Provider<double>((ref) {
  return ref.watch(settingsProvider).fontSize;
});

final highContrastProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).highContrast;
});

final reducedMotionProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).reducedMotion;
});

final soundEffectsProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).soundEffects;
});

final audioVolumeProvider = Provider<double>((ref) {
  return ref.watch(settingsProvider).audioVolume;
});

final autoAdvanceProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).autoAdvance;
});

final showHintsProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).showHints;
});

final dailyGoalProvider = Provider<int>((ref) {
  return ref.watch(settingsProvider).dailyGoal;
});

final userNameProvider = Provider<String>((ref) {
  return ref.watch(settingsProvider).userName;
});

final userAvatarProvider = Provider<String?>((ref) {
  return ref.watch(settingsProvider).userAvatar;
});

final parentalControlsProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).parentalControls;
});

final parentPinProvider = Provider<int?>((ref) {
  return ref.watch(settingsProvider).parentPin;
});

final timeLimitProvider = Provider<int>((ref) {
  return ref.watch(settingsProvider).timeLimitMinutes;
});

// Font provider based on settings
final appFontProvider = Provider<String>((ref) {
  final dyslexiaMode = ref.watch(dyslexiaModeProvider);
  return dyslexiaMode ? 'OpenDyslexic' : 'Inter';
});

// Effective text theme based on settings
final effectiveTextThemeProvider = Provider<TextTheme>((ref) {
  final fontSize = ref.watch(fontSizeProvider);
  final baseTheme = ref.watch(isDarkModeProvider) 
      ? ThemeData.dark().textTheme 
      : ThemeData.light().textTheme;
  
  return baseTheme.apply(
    fontSizeFactor: fontSize,
  );
});

// Parental controls validation
final parentAuthProvider = StateNotifierProvider<ParentAuthNotifier, bool>(
  (ref) => ParentAuthNotifier(ref),
);

class ParentAuthNotifier extends StateNotifier<bool> {
  final ProviderRef _ref;
  DateTime? _lastAuthenticated;
  
  ParentAuthNotifier(this._ref) : super(false);
  
  bool authenticate(int pin) {
    final correctPin = _ref.read(parentPinProvider);
    
    if (correctPin == null) {
      // No PIN set, allow access
      state = true;
      _lastAuthenticated = DateTime.now();
      return true;
    }
    
    if (pin == correctPin) {
      state = true;
      _lastAuthenticated = DateTime.now();
      return true;
    }
    
    return false;
  }
  
  bool checkAuthStatus() {
    if (_lastAuthenticated == null) {
      state = false;
      return false;
    }
    
    // Auth expires after 5 minutes
    if (DateTime.now().difference(_lastAuthenticated!).inMinutes > 5) {
      state = false;
      return false;
    }
    
    return state;
  }
  
  void logout() {
    state = false;
    _lastAuthenticated = null;
  }
}

// First launch provider
final isFirstLaunchProvider = FutureProvider<bool>((ref) async {
  final db = ref.read(databaseServiceProvider);
  await db.init();
  final hasLaunched = await db.getSetting<bool>('has_launched_before', defaultValue: false);
  return !hasLaunched;
});

final markFirstLaunchCompleteProvider = Provider<Future<void> Function()>((ref) {
  return () async {
    final db = ref.read(databaseServiceProvider);
    await db.init();
    await db.setSetting('has_launched_before', true);
  };
});

// Session timer for parental time limits
final sessionTimerProvider = StateNotifierProvider<SessionTimerNotifier, SessionTimerState>(
  (ref) => SessionTimerNotifier(ref),
);

class SessionTimerState {
  final int elapsedSeconds;
  final bool isRunning;
  final bool isPaused;
  final bool hasTimeRemaining;
  
  SessionTimerState({
    this.elapsedSeconds = 0,
    this.isRunning = false,
    this.isPaused = false,
    required bool hasTimeRemaining,
  }) : hasTimeRemaining = hasTimeRemaining;
  
  SessionTimerState copyWith({
    int? elapsedSeconds,
    bool? isRunning,
    bool? isPaused,
    bool? hasTimeRemaining,
  }) {
    return SessionTimerState(
      elapsedSeconds: elapsedSeconds ?? this.elapsedSeconds,
      isRunning: isRunning ?? this.isRunning,
      isPaused: isPaused ?? this.isPaused,
      hasTimeRemaining: hasTimeRemaining ?? this.hasTimeRemaining,
    );
  }
  
  Duration get elapsed => Duration(seconds: elapsedSeconds);
  int get elapsedMinutes => elapsedSeconds ~/ 60;
}

class SessionTimerNotifier extends StateNotifier<SessionTimerState> {
  final ProviderRef _ref;
  Timer? _timer;
  
  SessionTimerNotifier(this._ref) 
    : super(SessionTimerState(hasTimeRemaining: true)) {
    _checkTimeLimit();
  }
  
  void _checkTimeLimit() {
    final timeLimit = _ref.read(timeLimitProvider);
    final isParentalEnabled = _ref.read(parentalControlsProvider);
    
    if (!isParentalEnabled) {
      state = state.copyWith(hasTimeRemaining: true);
      return;
    }
    
    final hasTime = elapsedMinutes < timeLimit;
    state = state.copyWith(hasTimeRemaining: hasTime);
  }
  
  void start() {
    if (state.isRunning && !state.isPaused) return;
    
    state = state.copyWith(isRunning: true, isPaused: false);
    
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      final newElapsed = state.elapsedSeconds + 1;
      final timeLimit = _ref.read(timeLimitProvider) * 60;
      
      state = state.copyWith(
        elapsedSeconds: newElapsed,
        hasTimeRemaining: newElapsed < timeLimit,
      );
      
      if (newElapsed >= timeLimit && _ref.read(parentalControlsProvider)) {
        pause();
        // Could trigger a notification or save state
      }
    });
  }
  
  void pause() {
    _timer?.cancel();
    state = state.copyWith(isPaused: true);
  }
  
  void stop() {
    _timer?.cancel();
    state = SessionTimerState(hasTimeRemaining: true);
  }
  
  void resume() {
    start();
  }
  
  void reset() {
    _timer?.cancel();
    state = SessionTimerState(hasTimeRemaining: true);
  }
  
  int get elapsedMinutes => state.elapsedSeconds ~/ 60;
  
  int get remainingMinutes {
    final timeLimit = _ref.read(timeLimitProvider);
    return timeLimit - elapsedMinutes;
  }
  
  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}