class CVCWord {
  final String word;
  final String image;
  final String meaning;
  final List<String> phonemes;

  const CVCWord({
    required this.word,
    required this.image,
    required this.meaning,
    required this.phonemes,
  });

  factory CVCWord.fromJson(Map<String, dynamic> json) {
    return CVCWord(
      word: json['word'] as String,
      image: json['image'] as String? ?? '❓',
      meaning: json['meaning'] as String? ?? '',
      phonemes: List<String>.from(
        json['phonemes'] ?? json['word'].toString().split(''),
      ),
    );
  }

  Map<String, dynamic> toJson() => {
    'word': word,
    'image': image,
    'meaning': meaning,
    'phonemes': phonemes,
  };

  // Generate CVC words from SATPIN letters
  static List<String> generateSATPINWords() {
    final satpin = ['S', 'A', 'T', 'P', 'I', 'N'];
    final words = <String>[];
    
    for (var c1 in satpin) {
      for (var v in ['A', 'I']) {
        for (var c2 in satpin) {
          if (c2 != c1) {
            words.add('$c1$v$c2'.toLowerCase());
          }
        }
      }
    }
    
    // Known valid SATPIN words only
    final valid = [
      'sat', 'pat', 'tap', 'nap', 'sap',
      'pin', 'tin', 'sin', 'nip', 'tip', 'sip', 'pip',
      'pan', 'tan', 'tin', 'tan', 'pip',
      'pit', 'sit', 'nip', 'tap', 'nap',
      'ant', 'nap', 'sap', 'nip', 'tin',
      'inn', 'ann', 'pip', 'sip', 'tip',
    ];
    
    return valid.toSet().toList(); // Remove duplicates
  }
}
