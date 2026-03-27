import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/progress_service.dart';
import '../data/phonics_data.dart';

class ProgressScreen extends StatelessWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Progress 📈'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Consumer<ProgressService>(
        builder: (context, progress, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Stats Cards
                Row(
                  children: [
                    Expanded(
                      child: _StatCard(
                        icon: '⭐',
                        value: '${progress.totalStars}',
                        label: 'Total Stars',
                        color: const Color(0xFFFFD700),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _StatCard(
                        icon: '🔥',
                        value: '${progress.streakDays}',
                        label: 'Day Streak',
                        color: Colors.orange,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _StatCard(
                        icon: '📚',
                        value:'${(progress.progressPercent * 100).toInt()}%',
                        label: 'Complete',
                        color: const Color(0xFF6C63FF),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 30),

                // Progress Bar Section
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
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '🎯 Learning Progress',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 15),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: LinearProgressIndicator(
                          value: progress.progressPercent,
                          minHeight: 20,
                          backgroundColor: Colors.grey[200],
                          valueColor: const AlwaysStoppedAnimation<Color>(
                            Color(0xFF6C63FF),
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            '${progress.letterStars.values.where((s) => s > 0).length} / ${PhonicsData.allLetters.length} letters',
                            style: TextStyle(
                              color: Colors.grey[600],
                            ),
                          ),
                          Text(
                            '${progress.masteredWords.length} words learned',
                            style: TextStyle(
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 30),

                // Phase 1 Progress
                const Text(
                  '📖 Phase 1: SATPIN Letters',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 15),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: PhonicsData.satpinPhase1.map((letterData) {
                    final letter = letterData['letter'] as String;
                    final stars = progress.getLetterStars(letter);
                    return _MiniLetterCard(
                      letter: letter,
                      stars: stars,
                    );
                  }).toList(),
                ),
                const SizedBox(height: 30),

                // Phase 2 Progress
                const Text(
                  '📖 Phase 2: Next Letters',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 15),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: PhonicsData.phase2.map((letterData) {
                    final letter = letterData['letter'] as String;
                    final stars = progress.getLetterStars(letter);
                    return _MiniLetterCard(
                      letter: letter,
                      stars: stars,
                    );
                  }).toList(),
                ),
                const SizedBox(height: 30),

                // Words Learned
                if (progress.masteredWords.isNotEmpty) ...[
                  const Text(
                    '📝 Words You Can Read',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 15),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: progress.masteredWords
                        .map((word) => Chip(
                              label: Text(
                                word.toUpperCase(),
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              backgroundColor:
                                  const Color(0xFF6C63FF).withOpacity(0.1),
                              side: BorderSide(
                                color:
                                    const Color(0xFF6C63FF).withOpacity(0.3),
                              ),
                            ))
                        .toList(),
                  ),
                  const SizedBox(height: 30),
                ],

                // Mascot Growth
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        const Color(0xFF6C63FF).withOpacity(0.1),
                        const Color(0xFF00BFA6).withOpacity(0.1),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    children: [
                      const Text(
                        '🦜 Your Learning Buddy',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 15),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              children: [
                                Text(
                                  _getMascotEmoji(progress.mascotStage),
                                  style: const TextStyle(fontSize: 60),
                                ),
                                const SizedBox(height: 10),
                                Text(
                                  'Stage ${progress.mascotStage}/5',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 15),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _getMascotTitle(progress.mascotStage),
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  _getMascotMessage(progress.mascotStage),
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey[600],
                                  ),
                                ),
                                const SizedBox(height: 10),
                                Text(
                                  '${5 - progress.mascotStage} more stars to grow!',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[500],
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 30),

                // Reset Button
                Center(
                  child: TextButton.icon(
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (context) => AlertDialog(
                          title: const Text('Reset Progress?'),
                          content: const Text(
                            'This will delete all your stars and progress. This cannot be undone.',
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context),
                              child: const Text('Cancel'),
                            ),
                            TextButton(
                              onPressed: () async {
                                await progress.resetProgress();
                                if (mounted) {
                                  Navigator.pop(context);
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content:
                                          Text('Progress reset successfully'),
                                    ),
                                  );
                                }
                              },
                              child: const Text(
                                'Reset',
                                style: TextStyle(color: Colors.red),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                    icon: const Icon(Icons.restart_alt, color: Colors.red),
                    label: const Text(
                      'Reset All Progress',
                      style: TextStyle(color: Colors.red),
                    ),
                  ),
                ),
                const SizedBox(height: 30),
              ],
            ),
          );
        },
      ),
    );
  }

  String _getMascotEmoji(int stage) {
    const emojis = ['🥚', '🐣', '🐥', '🐤', '🦅'];
    return emojis[stage.clamp(0, 4)];
  }

  String _getMascotTitle(int stage) {
    const titles = [
      'Little Egg',
      'Hatching Chick',
      'Baby Bird',
      'Growing Chick',
      'Master Owl'
    ];
    return titles[stage.clamp(0, 4)];
  }

  String _getMascotMessage(int stage) {
    const messages = [
      'I\'m waiting to hatch!',
      'I\'m breaking out!',
      'Learning to fly!',
      'Getting stronger!',
      'Master reader! 🎉'
    ];
    return messages[stage.clamp(0, 4)];
  }
}

class _StatCard extends StatelessWidget {
  final String icon;
  final String value;
  final String label;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        children: [
          Text(icon, style: const TextStyle(fontSize: 32)),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

class _MiniLetterCard extends StatelessWidget {
  final String letter;
  final int stars;

  const _MiniLetterCard({required this.letter, required this.stars});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 50,
      height: 60,
      decoration: BoxDecoration(
        color: stars > 0 ? const Color(0xFF6C63FF).withOpacity(0.1) : Colors.grey[100],
        borderRadius: BorderRadius.circular(10),
        border: stars > 0
            ? Border.all(color: const Color(0xFF6C63FF))
            : Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            letter,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: stars > 0 ? const Color(0xFF6C63FF) : Colors.grey,
            ),
          ),
          const SizedBox(height: 2),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(
              3,
              (i) => Icon(
                i < stars ? Icons.star : Icons.star_border,
                size: 10,
                color: i < stars ? Colors.amber : Colors.grey[300],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
