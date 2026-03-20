import 'package:hive/hive.dart';
import 'package:phonics_master_pro/data/models/lesson.dart';
import 'package:phonics_master_pro/data/models/word_tile.dart';

class LessonRepository {
  static const String _boxName = 'lessons';
  static const String _progressBoxName = 'lesson_progress';
  
  Box<Lesson>? _lessonBox;
  Box<Map>? _progressBox;
  
  Future<void> init() async {
    if (!Hive.isAdapterRegistered(1)) {
      Hive.registerAdapter(LessonAdapter());
    }
    if (!Hive.isAdapterRegistered(2)) {
      Hive.registerAdapter(LessonStepAdapter());
    }
    
    _lessonBox = await Hive.openBox<Lesson>(_boxName);
    _progressBox = await Hive.openBox<Map>(_progressBoxName);
    
    // Seed initial curriculum if empty
    if (_lessonBox!.isEmpty) {
      await _seedLessons();
    }
  }
  
  Future<void> _seedLessons() async {
    final lessons = PhonicsCurriculum.allLessons;
    for (var lesson in lessons) {
      await _lessonBox!.put(lesson.id, lesson);
    }
  }
  
  // CRUD Operations
  Future<List<Lesson>> getAllLessons() async {
    if (_lessonBox == null) await init();
    return _lessonBox!.values.toList();
  }
  
  Future<Lesson?> getLessonById(String id) async {
    if (_lessonBox == null) await init();
    return _lessonBox!.get(id);
  }
  
  Future<List<Lesson>> getLessonsByLevel(int level) async {
    if (_lessonBox == null) await init();
    return _lessonBox!.values.where((l) => l.level == level).toList();
  }
  
  Future<void> saveLesson(Lesson lesson) async {
    if (_lessonBox == null) await init();
    await _lessonBox!.put(lesson.id, lesson);
  }
  
  Future<void> updateLessonProgress(String lessonId, double progress) async {
    if (_lessonBox == null) await init();
    final lesson = _lessonBox!.get(lessonId);
    if (lesson != null) {
      lesson.progress = progress;
      await lesson.save();
    }
  }
  
  Future<void> completeLesson(String lessonId, int stars) async {
    if (_lessonBox == null) await init();
    final lesson = _lessonBox!.get(lessonId);
    if (lesson != null) {
      lesson.isCompleted = true;
      lesson.progress = 1.0;
      lesson.stars = stars;
      lesson.completedAt = DateTime.now();
      await lesson.save();
    }
  }
  
  // Progress tracking
  Future<double> getOverallProgress() async {
    if (_lessonBox == null) await init();
    final lessons = _lessonBox!.values.toList();
    if (lessons.isEmpty) return 0.0;
    
    final totalProgress = lessons.fold<double>(
      0.0, 
      (sum, lesson) => sum + lesson.progress
    );
    return totalProgress / lessons.length;
  }
  
  Future<int> getCompletedLessonsCount() async {
    if (_lessonBox == null) await init();
    return _lessonBox!.values.where((l) => l.isCompleted).length;
  }
  
  Future<int> getTotalStars() async {
    if (_lessonBox == null) await init();
    return _lessonBox!.values.fold<int>(
      0, 
      (sum, lesson) => sum + lesson.stars
    );
  }
  
  // Get next lesson
  Future<Lesson?> getNextLesson() async {
    if (_lessonBox == null) await init();
    
    // First try to find incomplete started lessons
    final inProgress = _lessonBox!.values
        .where((l) => !l.isCompleted && l.progress > 0)
        .toList()
      ..sort((a, b) => a.level.compareTo(b.level));
    
    if (inProgress.isNotEmpty) return inProgress.first;
    
    // Then find first unstarted lesson
    final unstarted = _lessonBox!.values
        .where((l) => !l.isCompleted && l.progress == 0)
        .toList()
      ..sort((a, b) => a.level.compareTo(b.level));
    
    if (unstarted.isNotEmpty) return unstarted.first;
    
    return null; // All complete
  }
  
  // Recommended lessons based on level
  Future<List<Lesson>> getRecommendedLessons() async {
    if (_lessonBox == null) await init();
    
    final nextLesson = await getNextLesson();
    if (nextLesson == null) return [];
    
    // Get lessons at same level
    return _lessonBox!.values
        .where((l) => l.level == nextLesson.level && !l.isCompleted)
        .take(3)
        .toList();
  }
  
  // Reset progress
  Future<void> resetAllProgress() async {
    if (_lessonBox == null) await init();
    
    for (var lesson in _lessonBox!.values) {
      lesson.isCompleted = false;
      lesson.progress = 0.0;
      lesson.stars = 0;
      lesson.completedAt = null;
      await lesson.save();
    }
  }
  
  // Lesson step management
  Future<void> updateStepProgress(
    String lessonId, 
    String stepId, 
    bool completed
  ) async {
    if (_lessonBox == null) await init();
    
    final lesson = _lessonBox!.get(lessonId);
    if (lesson != null) {
      final stepIndex = lesson.steps.indexWhere((s) => s.id == stepId);
      if (stepIndex != -1) {
        lesson.steps[stepIndex].isCompleted = completed;
        
        // Recalculate progress
        final completedSteps = lesson.steps.where((s) => s.isCompleted).length;
        lesson.progress = completedSteps / lesson.steps.length;
        
        await lesson.save();
      }
    }
  }
  
  // Word practice
  Future<List<WordTile>> getWordsForLesson(String lessonId) async {
    final lesson = await getLessonById(lessonId);
    if (lesson == null) return [];
    
    // Extract words from lesson steps
    final wordIds = lesson.steps
        .where((s) => s.word != null)
        .map((s) => s.word!)
        .toSet();
    
    return wordIds
        .map((id) => WordLibrary.getById('word_$id'))
        .whereType<WordTile>()
        .toList();
  }
  
  // Search lessons
  Future<List<Lesson>> searchLessons(String query) async {
    if (_lessonBox == null) await init();
    
    final lowerQuery = query.toLowerCase();
    return _lessonBox!.values.where((lesson) {
      return lesson.title.toLowerCase().contains(lowerQuery) ||
             lesson.description.toLowerCase().contains(lowerQuery);
    }).toList();
  }
  
  // Stats
  Future<Map<String, dynamic>> getLessonStats() async {
    if (_lessonBox == null) await init();
    
    final lessons = _lessonBox!.values.toList();
    final byLevel = <int, int>{};
    
    for (var lesson in lessons) {
      byLevel[lesson.level] = (byLevel[lesson.level] ?? 0) + 1;
    }
    
    return {
      'totalLessons': lessons.length,
      'completedLessons': lessons.where((l) => l.isCompleted).length,
      'inProgressLessons': lessons.where((l) => !l.isCompleted && l.progress > 0).length,
      'totalStars': lessons.fold(0, (sum, l) => sum + l.stars),
      'lessonsByLevel': byLevel,
      'overallProgress': await getOverallProgress(),
    };
  }
  
  // Delete all data
  Future<void> clearAll() async {
    if (_lessonBox != null) {
      await _lessonBox!.clear();
    }
    if (_progressBox != null) {
      await _progressBox!.clear();
    }
  }
  
  // Close boxes
  Future<void> close() async {
    await _lessonBox?.close();
    await _progressBox?.close();
  }
}