import 'dart:convert';

class UserProgressModel {
  String region;
  String childName;
  int currentPhase;
  int currentLetterIndex;
  Map<String, int> letterStars;
  int streakDays;
  DateTime? lastPracticeDate;
  List<String> masteredWords;
  int mascotStage;

  UserProgressModel({
    this.region = 'au',
    this.childName = 'Friend',
    this.currentPhase = 1,
    this.currentLetterIndex = 0,
    Map<String, int>? letterStars,
    this.streakDays = 0,
    this.lastPracticeDate,
    List<String>? masteredWords,
    this.mascotStage = 1,
  }) : 
    letterStars = letterStars ?? {},
    masteredWords = masteredWords ?? [];

  factory UserProgressModel.fromJson(Map<String, dynamic> json) {
    return UserProgressModel(
      region: json['region'] as String? ?? 'au',
      childName: json['childName'] as String? ?? 'Friend',
      currentPhase: json['currentPhase'] as int? ?? 1,
      currentLetterIndex: json['currentLetterIndex'] as int? ?? 0,
      letterStars: Map<String, int>.from(json['letterStars'] ?? {}),
      streakDays: json['streakDays'] as int? ?? 0,
      lastPracticeDate: json['lastPracticeDate'] != null
          ? DateTime.parse(json['lastPracticeDate'] as String)
          : null,
      masteredWords: List<String>.from(json['masteredWords'] ?? []),
      mascotStage: json['mascotStage'] as int? ?? 1,
    );
  }

  Map<String, dynamic> toJson() => {
    return {
      'region': region,
      'childName': childName,
      'currentPhase': currentPhase,
      'currentLetterIndex': currentLetterIndex,
      'letterStars': letterStars,
      'streakDays': streakDays,
      'lastPracticeDate': lastPracticeDate?.toIso8601String(),
      'masteredWords': masteredWords,
      'mascotStage': mascotStage,
    };
  }

  String toJsonString() => jsonEncode(toJson());

  factory UserProgressModel.fromJsonString(String jsonStr) {
    final json = jsonDecode(jsonStr) as Map<String, dynamic>;
    return UserProgressModel.fromJson(json);
  }

  // Helpers
  int get totalStars => letterStars.values.fold(0, (sum, s) => sum + s);

  double get progressPercent {
    // Total letters across all phases
    const totalLetters = 26; // Approximate
    final completed = letterStars.values.where((s) => s > 0).length;
    return completed / totalLetters;
  }

  bool isLetterCompleted(String letter) => (letterStars[letter] ?? 0) > 0;

  void updateMascotStage() {
    final total = totalStars;
    if (total >= 30) {
      mascotStage = 5;
    } else if (total >= 20) {
      mascotStage = 4;
    } else if (total >= 12) {
      mascotStage = 3;
    } else if (total >= 5) {
      mascotStage = 2;
    } else {
      mascotStage = 1;
    }
  }

  void updateStreak() {
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month}-${today.day}';

    if (lastPracticeDate == null) {
      streakDays = 1;
      lastPracticeDate = today;
      return;
    }

    final last = '${lastPracticeDate!.year}-${lastPracticeDate!.month}-${lastPracticeDate!.day}';
    final yesterday = today.subtract(const Duration(days: 1));
    final yesterdayStr = '${yesterday.year}-${yesterday.month}-${yesterday.day}';

    if (todayStr == last) {
      // Already practiced today
      return;
    } else if (yesterdayStr == last) {
      // Practiced yesterday, continue streak
      streakDays++;
    } else {
      // Streak broken, start new
      streakDays = 1;
    }

    lastPracticeDate = today;
  }

  UserProgressModel copyWith({
    String? region,
    String? childName,
    int? currentPhase,
    int? currentLetterIndex,
    Map<String, int>? letterStars,
    int? streakDays,
    DateTime? lastPracticeDate,
    List<String>? masteredWords,
    int? mascotStage,
  }) {
    return UserProgressModel(
      region: region ?? this.region,
      childName: childName ?? this.childName,
      currentPhase: currentPhase ?? this.currentPhase,
      currentLetterIndex: currentLetterIndex ?? this.currentLetterIndex,
      letterStars: letterStars ?? this.letterStars,
      streakDays: streakDays ?? this.streakDays,
      lastPracticeDate: lastPracticeDate ?? this.lastPracticeDate,
      masteredWords: masteredWords ?? this.masteredWords,
      mascotStage: mascotStage ?? this.mascotStage,
    );
  }
}
