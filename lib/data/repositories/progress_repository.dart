import 'package:hive/hive.dart';
import 'package:phonics_master_pro/data/models/user_progress.dart';

class ProgressRepository {
  static const String _boxName = 'user_progress';
  static const String _achievementsBoxName = 'achievements';
  
  Box<UserProgress>? _progressBox;
  Box<Achievement>? _achievementsBox;
  
  Future<void> init() async {
    if (!Hive.isAdapterRegistered(3)) {
      Hive.registerAdapter(UserProgressAdapter());
    }
    if (!Hive.isAdapterRegistered(4)) {
      Hive.registerAdapter(AchievementAdapter());
    }
    
    _progressBox = await Hive.openBox<UserProgress>(_boxName);
    _achievementsBox = await Hive.openBox<Achievement>(_achievementsBoxName);
    
    // Seed achievements if empty
    if (_achievementsBox!.isEmpty) {
      await _seedAchievements();
    }
  }
  
  Future<void> _seedAchievements() async {
    for (var achievement in AchievementLibrary.all) {
      await _achievementsBox!.put(achievement.id, achievement);
    }
  }
  
  // User Progress CRUD
  Future<UserProgress> getOrCreateUserProgress(String userId) async {
    if (_progressBox == null) await init();
    
    var progress = _progressBox!.get(userId);
    if (progress == null) {
      progress = UserProgress.create(userId);
      await _progressBox!.put(userId, progress);
    }
    return progress;
  }
  
  Future<UserProgress?> getUserProgress(String userId) async {
    if (_progressBox == null) await init();
    return _progressBox!.get(userId);
  }
  
  Future<void> saveUserProgress(UserProgress progress) async {
    if (_progressBox == null) await init();
    await _progressBox!.put(progress.userId, progress);
  }
  
  // Streak management
  Future<void> updateStreak(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    progress.updateStreak();
    await progress.save();
  }
  
  Future<int> getCurrentStreak(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    return progress.streakDays;
  }
  
  Future<void> resetStreak(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    progress.streakDays = 0;
    progress.streakStartDate = null;
    await progress.save();
  }
  
  // Lesson completion
  Future<void> completeLesson(
    String userId, 
    String lessonId, 
    int stars,
    double accuracy,
  ) async {
    final progress = await getOrCreateUserProgress(userId);
    progress.completeLesson(lessonId, stars, accuracy);
    await progress.save();
    
    // Check for achievements after lesson completion
    await checkAchievements(userId);
  }
  
  Future<void> updateLessonProgress(String userId, String lessonId, double progress) async {
    final userProgress = await getOrCreateUserProgress(userId);
    userProgress.updateLessonProgress(lessonId, progress);
    await userProgress.save();
  }
  
  // Skill level management
  Future<void> updateSkillLevel(String userId, String skill, double level) async {
    final progress = await getOrCreateUserProgress(userId);
    progress.updateSkillLevel(skill, level);
    await progress.save();
  }
  
  Future<Map<String, double>> getSkillLevels(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    return Map<String, double>.from(progress.skillLevels);
  }
  
  // Time tracking
  Future<void> addTimeSpent(String userId, int minutes) async {
    final progress = await getOrCreateUserProgress(userId);
    progress.addTimeSpent(minutes);
    await progress.save();
  }
  
  Future<int> getTotalTimeSpent(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    return progress.totalTimeSpentMinutes;
  }
  
  // Achievement management
  Future<List<Achievement>> getAllAchievements() async {
    if (_achievementsBox == null) await init();
    return _achievementsBox!.values.toList();
  }
  
  Future<List<Achievement>> getUnlockedAchievements(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    
    if (_achievementsBox == null) await init();
    
    return progress.unlockedAchievements
        .map((id) => _achievementsBox!.get(id))
        .whereType<Achievement>()
        .toList();
  }
  
  Future<List<Achievement>> getLockedAchievements(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    
    if (_achievementsBox == null) await init();
    
    return _achievementsBox!.values
        .where((a) => !progress.unlockedAchievements.contains(a.id))
        .toList();
  }
  
  Future<Achievement?> getAchievementById(String achievementId) async {
    if (_achievementsBox == null) await init();
    return _achievementsBox!.get(achievementId);
  }
  
  Future<bool> unlockAchievement(String userId, String achievementId) async {
    final progress = await getOrCreateUserProgress(userId);
    
    if (progress.unlockedAchievements.contains(achievementId)) {
      return false; // Already unlocked
    }
    
    progress.unlockAchievement(achievementId);
    
    final achievement = await getAchievementById(achievementId);
    if (achievement != null) {
      achievement.unlock();
      await achievement.save();
    }
    
    await progress.save();
    return true;
  }
  
  // Achievement checking
  Future<List<Achievement>> checkAchievements(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    final newlyUnlocked = <Achievement>[];
    
    // Check each achievement condition
    final checks = {
      'first_lesson': () => progress.totalLessonsCompleted >= 1,
      'streak_3': () => progress.streakDays >= 3,
      'streak_7': () => progress.streakDays >= 7,
      'streak_30': () => progress.streakDays >= 30,
      'collector_10': () => progress.totalStarsEarned >= 10,
      'collector_50': () => progress.totalStarsEarned >= 50,
      'alphabet_master': () => _checkAlphabetMaster(progress),
      'word_builder': () => _checkWordBuilder(progress),
      'perfect_score': () => _checkPerfectScore(progress),
      'fast_learner': () => _checkFastLearner(progress),
      'tracing_pro': () => _checkTracingPro(progress),
      'pronunciation_expert': () => _checkPronunciationExpert(progress),
    };
    
    for (var entry in checks.entries) {
      if (!progress.unlockedAchievements.contains(entry.key)) {
        if (entry.value()) {
          final achievement = await getAchievementById(entry.key);
          if (achievement != null) {
            await unlockAchievement(userId, entry.key);
            newlyUnlocked.add(achievement);
          }
        }
      }
    }
    
    return newlyUnlocked;
  }
  
  bool _checkAlphabetMaster(UserProgress progress) {
    final alphabetLessons = ['lesson_a', 'lesson_b', 'lesson_c', 'lesson_d', 
                             'lesson_e', 'lesson_f', 'lesson_g', 'lesson_h',
                             'lesson_i', 'lesson_j', 'lesson_k', 'lesson_l',
                             'lesson_m', 'lesson_n', 'lesson_o', 'lesson_p',
                             'lesson_q', 'lesson_r', 'lesson_s', 'lesson_t',
                             'lesson_u', 'lesson_v', 'lesson_w', 'lesson_x',
                             'lesson_y', 'lesson_z'];
    return alphabetLessons.every((id) => progress.completedLessons.contains(id));
  }
  
  bool _checkWordBuilder(UserProgress progress) {
    final wordLessons = progress.completedLessons.where((id) => 
      id.contains('word_') || id.contains('lesson_cat') || id.contains('lesson_dog')
    ).length;
    return wordLessons >= 10;
  }
  
  bool _checkPerfectScore(UserProgress progress) {
    return progress.totalStarsEarned >= 3;
  }
  
  bool _checkFastLearner(UserProgress progress) {
    if (progress.lastSessionDate == null) return false;
    
    final today = DateTime.now();
    return progress.completedLessons
        .where((id) {
          final lessonDate = progress.lessonProgress[id];
          // This is a simplified check - in real app would store completion dates
          return progress.lastSessionDate?.day == today.day;
        })
        .length >= 5;
  }
  
  bool _checkTracingPro(UserProgress progress) {
    final highAccuracyLetters = progress.letterAccuracy.entries
        .where((e) => e.value >= 90)
        .length;
    return highAccuracyLetters >= 5;
  }
  
  bool _checkPronunciationExpert(UserProgress progress) {
    return progress.skillLevels['pronunciation'] != null && 
           progress.skillLevels['pronunciation']! >= 0.5;
  }
  
  // Letter accuracy
  Future<void> updateLetterAccuracy(String userId, String letter, int accuracy) async {
    final progress = await getOrCreateUserProgress(userId);
    progress.updateLetterAccuracy(letter, accuracy);
    await progress.save();
    
    // Check for tracing achievement
    await checkAchievements(userId);
  }
  
  Future<Map<String, int>> getLetterAccuracy(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    return Map<String, int>.from(progress.letterAccuracy);
  }
  
  // Stats
  Future<Map<String, dynamic>> getProgressStats(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    final achievements = await getUnlockedAchievements(userId);
    
    return {
      'totalLessonsCompleted': progress.totalLessonsCompleted,
      'totalStarsEarned': progress.totalStarsEarned,
      'currentStreak': progress.streakDays,
      'bestStreak': progress.streakDays, // In real app would track separately
      'totalTimeSpentMinutes': progress.totalTimeSpentMinutes,
      'skillLevels': progress.skillLevels,
      'letterAccuracy': progress.letterAccuracy,
      'achievementsUnlocked': achievements.length,
      'achievementsTotal': AchievementLibrary.all.length,
      'overallAccuracy': progress.overallAccuracy,
    };
  }
  
  // Daily goal tracking
  Future<Map<String, dynamic>> getDailyProgress(String userId) async {
    final progress = await getOrCreateUserProgress(userId);
    final today = DateTime.now();
    
    // Check if last session was today
    final isToday = progress.lastSessionDate != null &&
        progress.lastSessionDate!.day == today.day &&
        progress.lastSessionDate!.month == today.month &&
        progress.lastSessionDate!.year == today.year;
    
    return {
      'hasPracticedToday': isToday,
      'lessonsToday': isToday ? progress.totalLessonsCompleted : 0,
      'minutesToday': isToday ? progress.totalTimeSpentMinutes : 0,
      'streakActive': isToday,
      'currentStreak': progress.streakDays,
    };
  }
  
  // Reset all progress
  Future<void> resetAllProgress(String userId) async {
    final progress = UserProgress.create(userId);
    await _progressBox!.put(userId, progress);
    
    // Reset achievement unlocks
    if (_achievementsBox != null) {
      for (var achievement in _achievementsBox!.values) {
        achievement.isUnlocked = false;
        achievement.unlockedAt = null;
        await achievement.save();
      }
    }
  }
  
  // Close boxes
  Future<void> close() async {
    await _progressBox?.close();
    await _achievementsBox?.close();
  }
}