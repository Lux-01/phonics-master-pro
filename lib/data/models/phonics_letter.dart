import 'dart:ui' as ui;

import 'package:flutter/material.dart';

class PhonicsLetter {
  final String letter;
  final String sound;
  final String exampleWord;
  final String? audioAsset;
  final String? exampleImageAsset;
  final bool isVowel;
  final int strokeCount;
  final List<Path> strokePaths;
  final Color color;
  
  PhonicsLetter({
    required this.letter,
    required this.sound,
    required this.exampleWord,
    this.audioAsset,
    this.exampleImageAsset,
    this.isVowel = false,
    this.strokeCount = 1,
    this.strokePaths = const [],
    this.color = const Color(0xFF6B6B),
  });
  
  // Stroke paths for tracing - simplified versions
  Path getDisplayPath() {
    return strokePaths.isNotEmpty ? strokePaths[0] : _generateDefaultPath();
  }
  
  Path _generateDefaultPath() {
    final path = Path();
    // Default simple path
    path.moveTo(0, 100);
    path.lineTo(50, 0);
    path.lineTo(100, 100);
    return path;
  }
  
  // All 26 letters
  static List<PhonicsLetter> get allLetters => [
    // A
    PhonicsLetter(
      letter: 'A',
      sound: '/æ/',
      exampleWord: 'apple',
      audioAsset: 'assets/audio/sounds/a_sound.mp3',
      exampleImageAsset: 'assets/images/words/apple.png',
      isVowel: true,
      strokeCount: 3,
      color: const Color(0xFFFF6B6B),
    ),
    // B
    PhonicsLetter(
      letter: 'B',
      sound: '/b/',
      exampleWord: 'ball',
      audioAsset: 'assets/audio/sounds/b_sound.mp3',
      exampleImageAsset: 'assets/images/words/ball.png',
      strokeCount: 2,
      color: const Color(0xFF4ECDC4),
    ),
    // C
    PhonicsLetter(
      letter: 'C',
      sound: '/k/',
      exampleWord: 'cat',
      audioAsset: 'assets/audio/sounds/c_sound.mp3',
      exampleImageAsset: 'assets/images/words/cat.png',
      strokeCount: 1,
      color: const Color(0xFF9B59B6),
    ),
    // D
    PhonicsLetter(
      letter: 'D',
      sound: '/d/',
      exampleWord: 'dog',
      audioAsset: 'assets/audio/sounds/d_sound.mp3',
      exampleImageAsset: 'assets/images/words/dog.png',
      strokeCount: 2,
      color: const Color(0xFFE67E22),
    ),
    // E
    PhonicsLetter(
      letter: 'E',
      sound: '/e/',
      exampleWord: 'elephant',
      audioAsset: 'assets/audio/sounds/e_sound.mp3',
      exampleImageAsset: 'assets/images/words/elephant.png',
      isVowel: true,
      strokeCount: 4,
      color: const Color(0xFF3498DB),
    ),
    // F
    PhonicsLetter(
      letter: 'F',
      sound: '/f/',
      exampleWord: 'fish',
      audioAsset: 'assets/audio/sounds/f_sound.mp3',
      exampleImageAsset: 'assets/images/words/fish.png',
      strokeCount: 3,
      color: const Color(0xFF1ABC9C),
    ),
    // G
    PhonicsLetter(
      letter: 'G',
      sound: '/g/',
      exampleWord: 'goat',
      audioAsset: 'assets/audio/sounds/g_sound.mp3',
      exampleImageAsset: 'assets/images/words/goat.png',
      strokeCount: 2,
      color: const Color(0xFFF39C12),
    ),
    // H
    PhonicsLetter(
      letter: 'H',
      sound: '/h/',
      exampleWord: 'hat',
      audioAsset: 'assets/audio/sounds/h_sound.mp3',
      exampleImageAsset: 'assets/images/words/hat.png',
      strokeCount: 3,
      color: const Color(0xFF34495E),
    ),
    // I
    PhonicsLetter(
      letter: 'I',
      sound: '/ɪ/',
      exampleWord: 'igloo',
      audioAsset: 'assets/audio/sounds/i_sound.mp3',
      exampleImageAsset: 'assets/images/words/igloo.png',
      isVowel: true,
      strokeCount: 3,
      color: const Color(0xFF16A085),
    ),
    // J
    PhonicsLetter(
      letter: 'J',
      sound: '/dʒ/',
      exampleWord: 'jam',
      audioAsset: 'assets/audio/sounds/j_sound.mp3',
      exampleImageAsset: 'assets/images/words/jam.png',
      strokeCount: 1,
      color: const Color(0xFF27AE60),
    ),
    // K
    PhonicsLetter(
      letter: 'K',
      sound: '/k/',
      exampleWord: 'kite',
      audioAsset: 'assets/audio/sounds/k_sound.mp3',
      exampleImageAsset: 'assets/images/words/kite.png',
      strokeCount: 3,
      color: const Color(0xFF2980B9),
    ),
    // L
    PhonicsLetter(
      letter: 'L',
      sound: '/l/',
      exampleWord: 'lion',
      audioAsset: 'assets/audio/sounds/l_sound.mp3',
      exampleImageAsset: 'assets/images/words/lion.png',
      strokeCount: 2,
      color: const Color(0xFF8E44AD),
    ),
    // M
    PhonicsLetter(
      letter: 'M',
      sound: '/m/',
      exampleWord: 'moon',
      audioAsset: 'assets/audio/sounds/m_sound.mp3',
      exampleImageAsset: 'assets/images/words/moon.png',
      strokeCount: 4,
      color: const Color(0xFFD35400),
    ),
    // N-Z continue...
    // ... add remaining letters
  ];
  
  String get lowerCase => letter.toLowerCase();
  
  String get displaySound => sound;
  
  String get fullExample => '$exampleWord (${sound})';
}

// Extension for color utilities
extension ColorExtension on PhonicsLetter {
  Color get backgroundColor => color.withOpacity(0.1);
  Color get borderColor => color;
  Gradient get gradient => LinearGradient(
    colors: [color.withOpacity(0.3), color.withOpacity(0.1)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
