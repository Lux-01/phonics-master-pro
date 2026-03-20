import 'package:hive/hive.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:phonics_master_pro/data/models/lesson.dart';
import 'package:phonics_master_pro/data/models/user_progress.dart';
import 'package:phonics_master_pro/data/models/word_tile.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  factory DatabaseService() => _instance;
  DatabaseService._internal();
  
  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;
  
  // Box references
  Box<Lesson>? _lessonsBox;
  Box<UserProgress>? _userProgressBox;
  Box<WordTile>? _wordsBox;
  Box<Map>? _settingsBox;
  
  Future<void> init() async {
    if (_isInitialized) return;
    
    // Initialize Hive
    await Hive.initFlutter();
    
    // Register adapters
    _registerAdapters();
    
    // Open boxes
    _lessonsBox = await Hive.openBox<Lesson>('lessons');
    _userProgressBox = await Hive.openBox<UserProgress>('user_progress');
    _wordsBox = await Hive.openBox<WordTile>('words');
    _settingsBox = await Hive.openBox<Map>('settings');
    
    _isInitialized = true;
  }
  
  void _registerAdapters() {
    // Check if already registered to avoid crashes
    if (!Hive.isAdapterRegistered(1)) {
      Hive.registerAdapter(LessonAdapter());
    }
    if (!Hive.isAdapterRegistered(2)) {
      Hive.registerAdapter(LessonStepAdapter());
    }
    if (!Hive.isAdapterRegistered(3)) {
      Hive.registerAdapter(UserProgressAdapter());
    }
    if (!Hive.isAdapterRegistered(4)) {
      Hive.registerAdapter(AchievementAdapter());
    }
    if (!Hive.isAdapterRegistered(5)) {
      Hive.registerAdapter(WordTileAdapter());
    }
    if (!Hive.isAdapterRegistered(6)) {
      Hive.registerAdapter(LessonStep2Adapter());
    }
  }
  
  // Generic CRUD operations
  Future<T?> get<T>(String boxName, String key) async {
    final box = await _getBox<T>(boxName);
    return box.get(key);
  }
  
  Future<void> put<T>(String boxName, String key, T value) async {
    final box = await _getBox<T>(boxName);
    await box.put(key, value);
  }
  
  Future<void> delete<T>(String boxName, String key) async {
    final box = await _getBox<T>(boxName);
    await box.delete(key);
  }
  
  Future<List<T>> getAll<T>(String boxName) async {
    final box = await _getBox<T>(boxName);
    return box.values.toList();
  }
  
  Future<void> clear<T>(String boxName) async {
    final box = await _getBox<T>(boxName);
    await box.clear();
  }
  
  Future<Box<T>> _getBox<T>(String boxName) async {
    if (!_isInitialized) await init();
    
    switch (boxName) {
      case 'lessons':
        return _lessonsBox as Box<T>;
      case 'user_progress':
        return _userProgressBox as Box<T>;
      case 'words':
        return _wordsBox as Box<T>;
      case 'settings':
        return _settingsBox as Box<T>;
      default:
        return await Hive.openBox<T>(boxName);
    }
  }
  
  // Settings helpers
  Future<void> setSetting(String key, dynamic value) async {
    if (_settingsBox == null) await init();
    await _settingsBox!.put(key, {'value': value});
  }
  
  Future<T?> getSetting<T>(String key, {T? defaultValue}) async {
    if (_settingsBox == null) await init();
    final result = _settingsBox!.get(key);
    if (result == null) return defaultValue;
    return result['value'] as T?;
  }
  
  Future<void> removeSetting(String key) async {
    if (_settingsBox == null) await init();
    await _settingsBox!.delete(key);
  }
  
  // Batch operations
  Future<void> putAll<T>(String boxName, Map<String, T> entries) async {
    final box = await _getBox<T>(boxName);
    await box.putAll(entries);
  }
  
  // Close all boxes
  Future<void> closeAll() async {
    await _lessonsBox?.close();
    await _userProgressBox?.close();
    await _wordsBox?.close();
    await _settingsBox?.close();
    _isInitialized = false;
  }
  
  // Reset all data
  Future<void> resetAll() async {
    await _lessonsBox?.clear();
    await _userProgressBox?.clear();
    await _wordsBox?.clear();
    await _settingsBox?.clear();
  }
  
  // Backup and restore (for parent settings)
  Future<Map<String, dynamic>> exportData() async {
    final export = <String, dynamic>{};
    
    // Export user progress
    final userProgress = <String, dynamic>{};
    for (var entry in _userProgressBox!.toMap().entries) {
      userProgress[entry.key] = _userProgressToMap(entry.value);
    }
    export['user_progress'] = userProgress;
    
    // Export settings
    export['settings'] = _settingsBox!.toMap();
    
    return export;
  }
  
  Future<void> importData(Map<String, dynamic> data) async {
    // Import user progress
    final userProgress = data['user_progress'] as Map<String, dynamic>?;
    if (userProgress != null) {
      for (var entry in userProgress.entries) {
        // Recreate UserProgress from map
      }
    }
    
    // Import settings
    final settings = data['settings'] as Map<String, dynamic>?;
    if (settings != null) {
      await _settingsBox!.clear();
      await _settingsBox!.putAll(settings.cast<String, Map>());
    }
  }
  
  Map<String, dynamic> _userProgressToMap(UserProgress progress) {
    return {
      'userId': progress.userId,
      'totalLessonsCompleted': progress.totalLessonsCompleted,
      'streakDays': progress.streakDays,
      'lastSessionDate': progress.lastSessionDate?.toIso8601String(),
      'skillLevels': progress.skillLevels,
      'unlockedAchievements': progress.unlockedAchievements,
      'totalStarsEarned': progress.totalStarsEarned,
      'completedLessons': progress.completedLessons,
    };
  }
  
  // Stats
  Future<int> getBoxSize(String boxName) async {
    final box = await _getBox<dynamic>(boxName);
    return box.length;
  }
  
  Future<int> getTotalSize() async {
    int total = 0;
    total += await getBoxSize('lessons');
    total += await getBoxSize('user_progress');
    total += await getBoxSize('words');
    total += await getBoxSize('settings');
    return total;
  }
  
  // Compact database
  Future<void> compact() async {
    await Hive.compact();
  }
}

// Extension for migration
extension DatabaseMigration on DatabaseService {
  Future<void> migrateIfNeeded() async {
    final currentVersion = await getSetting<int>('db_version', defaultValue: 1);
    
    if (currentVersion < 2) {
      // Perform migration to version 2
      await _migrateToV2();
      await setSetting('db_version', 2);
    }
  }
  
  Future<void> _migrateToV2() async {
    // Migration logic for version 2
    // e.g., add new fields, transform data
  }
}