import 'package:flutter/material.dart';
import 'package:hive/hive.dart';

part 'word_tile.g.dart';

@HiveType(typeId: 5)
class WordTile extends HiveObject {
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final String word;
  
  @HiveField(2)
  final String imageAsset;
  
  @HiveField(3)
  final String audioAsset;
  
  @HiveField(4)
  final int difficulty;
  
  @HiveField(5)
  final List<String> phonemes;
  
  @HiveField(6)
  final String? category;
  
  @HiveField(7)
  bool isLearned;
  
  @HiveField(8)
  int practiceCount;
  
  WordTile({
    required this.id,
    required this.word,
    required this.imageAsset,
    required this.audioAsset,
    this.difficulty = 1,
    required this.phonemes,
    this.category,
    this.isLearned = false,
    this.practiceCount = 0,
  });
  
  void markAsLearned() {
    isLearned = true;
    practiceCount++;
  }
  
  void incrementPractice() {
    practiceCount++;
  }
  
  String get displayWord => word.toUpperCase();
  
  String get firstLetter => word[0].toUpperCase();
  
  String get lastLetter => word[word.length - 1].toLowerCase();
  
  int get letterCount => word.length;
  
  bool get isCVC => phonemes.length == 3 && 
    !['a', 'e', 'i', 'o', 'u'].contains(phonemes[0]) &&
    ['a', 'e', 'i', 'o', 'u'].contains(phonemes[1]) &&
    !['a', 'e', 'i', 'o', 'u'].contains(phonemes[2]);
}

// Predefined word library
class WordLibrary {
  static List<WordTile> get allWords => [
    // Level 1: CVC Words (a)
    WordTile(
      id: 'word_cat',
      word: 'cat',
      imageAsset: 'assets/images/words/cat.png',
      audioAsset: 'assets/audio/words/cat.mp3',
      difficulty: 1,
      phonemes: ['c', 'a', 't'],
      category: 'animals',
    ),
    WordTile(
      id: 'word_hat',
      word: 'hat',
      imageAsset: 'assets/images/words/hat.png',
      audioAsset: 'assets/audio/words/hat.mp3',
      difficulty: 1,
      phonemes: ['h', 'a', 't'],
      category: 'clothes',
    ),
    WordTile(
      id: 'word_mat',
      word: 'mat',
      imageAsset: 'assets/images/words/mat.png',
      audioAsset: 'assets/audio/words/mat.mp3',
      difficulty: 1,
      phonemes: ['m', 'a', 't'],
      category: 'house',
    ),
    WordTile(
      id: 'word_rat',
      word: 'rat',
      imageAsset: 'assets/images/words/rat.png',
      audioAsset: 'assets/audio/words/rat.mp3',
      difficulty: 1,
      phonemes: ['r', 'a', 't'],
      category: 'animals',
    ),
    WordTile(
      id: 'word_bat',
      word: 'bat',
      imageAsset: 'assets/images/words/bat.png',
      audioAsset: 'assets/audio/words/bat.mp3',
      difficulty: 1,
      phonemes: ['b', 'a', 't'],
      category: 'animals',
    ),
    // Level 1: CVC Words (e)
    WordTile(
      id: 'word_bed',
      word: 'bed',
      imageAsset: 'assets/images/words/bed.png',
      audioAsset: 'assets/audio/words/bed.mp3',
      difficulty: 1,
      phonemes: ['b', 'e', 'd'],
      category: 'house',
    ),
    WordTile(
      id: 'word_red',
      word: 'red',
      imageAsset: 'assets/images/words/red.png',
      audioAsset: 'assets/audio/words/red.mp3',
      difficulty: 1,
      phonemes: ['r', 'e', 'd'],
      category: 'colors',
    ),
    WordTile(
      id: 'word_hen',
      word: 'hen',
      imageAsset: 'assets/images/words/hen.png',
      audioAsset: 'assets/audio/words/hen.mp3',
      difficulty: 1,
      phonemes: ['h', 'e', 'n'],
      category: 'animals',
    ),
    // Level 1: CVC Words (i)
    WordTile(
      id: 'word_pig',
      word: 'pig',
      imageAsset: 'assets/images/words/pig.png',
      audioAsset: 'assets/audio/words/pig.mp3',
      difficulty: 1,
      phonemes: ['p', 'i', 'g'],
      category: 'animals',
    ),
    WordTile(
      id: 'word_big',
      word: 'big',
      imageAsset: 'assets/images/words/big.png',
      audioAsset: 'assets/audio/words/big.mp3',
      difficulty: 1,
      phonemes: ['b', 'i', 'g'],
      category: 'descriptive',
    ),
    WordTile(
      id: 'word_sit',
      word: 'sit',
      imageAsset: 'assets/images/words/sit.png',
      audioAsset: 'assets/audio/words/sit.mp3',
      difficulty: 1,
      phonemes: ['s', 'i', 't'],
      category: 'actions',
    ),
    // Level 1: CVC Words (o)
    WordTile(
      id: 'word_dog',
      word: 'dog',
      imageAsset: 'assets/images/words/dog.png',
      audioAsset: 'assets/audio/words/dog.mp3',
      difficulty: 1,
      phonemes: ['d', 'o', 'g'],
      category: 'animals',
    ),
    WordTile(
      id: 'word_log',
      word: 'log',
      imageAsset: 'assets/images/words/log.png',
      audioAsset: 'assets/audio/words/log.mp3',
      difficulty: 1,
      phonemes: ['l', 'o', 'g'],
      category: 'nature',
    ),
    WordTile(
      id: 'word_mop',
      word: 'mop',
      imageAsset: 'assets/images/words/mop.png',
      audioAsset: 'assets/audio/words/mop.mp3',
      difficulty: 1,
      phonemes: ['m', 'o', 'p'],
      category: 'house',
    ),
    // Level 1: CVC Words (u)
    WordTile(
      id: 'word_sun',
      word: 'sun',
      imageAsset: 'assets/images/words/sun.png',
      audioAsset: 'assets/audio/words/sun.mp3',
      difficulty: 1,
      phonemes: ['s', 'u', 'n'],
      category: 'nature',
    ),
    WordTile(
      id: 'word_bun',
      word: 'bun',
      imageAsset: 'assets/images/words/bun.png',
      audioAsset: 'assets/audio/words/bun.mp3',
      difficulty: 1,
      phonemes: ['b', 'u', 'n'],
      category: 'food',
    ),
    WordTile(
      id: 'word_cup',
      word: 'cup',
      imageAsset: 'assets/images/words/cup.png',
      audioAsset: 'assets/audio/words/cup.mp3',
      difficulty: 1,
      phonemes: ['c', 'u', 'p'],
      category: 'house',
    ),
    
    // Level 2: Easy Words
    WordTile(
      id: 'word_ball',
      word: 'ball',
      imageAsset: 'assets/images/words/ball.png',
      audioAsset: 'assets/audio/words/ball.mp3',
      difficulty: 2,
      phonemes: ['b', 'a', 'll'],
      category: 'toys',
    ),
    WordTile(
      id: 'word_apple',
      word: 'apple',
      imageAsset: 'assets/images/words/apple.png',
      audioAsset: 'assets/audio/words/apple.mp3',
      difficulty: 2,
      phonemes: ['a', 'p', 'p', 'l', 'e'],
      category: 'food',
    ),
    WordTile(
      id: 'word_fish',
      word: 'fish',
      imageAsset: 'assets/images/words/fish.png',
      audioAsset: 'assets/audio/words/fish.mp3',
      difficulty: 2,
      phonemes: ['f', 'i', 'sh'],
      category: 'animals',
    ),
    WordTile(
      id: 'word_duck',
      word: 'duck',
      imageAsset: 'assets/images/words/duck.png',
      audioAsset: 'assets/audio/words/duck.mp3',
      difficulty: 2,
      phonemes: ['d', 'u', 'ck'],
      category: 'animals',
    ),
    WordTile(
      id: 'word_bird',
      word: 'bird',
      imageAsset: 'assets/images/words/bird.png',
      audioAsset: 'assets/audio/words/bird.mp3',
      difficulty: 2,
      phonemes: ['b', 'ir', 'd'],
      category: 'animals',
    ),
    WordTile(
      id: 'word_tree',
      word: 'tree',
      imageAsset: 'assets/images/words/tree.png',
      audioAsset: 'assets/audio/words/tree.mp3',
      difficulty: 2,
      phonemes: ['t', 'r', 'ee'],
      category: 'nature',
    ),
    
    // Level 3: Sight Words
    WordTile(
      id: 'word_the',
      word: 'the',
      imageAsset: 'assets/images/words/the.png',
      audioAsset: 'assets/audio/words/the.mp3',
      difficulty: 3,
      phonemes: ['th', 'e'],
      category: 'sight_words',
    ),
    WordTile(
      id: 'word_and',
      word: 'and',
      imageAsset: 'assets/images/words/and.png',
      audioAsset: 'assets/audio/words/and.mp3',
      difficulty: 3,
      phonemes: ['a', 'n', 'd'],
      category: 'sight_words',
    ),
    WordTile(
      id: 'word_is',
      word: 'is',
      imageAsset: 'assets/images/words/is.png',
      audioAsset: 'assets/audio/words/is.mp3',
      difficulty: 3,
      phonemes: ['i', 's'],
      category: 'sight_words',
    ),
    WordTile(
      id: 'word_it',
      word: 'it',
      imageAsset: 'assets/images/words/it.png',
      audioAsset: 'assets/audio/words/it.mp3',
      difficulty: 3,
      phonemes: ['i', 't'],
      category: 'sight_words',
    ),
    WordTile(
      id: 'word_you',
      word: 'you',
      imageAsset: 'assets/images/words/you.png',
      audioAsset: 'assets/audio/words/you.mp3',
      difficulty: 3,
      phonemes: ['y', 'ou'],
      category: 'sight_words',
    ),
  ];
  
  static List<WordTile> getByDifficulty(int difficulty) {
    return allWords.where((w) => w.difficulty == difficulty).toList();
  }
  
  static List<WordTile> getByCategory(String category) {
    return allWords.where((w) => w.category == category).toList();
  }
  
  static List<WordTile> getByPhoneme(String phoneme) {
    return allWords.where((w) => w.phonemes.contains(phoneme.toLowerCase())).toList();
  }
  
  static List<String> get categories {
    return allWords.map((w) => w.category).whereType<String>().toSet().toList();
  }
  
  static WordTile? getById(String id) {
    try {
      return allWords.firstWhere((w) => w.id == id);
    } catch (e) {
      return null;
    }
  }
}

// LessonStep model - updated with Hive support
@HiveType(typeId: 6)
class LessonStep extends HiveObject {
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final String type;
  
  @HiveField(2)
  final String? title;
  
  @HiveField(3)
  final String? content;
  
  @HiveField(4)
  final String? audioAsset;
  
  @HiveField(5)
  final String? imageAsset;
  
  @HiveField(6)
  final String? letterId;
  
  @HiveField(7)
  final String? wordId;
  
  @HiveField(8)
  final List<String>? options;
  
  @HiveField(9)
  final String? correctAnswer;
  
  @HiveField(10)
  bool isCompleted;
  
  @HiveField(11)
  int attempts;
  
  LessonStep({
    required this.id,
    required this.type,
    this.title,
    this.content,
    this.audioAsset,
    this.imageAsset,
    this.letterId,
    this.wordId,
    this.options,
    this.correctAnswer,
    this.isCompleted = false,
    this.attempts = 0,
  });
  
  void complete() {
    isCompleted = true;
  }
  
  void incrementAttempts() {
    attempts++;
  }
  
  bool get isInteractive => ['match', 'trace', 'spell', 'pronounce'].contains(type);
  
  bool get requiresAudio => ['listen', 'pronounce', 'blend'].contains(type);
}