import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/audio_service.dart';
import '../services/progress_service.dart';
import '../data/phonics_data.dart';
import 'package:confetti/confetti.dart';

class WordBuilderScreen extends StatefulWidget {
  const WordBuilderScreen({super.key});

  @override
  State<WordBuilderScreen> createState() => _WordBuilderScreenState();
}

class _WordBuilderScreenState extends State<WordBuilderScreen>
    with TickerProviderStateMixin {
  late ConfettiController _confettiController;
  String? _currentWord;
  List<String> _wordLetters = [];
  List<String> _availableLetters = [];
  int _score = 0;
  int _wordsCompleted = 0;

  @override
  void initState() {
    super.initState();
    _confettiController = ConfettiController(
      duration: const Duration(seconds: 2),
    );
    _selectNewWord();
  }

  void _selectNewWord() {
    final words = PhonicsData.phase1CVCWords;
    final random = DateTime.now().millisecondsSinceEpoch % words.length;
    _currentWord = words[random]['word'] as String;
    _wordLetters = List.filled(3, '');
    _availableLetters = _currentWord!.split('')..shuffle();
  }

  void _placeLetter(int slotIndex, String letter) {
    setState(() {
      _wordLetters[slotIndex] = letter;
      _availableLetters.remove(letter);
    });

    // Check if word is complete
    if (_wordLetters.join() == _currentWord) {
      _wordCompleted();
    }
  }

  void _removeLetter(int slotIndex) {
    if (_wordLetters[slotIndex].isNotEmpty) {
      setState(() {
        _availableLetters.add(_wordLetters[slotIndex]);
        _wordLetters[slotIndex] = '';
      });
    }
  }

  Future<void> _wordCompleted() async {
    _confettiController.play();
    _score += 10;
    _wordsCompleted++;

    final audio = context.read<AudioService>();
    await audio.playWord(_currentWord!);
    await audio.playSuccess();

    // Save progress
    context.read<ProgressService>().addMasteredWord(_currentWord!);

    // Show success dialog
    if (mounted) {
      await showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('🎉', style: TextStyle(fontSize: 60)),
              const SizedBox(height: 20),
              Text(
                '"$_currentWord"',
                style: const TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF6C63FF),
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'You read it!',
                style: TextStyle(fontSize: 18),
              ),
              const SizedBox(height: 10),
              Text(
                '+10 points!',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.amber.shade700,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 30),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  setState(() {
                    _selectNewWord();
                  });
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6C63FF),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 40,
                    vertical: 15,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                child: const Text(
                  'Next Word',
                  style: TextStyle(fontSize: 18, color: Colors.white),
                ),
              ),
            ],
          ),
        ),
      );
    }
  }

  Future<void> _soundItOut() async {
    final audio = context.read<AudioService>();
    for (int i = 0; i < _wordLetters.length; i++) {
      if (_wordLetters[i].isNotEmpty) {
        await audio.playLetterSound(_wordLetters[i]);
        await Future.delayed(const Duration(milliseconds: 600));
      }
    }
  }

  @override
  void dispose() {
    _confettiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Word Builder 🧩'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF6C63FF).withOpacity(0.1),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Row(
              children: [
                const Icon(Icons.star, color: Color(0xFF6C63FF), size: 20),
                const SizedBox(width: 4),
                Text(
                  '$_score',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF6C63FF),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  // Instructions
                  Container(
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                      color: Colors.amber.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.lightbulb, color: Colors.amber),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Drag the letters to spell the word!',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.amber.shade800,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 30),

                  // Word Picture/Meaning Display
                  if (_currentWord != null)
                    _buildWordDisplay(),

                  const Spacer(),

                  // Word Slots
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: List.generate(
                      3,
                      (index) => _WordSlot(
                        letter: _wordLetters[index],
                        onTap: () => _removeLetter(index),
                      ),
                    ),
                  ),

                  const SizedBox(height: 30),

                  // Sound It Out Button
                  ElevatedButton.icon(
                    onPressed: _wordLetters.any((l) => l.isNotEmpty) 
                        ? _soundItOut 
                        : null,
                    icon: const Icon(Icons.volume_up),
                    label: const Text('Sound It Out 🔊'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF00BFA6),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 30,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                    ),
                  ),

                  const SizedBox(height: 30),

                  // Available Letters
                  Wrap(
                    spacing: 15,
                    runSpacing: 15,
                    alignment: WrapAlignment.center,
                    children: _availableLetters
                        .map((letter) => _DraggableLetter(
                              letter: letter,
                              onDragComplete: () {
                                // Wait for drag
                              },
                            ))
                        .toList(),
                  ),

                  const Spacer(),
                ],
              ),
            ),
          ),
          // Confetti
          Align(
            alignment: Alignment.topCenter,
            child: ConfettiWidget(
              confettiController: _confettiController,
              blastDirectionality: BlastDirectionality.explosive,
              shouldLoop: false,
              colors: const [
                Colors.green,
                Colors.blue,
                Colors.pink,
                Colors.orange,
                Colors.purple
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWordDisplay() {
    final wordData = PhonicsData.phase1CVCWords.firstWhere(
      (w) => w['word'] == _currentWord,
      orElse: () => {'image': '❓', 'meaning': 'Unknown word'},
    );

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            wordData['image'] as String,
            style: const TextStyle(fontSize: 60),
          ),
          const SizedBox(height: 10),
          Text(
            wordData['meaning'] as String,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

class _WordSlot extends StatelessWidget {
  final String letter;
  final VoidCallback onTap;

  const _WordSlot({required this.letter, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return DragTarget<String>(
      onAccept: (draggedLetter) {
        onTap();
        // The slot will be filled via parent state
      },
      builder: (context, candidateData, rejectedData) {
        return GestureDetector(
          onTap: letter.isNotEmpty ? onTap : null,
          child: Container(
            width: 80,
            height: 100,
            decoration: BoxDecoration(
              color: letter.isEmpty
                  ? Colors.grey[200]
                  : const Color(0xFF6C63FF).withOpacity(0.2),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(
                color: letter.isEmpty
                    ? Colors.grey[400]!
                    : const Color(0xFF6C63FF),
                width: letter.isEmpty ? 2 : 3,
              ),
              boxShadow: letter.isNotEmpty
                  ? [
                      BoxShadow(
                        color: const Color(0xFF6C63FF).withOpacity(0.3),
                        blurRadius: 10,
                      ),
                    ]
                  : null,
            ),
            child: Center(
              child: letter.isEmpty
                  ? Icon(Icons.add, size: 30, color: Colors.grey[400])
                  : Text(
                      letter.toUpperCase(),
                      style: const TextStyle(
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF6C63FF),
                      ),
                    ),
            ),
          ),
        );
      },
    );
  }
}

class _DraggableLetter extends StatelessWidget {
  final String letter;
  final VoidCallback onDragComplete;

  const _DraggableLetter({
    required this.letter,
    required this.onDragComplete,
  });

  @override
  Widget build(BuildContext context) {
    return Draggable<String>(
      data: letter,
      feedback: _LetterCard(letter: letter, isDragging: true),
      childWhenDragging: Opacity(
        opacity: 0.3,
        child: _LetterCard(letter: letter, isDragging: false),
      ),
      onDragCompleted: onDragComplete,
      child: _LetterCard(letter: letter, isDragging: false),
    );
  }
}

class _LetterCard extends StatelessWidget {
  final String letter;
  final bool isDragging;

  const _LetterCard({
    required this.letter,
    required this.isDragging,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 60,
      height: 80,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF6C63FF), Color(0xFF00BFA6)],
        ),
        borderRadius: BorderRadius.circular(15),
        boxShadow: isDragging
            ? [
                BoxShadow(
                  color: const Color(0xFF6C63FF).withOpacity(0.5),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ]
            : [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
      ),
      child: Center(
        child: Text(
          letter.toUpperCase(),
          style: TextStyle(
            fontSize: 36,
            fontWeight: FontWeight.bold,
            color: Colors.white.withOpacity(isDragging ? 0.9 : 1.0),
          ),
        ),
      ),
    );
  }
}
