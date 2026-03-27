import 'package:flutter/foundation.dart';
import 'dart:convert';
import '../data/phonics_data.dart';
import 'storage_service.dart';

class ProgressService extends ChangeNotifier {
  final StorageService _storage;

  String _region = 'au';
  String _childName = 'Friend';
  int _currentPhase = 1;
  int _currentLetterIndex = 0;
  Map<String, int> _letterStars = {};
  int _streakDays = 0;
  String? _lastPracticeDate;
  List<String> _masteredWords = [];
  int _mascotStage = 1;

  ProgressService(this._storage);

  // Getters
  String get region => _region;
  String get childName => _childName;
  int get currentPhase => _currentPhase;
  int get currentLetterIndex => _currentLetterIndex;
  Map<String, int> get letterStars => _letterStars;
  int get streakDays => _streakDays;
  List<String> get masteredWords => _masteredWords;
  int get mascotStage => _mascotStage;
  int get totalStars => _letterStars.values.fold(0, (sum, stars) => sum + stars);

  // Current letter
  Map<String, dynamic> get currentLetter {
    final phaseData = _currentPhase == 1
        ? PhonicsData.satpinPhase1
        : _currentPhase == 2
            ? PhonicsData.phase2
            : [];
    if (_currentLetterIndex < phaseData.length) {
      return phaseData[_currentLetterIndex];
    }
    return {};
  }

  // Progress percentage
  double get progressPercent {
    final allLetters = PhonicsData.satpinPhase1.length + PhonicsData.phase2.length;
    if (allLetters == 0) return 0.0;
    final completed = _letterStars.values.where((s) => s > 0).length;
    return completed / allLetters;
  }

  // Load from storage
  Future<void> loadProgress() async {
    _region = _storage.getRegion() ?? 'au';
    _childName = _storage.getChildName() ?? 'Friend';
    _currentPhase = _storage.getCurrentPhase();
    _currentLetterIndex = _storage.getCurrentLetterIndex();
    _streakDays = _storage.getStreak();
    _lastPracticeDate = _storage.getLastPractice();
    _masteredWords = _storage.getMasteredWords();

    // Load letter stars
    for (final letterData in PhonicsData.allLetters) {
      final letter = letterData['letter'] as String;
      _letterStars[letter] = _storage.getLetterStars(letter);
    }

    // Calculate mascot stage based on stars
    _updateMascotStage();

    notifyListeners();
  }

  // Save to storage
  Future<void> _save() async {
    await _storage.setRegion(_region);
    await _storage.setChildName(_childName);
    await _storage.setCurrentPhase(_currentPhase);
    await _storage.setCurrentLetterIndex(_currentLetterIndex);
    await _storage.setStreak(_streakDays);
    if (_lastPracticeDate != null) {
      await _storage.setLastPractice(_lastPracticeDate!);
    }

    for (final entry in _letterStars.entries) {
      await _storage.setLetterStars(entry.key, entry.value);
    }

    notifyListeners();
  }

  // Update region
  Future<void> setRegion(String region) async {
    _region = region;
    await _storage.setRegion(region);
    notifyListeners();
  }

  // Update child name
  Future<void> setChildName(String name) async {
    _childName = name;
    await _storage.setChildName(name);
    notifyListeners();
  }

  // Record letter completion
  Future<void> completeLetter(String letter, int stars) async {
    _letterStars[letter] = stars;
    await _storage.setLetterStars(letter, stars);
    _updateMascotStage();
    _updateStreak();
    await _save();
  }

  // Move to next letter
  Future<void> nextLetter() async {
    final currentList = _currentPhase == 1
        ? PhonicsData.satpinPhase1
        : PhonicsData.phase2;

    if (_currentLetterIndex < currentList.length - 1) {
      _currentLetterIndex++;
    } else if (_currentPhase == 1) {
      _currentPhase = 2;
      _currentLetterIndex = 0;
    }

    await _save();
  }

  // Add mastered word
  Future<void> addMasteredWord(String word) async {
    await _storage.addMasteredWord(word);
    _masteredWords = _storage.getMasteredWords();
    _updateStreak();
    notifyListeners();
  }

  // Update streak
  void _updateStreak() {
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month}-${today.day}';

    if (_lastPracticeDate == null) {
      _streakDays = 1;
      _lastPracticeDate = todayStr;
      return;
    }

    final last = DateTime.parse(_lastPracticeDate!);
    final yesterday = today.subtract(const Duration(days: 1));

    if (todayStr == _lastPracticeDate) {
      // Already practiced today
      return;
    } else if ('${yesterday.year}-${yesterday.month}-${yesterday.day}' ==
        _lastPracticeDate) {
      _streakDays++;
    } else {
      _streakDays = 1;
    }

    _lastPracticeDate = todayStr;
  }

  // Update mascot stage based on progress
  void _updateMascotStage() {
    final total = totalStars;
    if (total >= 30) {
      _mascotStage = 5;
    } else if (total >= 20) {
      _mascotStage = 4;
    } else if (total >= 12) {
      _mascotStage = 3;
    } else if (total >= 5) {
      _mascotStage = 2;
    } else {
      _mascotStage = 1;
    }
  }

  // Get letters for current phase
  List<Map<String, dynamic>> getCurrentPhaseLetters() {
    return _currentPhase == 1 ? PhonicsData.satpinPhase1 : PhonicsData.phase2;
  }

  // Stars for a specific letter
  int getLetterStars(String letter) {
    return _letterStars[letter] ?? 0;
  }

  // Is letter completed?
  bool isLetterCompleted(String letter) {
    return (_letterStars[letter] ?? 0) > 0;
  }

  // Reset progress
  Future<void> resetProgress() async {
    await _storage.clearAll();
    _region = 'au';
    _childName = 'Friend';
    _currentPhase = 1;
    _currentLetterIndex = 0;
    _letterStars = {};
    _streakDays = 0;
    _lastPracticeDate = null;
    _masteredWords = [];
    _mascotStage = 1;
    notifyListeners();
  }
}
