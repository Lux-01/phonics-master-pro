import 'package:hive/hive.dart';
import 'package:phonics_master_pro/data/models/phonics_letter.dart';

part 'lesson.g.dart';

@HiveType(typeId: 1)
class Lesson extends HiveObject {
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final String title;
  
  @HiveField(2)
  final String description;
  
  @HiveField(3)
  final int level;
  
  @HiveField(4)
  final List<LessonStep> steps;
  
  @HiveField(5)
  bool isCompleted;
  
  @HiveField(6)
  double progress;
  
  @HiveField(7)
  DateTime? completedAt;
  
  @HiveField(8)
  final String? thumbnailAsset;
  
  @HiveField(9)
  final String colorHex;
  
  @HiveField(10)
  final String iconAsset;
  
  @HiveField(11)
  final int stars;
  
  Lesson({
    required this.id,
    required this.title,
    required this.description,
    required this.level,
    required this.steps,
    this.isCompleted = false,
    this.progress = 0.0,
    this.completedAt,
    this.thumbnailAsset,
    this.colorHex = 'FF6B6B',
    this.iconAsset = 'assets/images/icons/lesson.png',
    this.stars = 0,
  });
}

@HiveType(typeId: 2)
class LessonStep {
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
  final PhonicsLetter? letter;
  
  @HiveField(7)
  final String? word;
  
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
    this.letter,
    this.word,
    this.options,
    this.correctAnswer,
    this.isCompleted = false,
    this.attempts = 0,
  });
}

// Pre-built phonics curriculum
class PhonicsCurriculum {
  static List<Lesson> get allLessons => [
    // Level 1: Single Letters A-M
    Lesson(
      id: 'lesson_a',
      title: 'Letter A',
      description: 'Learn the sound of letter A as in "apple"',
      level: 1,
      colorHex: 'FF6B6B',
      iconAsset: 'assets/images/letters/A.png',
      steps: [
        LessonStep(
          id: 'a_intro',
          type: 'intro',
          title: 'Meet Letter A',
          content: 'The letter A makes the sound /æ/',
          audioAsset: 'assets/audio/sounds/a_sound.mp3',
          imageAsset: 'assets/images/words/apple.png',
          letter: PhonicsLetter.allLetters[0], // 'A'
        ),
        LessonStep(
          id: 'a_listen',
          type: 'listen',
          title: 'Listen to A',
          audioAsset: 'assets/audio/words/apple.mp3',
          imageAsset: 'assets/images/words/apple.png',
          correctAnswer: 'apple',
        ),
        LessonStep(
          id: 'a_trace',
          type: 'trace',
          title: 'Trace Letter A',
          letter: PhonicsLetter.allLetters[0],
        ),
        LessonStep(
          id: 'a_practice',
          type: 'match',
          title: 'Match the Sound',
          options: ['apple', 'ball', 'cat', 'dog'],
          correctAnswer: 'apple',
          audioAsset: 'assets/audio/sounds/a_sound.mp3',
        ),
      ],
    ),
    
    Lesson(
      id: 'lesson_b',
      title: 'Letter B',
      description: 'Learn the sound of letter B as in "ball"',
      level: 1,
      colorHex: '4ECDC4',
      iconAsset: 'assets/images/letters/B.png',
      steps: [
        LessonStep(
          id: 'b_intro',
          type: 'intro',
          title: 'Meet Letter B',
          content: 'The letter B makes the sound /b/',
          audioAsset: 'assets/audio/sounds/b_sound.mp3',
          imageAsset: 'assets/images/words/ball.png',
          letter: PhonicsLetter.allLetters[1], // 'B'
        ),
        LessonStep(
          id: 'b_listen',
          type: 'listen',
          title: 'Listen to B',
          audioAsset: 'assets/audio/words/ball.mp3',
          imageAsset: 'assets/images/words/ball.png',
        ),
        LessonStep(
          id: 'b_trace',
          type: 'trace',
          title: 'Trace Letter B',
          letter: PhonicsLetter.allLetters[1],
        ),
        LessonStep(
          id: 'b_practice',
          type: 'match',
          title: 'Match the Sound',
          options: ['apple', 'ball', 'cat', 'dog'],
          correctAnswer: 'ball',
          audioAsset: 'assets/audio/sounds/b_sound.mp3',
        ),
      ],
    ),
    
    Lesson(
      id: 'lesson_c',
      title: 'Letter C',
      description: 'Learn the sound of letter C as in "cat"',
      level: 1,
      colorHex: 'FFE66D',
      iconAsset: 'assets/images/letters/C.png',
      steps: [
        LessonStep(
          id: 'c_intro',
          type: 'intro',
          title: 'Meet Letter C',
          content: 'The letter C makes the sound /k/',
          audioAsset: 'assets/audio/sounds/c_sound.mp3',
          imageAsset: 'assets/images/words/cat.png',
          letter: PhonicsLetter.allLetters[2],
        ),
        LessonStep(
          id: 'c_listen',
          type: 'listen',
          title: 'Listen to C',
          audioAsset: 'assets/audio/words/cat.mp3',
          imageAsset: 'assets/images/words/cat.png',
        ),
        LessonStep(
          id: 'c_trace',
          type: 'trace',
          title: 'Trace Letter C',
          letter: PhonicsLetter.allLetters[2],
        ),
        LessonStep(
          id: 'c_practice',
          type: 'match',
          title: 'Match the Sound',
          options: ['apple', 'ball', 'cat', 'dog'],
          correctAnswer: 'cat',
          audioAsset: 'assets/audio/sounds/c_sound.mp3',
        ),
      ],
    ),
    
    Lesson(
      id: 'lesson_cat',
      title: 'Word: CAT',
      description: 'Learn to blend sounds C-A-T',
      level: 2,
      colorHex: '9B59B6',
      iconAsset: 'assets/images/words/cat_word.png',
      steps: [
        LessonStep(
          id: 'cat_blend',
          type: 'blend',
          title: 'Blend the Sounds',
          content: 'C-A-T',
          audioAsset: 'assets/audio/words/cat_blend.mp3',
          imageAsset: 'assets/images/words/cat.png',
          word: 'cat',
        ),
        LessonStep(
          id: 'cat_read',
          type: 'read',
          title: 'Read CAT',
          content: 'cat',
          audioAsset: 'assets/audio/words/cat.mp3',
          imageAsset: 'assets/images/words/cat.png',
          word: 'cat',
        ),
        LessonStep(
          id: 'cat_spell',
          type: 'spell',
          title: 'Spell CAT',
          word: 'cat',
          options: ['c', 'a', 't', 'b'],
          correctAnswer: 'cat',
        ),
      ],
    ),
    
    // More lessons...
    Lesson(
      id: 'lesson_d',
      title: 'Letter D',
      description: 'Learn the sound of letter D as in "dog"',
      level: 1,
      colorHex: 'E67E22',
      iconAsset: 'assets/images/letters/D.png',
      steps: [
        LessonStep(
          id: 'd_intro',
          type: 'intro',
          title: 'Meet Letter D',
          content: 'The letter D makes the sound /d/',
          audioAsset: 'assets/audio/sounds/d_sound.mp3',
          imageAsset: 'assets/images/words/dog.png',
          letter: PhonicsLetter.allLetters[3],
        ),
        LessonStep(
          id: 'd_trace',
          type: 'trace',
          title: 'Trace Letter D',
          letter: PhonicsLetter.allLetters[3],
        ),
        LessonStep(
          id: 'd_practice',
          type: 'match',
          title: 'Match the Sound',
          options: ['duck', 'ball', 'cat', 'dog'],
          correctAnswer: 'dog',
        ),
      ],
    ),
  ];
  
  static List<Lesson> getLessonsByLevel(int level) {
    return allLessons.where((l) => l.level == level).toList();
  }
}
