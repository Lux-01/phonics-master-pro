import 'package:hive/hive.dart';

part 'user_progress.g.dart';

@HiveType(typeId: 3)
class UserProgress extends HiveObject {
  @HiveField(0)
  final String userId;
  
  @HiveField(1)
  int totalLessonsCompleted;
  
  @HiveField(2)
  int streakDays;
  
  @HiveField(3)
  DateTime? lastSessionDate;
  
  @HiveField(4)
  Map<String, double> skillLevels;
  
  @HiveField(5)
  List<String> unlockedAchievements;
  
  @HiveField(6)
  int totalStarsEarned;
  
  @HiveField(7)
  int totalTimeSpentMinutes;
  
  @HiveField(8)
  Map<String, double> lessonProgress;
  
  @HiveField(9)
  DateTime? streakStartDate;
  
  @HiveField(10)
  List<String> completedLessons;
  
  @HiveField(11)
  Map<String, int> letterAccuracy;
  
  UserProgress({
    required this.userId,
    this.totalLessonsCompleted = 0,
    this.streakDays = 0,
    this.lastSessionDate,
    this.skillLevels = const {},
    this.unlockedAchievements = const [],
    this.totalStarsEarned = 0,
    this.totalTimeSpentMinutes = 0,
    this.lessonProgress = const {},
    this.streakStartDate,
    this.completedLessons = const [],
    this.letterAccuracy = const {},
  });
  
  factory UserProgress.create(String userId) {
    return UserProgress(
      userId: userId,
      skillLevels: {
        'letter_sounds': 0.0,
        'blending': 0.0,
        'sight_words': 0.0,
        'tracing': 0.0,
        'pronunciation': 0.0,
      },
    );
  }
  
  void updateStreak() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    
    if (lastSessionDate == null) {
      streakDays = 1;
      streakStartDate = today;
    } else {
      final lastDate = DateTime(
        lastSessionDate!.year,
        lastSessionDate!.month,
        lastSessionDate!.day,
      );
      final difference = today.difference(lastDate).inDays;
      
      if (difference == 1) {
        streakDays++;
      } else if (difference > 1) {
        streakDays = 1;
        streakStartDate = today;
      }
    }
    
    lastSessionDate = now;
  }
  
  void completeLesson(String lessonId, int stars, double accuracy) {
    if (!completedLessons.contains(lessonId)) {
      completedLessons.add(lessonId);
      totalLessonsCompleted++;
    }
    
    totalStarsEarned += stars;
    lessonProgress[lessonId] = 1.0;
    updateStreak();
  }
  
  void updateLessonProgress(String lessonId, double progress) {
    lessonProgress[lessonId] = progress.clamp(0.0, 1.0);
  }
  
  void updateSkillLevel(String skill, double level) {
    skillLevels[skill] = level.clamp(0.0, 1.0);
  }
  
  void addTimeSpent(int minutes) {
    totalTimeSpentMinutes += minutes;
  }
  
  void unlockAchievement(String achievementId) {
    if (!unlockedAchievements.contains(achievementId)) {
      unlockedAchievements.add(achievementId);
    }
  }
  
  void updateLetterAccuracy(String letter, int accuracy) {
    letterAccuracy[letter] = accuracy;
  }
  
  double get overallAccuracy {
    if (letterAccuracy.isEmpty) return 0.0;
    final total = letterAccuracy.values.reduce((a, b) => a + b);
    return total / letterAccuracy.length / 100;
  }
  
  double getLevelProgress(int level) {
    final levelLessons = lessonProgress.entries
        .where((e) => e.key.startsWith('level$level'));
    if (levelLessons.isEmpty) return 0.0;
    return levelLessons.map((e) => e.value).reduce((a, b) => a + b) / levelLessons.length;
  }
}

@HiveType(typeId: 4)
class Achievement extends HiveObject {
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final String title;
  
  @HiveField(2)
  final String description;
  
  @HiveField(3)
  final String iconAsset;
  
  @HiveField(4)
  final String? badgeColor;
  
  @HiveField(5)
  final int requiredProgress;
  
  @HiveField(6)
  bool isUnlocked;
  
  @HiveField(7)
  DateTime? unlockedAt;
  
  @HiveField(8)
  final String category;
  
  Achievement({
    required this.id,
    required this.title,
    required this.description,
    required this.iconAsset,
    this.badgeColor,
    this.requiredProgress = 1,
    this.isUnlocked = false,
    this.unlockedAt,
    this.category = 'general',
  });
  
  void unlock() {
    if (!isUnlocked) {
      isUnlocked = true;
      unlockedAt = DateTime.now();
    }
  }
}

// Predefined achievements
class AchievementLibrary {
  static List<Achievement> get all => [
    Achievement(
      id: 'first_lesson',
      title: 'First Steps',
      description: 'Complete your first lesson',
      iconAsset: 'assets/images/achievements/first_steps.png',
      badgeColor: '27AE60',
      category: 'milestone',
    ),
    Achievement(
      id: 'streak_3',
      title: 'On a Roll',
      description: 'Maintain a 3-day streak',
      iconAsset: 'assets/images/achievements/streak.png',
      badgeColor: 'E67E22',
      category: 'streak',
    ),
    Achievement(
      id: 'streak_7',
      title: 'Week Warrior',
      description: 'Maintain a 7-day streak',
      iconAsset: 'assets/images/achievements/streak_7.png',
      badgeColor: 'E74C3C',
      category: 'streak',
    ),
    Achievement(
      id: 'streak_30',
      title: 'Month Master',
      description: 'Maintain a 30-day streak',
      iconAsset: 'assets/images/achievements/streak_30.png',
      badgeColor: '9B59B6',
      category: 'streak',
    ),
    Achievement(
      id: 'collector_10',
      title: 'Star Collector',
      description: 'Earn 10 stars',
      iconAsset: 'assets/images/achievements/stars.png',
      badgeColor: 'F1C40F',
      category: 'collection',
    ),
    Achievement(
      id: 'collector_50',
      title: 'Star Hoarder',
      description: 'Earn 50 stars',
      iconAsset: 'assets/images/achievements/stars_50.png',
      badgeColor: 'F39C12',
      category: 'collection',
    ),
    Achievement(
      id: 'alphabet_master',
      title: 'Alphabet Master',
      description: 'Complete all ABC lessons',
      iconAsset: 'assets/images/achievements/alphabet.png',
      badgeColor: '3498DB',
      category: 'completion',
    ),
    Achievement(
      id: 'word_builder',
      title: 'Word Builder',
      description: 'Complete 10 word lessons',
      iconAsset: 'assets/images/achievements/words.png',
      badgeColor: '1ABC9C',
      category: 'completion',
    ),
    Achievement(
      id: 'perfect_score',
      title: 'Perfect Score',
      description: 'Get 3 stars on any lesson',
      iconAsset: 'assets/images/achievements/perfect.png',
      badgeColor: 'FF6B6B',
      category: 'performance',
    ),
    Achievement(
      id: 'fast_learner',
      title: 'Fast Learner',
      description: 'Complete 5 lessons in one day',
      iconAsset: 'assets/images/achievements/speed.png',
      badgeColor: 'E74C3C',
      category: 'performance',
    ),
    Achievement(
      id: 'tracing_pro',
      title: 'Tracing Pro',
      description: 'Achieve 90% accuracy on 5 letters',
      iconAsset: 'assets/images/achievements/tracing.png',
      badgeColor: '4ECDC4',
      category: 'skill',
    ),
    Achievement(
      id: 'pronunciation_expert',
      title: 'Voice Virtuoso',
      description: 'Get 5 pronunciation checks correct',
      iconAsset: 'assets/images/achievements/voice.png',
      badgeColor: '9B59B6',
      category: 'skill',
    ),
  ];
  
  static Achievement? getById(String id) {
    try {
      return all.firstWhere((a) => a.id == id);
    } catch (e) {
      return null;
    }
  }
}

// Gamification helpers
class GamificationRules {
  static int calculateStars(double accuracy, int attempts, int timeInSeconds) {
    int stars = 1;
    
    if (accuracy >= 0.9) stars++;
    if (attempts <= 2) stars++;
    if (timeInSeconds < 60) stars++;
    
    return stars.clamp(1, 3);
  }
  
  static int calculateXP(double accuracy, int lessonLevel, bool isCompleted) {
    int baseXP = 10 * lessonLevel;
    int accuracyBonus = (accuracy * 50).toInt();
    int completionBonus = isCompleted ? 50 : 0;
    
    return baseXP + accuracyBonus + completionBonus;
  }
  
  static String getStreakMessage(int streak) {
    if (streak >= 30) return 'Incredible! 🔥 $streak day streak!';
    if (streak >= 7) return 'Amazing! 🔥 $streak day streak!';
    if (streak >= 3) return 'Great job! 🔥 $streak day streak!';
    if (streak >= 1) return 'Keep it up! 🔥 $streak day streak';
    return 'Start your streak today!';
  }
}