import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class StorageService {
  SharedPreferences? _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // Region selection
  Future<void> setRegion(String region) async {
    await _prefs?.setString('region', region);
  }

  String? getRegion() {
    return _prefs?.getString('region');
  }

  // Child name
  Future<void> setChildName(String name) async {
    await _prefs?.setString('child_name', name);
  }

  String? getChildName() {
    return _prefs?.getString('child_name');
  }

  // Progress data
  Future<void> saveProgress(Map<String, dynamic> progress) async {
    final jsonStr = jsonEncode(progress);
    await _prefs?.setString('progress', jsonStr);
  }

  Map<String, dynamic>? getProgress() {
    final jsonStr = _prefs?.getString('progress');
    if (jsonStr == null) return null;
    try {
      return jsonDecode(jsonStr) as Map<String, dynamic>;
    } catch (e) {
      print('Error decoding progress: $e');
      return null;
    }
  }

  // Letter stars (1-3 stars per letter)
  Future<void> setLetterStars(String letter, int stars) async {
    await _prefs?.setInt('stars_$letter', stars);
  }

  int getLetterStars(String letter) {
    return _prefs?.getInt('stars_$letter') ?? 0;
  }

  // Current streak
  Future<void> setStreak(int streak) async {
    await _prefs?.setInt('streak', streak);
  }

  int getStreak() {
    return _prefs?.getInt('streak') ?? 0;
  }

  // Last practice date
  Future<void> setLastPractice(String date) async {
    await _prefs?.setString('last_practice', date);
  }

  String? getLastPractice() {
    return _prefs?.getString('last_practice');
  }

  // Mastered words
  Future<void> addMasteredWord(String word) async {
    final words = getMasteredWords();
    if (!words.contains(word)) {
      words.add(word);
      await _prefs?.setStringList('mastered_words', words);
    }
  }

  List<String> getMasteredWords() {
    return _prefs?.getStringList('mastered_words') ?? [];
  }

  // Current phase/letter position
  Future<void> setCurrentPhase(int phase) async {
    await _prefs?.setInt('current_phase', phase);
  }

  int getCurrentPhase() {
    return _prefs?.getInt('current_phase') ?? 1;
  }

  Future<void> setCurrentLetterIndex(int index) async {
    await _prefs?.setInt('letter_index', index);
  }

  int getCurrentLetterIndex() {
    return _prefs?.getInt('letter_index') ?? 0;
  }

  // Game high scores
  Future<void> setGameHighScore(String game, int score) async {
    await _prefs?.setInt('highscore_$game', score);
  }

  int getGameHighScore(String game) {
    return _prefs?.getInt('highscore_$game') ?? 0;
  }

  // Clear all data (reset)
  Future<void> clearAll() async {
    await _prefs?.clear();
  }
}
