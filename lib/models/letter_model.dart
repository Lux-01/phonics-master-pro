class Letter {
  final String char;
  final String sound;
  final String name;
  final int phase;
  final List<String> exampleWords;
  final Animal animal;
  final bool isVowel;

  const Letter({
    required this.char,
    required this.sound,
    required this.name,
    required this.phase,
    required this.exampleWords,
    required this.animal,
    this.isVowel = false,
  });

  factory Letter.fromJson(Map<String, dynamic> json) {
    return Letter(
      char: json['letter'] as String,
      sound: json['sound'] as String,
      name: json['name'] ?? json['letter'],
      phase: json['phase'] as int? ?? 1,
      exampleWords: List<String>.from(json['exampleWords'] ?? []),
      animal: Animal.fromJson(json['animal'] ?? {}),
      isVowel: json['isVowel'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
    'letter': char,
    'sound': sound,
    'name': name,
    'phase': phase,
    'exampleWords': exampleWords,
    'animal': animal.toJson(),
    'isVowel': isVowel,
  };
}

class Animal {
  final String name;
  final String emoji;
  final String action;

  const Animal({
    required this.name,
    required this.emoji,
    required this.action,
  });

  factory Animal.fromJson(Map<String, dynamic> json) {
    return Animal(
      name: json['name'] as String? ?? 'Unknown',
      emoji: json['emoji'] as String? ?? '❓',
      action: json['action'] as String? ?? 'move',
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'emoji': emoji,
    'action': action,
  };
}
