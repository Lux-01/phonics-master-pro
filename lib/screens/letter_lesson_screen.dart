import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/audio_service.dart';
import '../services/progress_service.dart';
import '../data/phonics_data.dart';
import 'package:confetti/confetti.dart';

class LetterLessonScreen extends StatefulWidget {
  final Map<String, dynamic> letterData;
  final int letterIndex;

  const LetterLessonScreen({
    super.key,
    required this.letterData,
    required this.letterIndex,
  });

  @override
  State<LetterLessonScreen> createState() => _LetterLessonScreenState();
}

class _LetterLessonScreenState extends State<LetterLessonScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _letterAnimController;
  late ConfettiController _confettiController;
  int _stars = 0;
  bool _lessonComplete = false;
  int _completedActivities = 0;

  @override
  void initState() {
    super.initState();
    _letterAnimController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _confettiController = ConfettiController(
      duration: const Duration(seconds: 2),
    );

    // Load existing stars
    final progress = context.read<ProgressService>();
    _stars = progress.getLetterStars(widget.letterData['letter']);
    _lessonComplete = _stars > 0;
  }

  void _incrementActivity() {
    setState(() {
      _completedActivities++;
      if (_completedActivities >= 3 && !_lessonComplete) {
        _lessonComplete = true;
        _stars = _stars == 0 ? 1 : _stars;
        _completeLesson();
      }
    });
  }

  Future<void> _completeLesson() async {
    _confettiController.play();
    final progress = context.read<ProgressService>();
    final audio = context.read<AudioService>();

    await audio.playSuccess();

    await progress.completeLetter(widget.letterData['letter'], _stars);
    await progress.nextLetter();

    // Show completion dialog
    if (mounted) {
      Future.delayed(const Duration(milliseconds: 500), () {
        _showCompletionDialog();
      });
    }
  }

  void _showCompletionDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('🌟', style: TextStyle(fontSize: 60)),
            const SizedBox(height: 20),
            const Text(
              'Amazing!',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'You earned ⭐ for letter ${widget.letterData['letter']}!',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pop(context);
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
                'Continue',
                style: TextStyle(fontSize: 18, color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _letterAnimController.dispose();
    _confettiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final letter = widget.letterData['letter'] as String;
    final sound = widget.letterData['sound'] as String;
    final animal = widget.letterData['animal'] as Map<String, dynamic>;
    final exampleWords = widget.letterData['exampleWords'] as List<dynamic>;

    return Scaffold(
      appBar: AppBar(
        title: Text('Letter $letter'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Row(
              children: [
                ...List.generate(
                  3,
                  (i) => Icon(
                    i < _stars ? Icons.star : Icons.star_border,
                    color: i < _stars ? Colors.amber : Colors.grey,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Large Letter Display
                GestureDetector(
                  onTap: () async {
                    _letterAnimController
                        .forward()
                        .then((_) => _letterAnimController.reverse());
                    final audio = context.read<AudioService>();
                    await audio.playLetterSound(letter);
                    _incrementActivity();
                  },
                  child: ScaleTransition(
                    scale: Tween<double>(begin: 1.0, end: 1.1).animate(
                      CurvedAnimation(
                        parent: _letterAnimController,
                        curve: Curves.elasticOut,
                      ),
                    ),
                    child: Container(
                      width: 200,
                      height: 200,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF6C63FF), Color(0xFF00BFA6)],
                        ),
                        borderRadius: BorderRadius.circular(30),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF6C63FF).withOpacity(0.3),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Center(
                        child: Text(
                          letter,
                          style: const TextStyle(
                            fontSize: 120,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // Sound Hint
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 30,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(25),
                  ),
                  child: Text(
                    'says "$sound"',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.amber,
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Tap the letter to hear the sound',
                  style: TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 40),

                // Animal Section
                Container(
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
                        animal['name'],
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 15),
                      Text(
                        animal['emoji'],
                        style: const TextStyle(fontSize: 80),
                      ),
                      const SizedBox(height: 15),
                      Text(
                        '"${animal['name']} ${widget.letterData['action']}"',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.grey[600],
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 30),

                // Example Words
                const Text(
                  'Example Words',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 20),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: exampleWords.map((word) {
                    return _WordChip(
                      word: word.toString(),
                      onTap: () async {
                        final audio = context.read<AudioService>();
                        await audio.playWord(word.toString());
                        _incrementActivity();
                      },
                    );
                  }).toList(),
                ),

                const SizedBox(height: 50),

                // Complete Button
                if (!_lessonComplete)
                  ElevatedButton.icon(
                    onPressed: () async {
                      setState(() {
                        _stars = 3;
                        _lessonComplete = true;
                      });
                      await _completeLesson();
                    },
                    icon: const Icon(Icons.check_circle),
                    label: const Text(
                      'I Can Do This!',
                      style: TextStyle(fontSize: 18),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF00BFA6),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 40,
                        vertical: 15,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                    ),
                  )
                else
                  Container(
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.check_circle, color: Colors.green),
                        SizedBox(width: 10),
                        Text(
                          'Completed! +⭐',
                          style: TextStyle(
                            fontSize: 18,
                            color: Colors.green,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),

                const SizedBox(height: 40),
              ],
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
}

class _WordChip extends StatelessWidget {
  final String word;
  final VoidCallback onTap;

  const _WordChip({required this.word, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF6C63FF).withOpacity(0.1),
          borderRadius: BorderRadius.circular(15),
          border: Border.all(
            color: const Color(0xFF6C63FF).withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.volume_up,
              size: 20,
              color: Color(0xFF6C63FF),
            ),
            const SizedBox(width: 8),
            Text(
              word,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF6C63FF),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
