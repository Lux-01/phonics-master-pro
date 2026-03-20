import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:confetti/confetti.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/data/models/lesson.dart';
import 'package:phonics_master_pro/data/models/word_tile.dart';
import 'package:phonics_master_pro/presentation/providers/lesson_provider.dart';
import 'package:phonics_master_pro/presentation/providers/audio_provider.dart';
import 'package:phonics_master_pro/presentation/widgets/letter_card.dart';
import 'package:phonics_master_pro/presentation/widgets/progress_bar.dart';

class LessonScreen extends ConsumerStatefulWidget {
  final String lessonId;

  const LessonScreen({
    super.key,
    required this.lessonId,
  });

  @override
  ConsumerState<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends ConsumerState<LessonScreen>
    with SingleTickerProviderStateMixin {
  late ConfettiController _confettiController;
  late PageController _pageController;
  int _currentStep = 0;
  bool _showingCompletion = false;
  int _earnedStars = 0;
  Map<String, int> _stepAttempts = {};
  
  @override
  void initState() {
    super.initState();
    _confettiController = ConfettiController(duration: const Duration(seconds: 3));
    _pageController = PageController();
    
    // Initialize lesson
    Future(() {
      ref.read(lessonProgressProvider.notifier).startLesson(widget.lessonId);
    });
    
    // Lock orientation
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
  }
  
  @override
  void dispose() {
    _confettiController.dispose();
    _pageController.dispose();
    
    // Reset orientation
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);
    
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lessonAsync = ref.watch(lessonProvider(widget.lessonId));
    final volume = ref.watch(volumeProvider);
    
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: lessonAsync.when(
        data: (lesson) {
          if (lesson == null) {
            return _buildError('Lesson not found');
          }
          
          return _buildLessonContent(lesson);
        },
        loading: () => _buildLoading(),
        error: (_, __) => _buildError('Failed to load lesson'),
      ),
    );
  }
  
  Widget _buildLessonContent(Lesson lesson) {
    final color = Color(int.parse('0xFF${lesson.colorHex}'));
    final currentStepData = lesson.steps[_currentStep];
    final progress = (_currentStep + 1) / lesson.steps.length;
    
    return SafeArea(
      child: Stack(
        children: [
          Column(
            children: [
              // Header
              _buildHeader(lesson, color, progress),
              
              // Progress bar
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                child: CustomProgressBar(
                  progress: progress,
                  height: 8,
                  backgroundColor: Colors.grey[200]!,
                  progressColor: color,
                  borderRadius: 4,
                ),
              ),
              
              // Step content
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  physics: const NeverScrollableScrollPhysics(),
                  onPageChanged: (index) => setState(() => _currentStep = index),
                  itemCount: lesson.steps.length,
                  itemBuilder: (context, index) {
                    return _buildStepContent(lesson.steps[index], color);
                  },
                ),
              ),
              
              // Navigation buttons
              _buildNavigationButtons(lesson, color),
            ],
          ),
          
          // Confetti overlay
          Align(
            alignment: Alignment.topCenter,
            child: ConfettiWidget(
              confettiController: _confettiController,
              blastDirectionality: BlastDirectionality.explosive,
              particleDrag: 0.05,
              emissionFrequency: 0.05,
              numberOfParticles: 50,
              gravity: 0.1,
              colors: const [
                Colors.green,
                Colors.blue,
                Colors.pink,
                Colors.orange,
                Colors.purple,
              ],
            ),
          ),
          
          // Completion overlay
          if (_showingCompletion)
            _buildCompletionOverlay(lesson),
        ],
      ),
    );
  }
  
  Widget _buildHeader(Lesson lesson, Color color, double progress) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
          ),
        ],
      ),
      child: Row(
        children: [
          // Back button
          IconButton(
            onPressed: () => _showExitDialog(),
            icon: const Icon(Icons.arrow_back),
            style: IconButton.styleFrom(
              backgroundColor: Colors.grey[100],
            ),
          ),
          const SizedBox(width: 16),
          
          // Lesson info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  lesson.title,
                  style: GoogleFonts.baloo2(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textColor,
                  ),
                ),
                Text(
                  'Step ${_currentStep + 1} of ${lesson.steps.length}',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: AppTheme.textColor.withOpacity(0.5),
                  ),
                ),
              ],
            ),
          ),
          
          // Volume control
          IconButton(
            onPressed: () {
              final currentVolume = ref.read(volumeProvider);
              ref.read(volumeProvider.notifier).setVolume(
                currentVolume > 0 ? 0 : 1.0,
              );
            },
            icon: Icon(
              volume > 0 ? Icons.volume_up : Icons.volume_off,
              color: AppTheme.textColor,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildStepContent(LessonStep step, Color color) {
    switch (step.type) {
      case 'intro':
        return _buildIntroStep(step, color);
      case 'listen':
        return _buildListenStep(step, color);
      case 'trace':
        return _buildTraceStep(step, color);
      case 'match':
        return _buildMatchStep(step, color);
      case 'blend':
        return _buildBlendStep(step, color);
      case 'read':
        return _buildReadStep(step, color);
      case 'spell':
        return _buildSpellStep(step, color);
      default:
        return _buildGenericStep(step, color);
    }
  }
  
  Widget _buildIntroStep(LessonStep step, Color color) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (step.letter != null) ...[
            Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [color.withOpacity(0.2), color.withOpacity(0.1)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(32),
              ),
              child: Center(
                child: Text(
                  step.letter!.letter,
                  style: GoogleFonts.baloo2(
                    fontSize: 120,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 32),
          ],
          
          if (step.title != null) ...[
            Text(
              step.title!,
              style: GoogleFonts.baloo2(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
          ],
          
          if (step.content != null) ...[
            Text(
              step.content!,
              style: GoogleFonts.inter(
                fontSize: 20,
                color: AppTheme.textColor.withOpacity(0.7),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
          ],
          
          if (step.audioAsset != null)
            _buildPlayButton(step.audioAsset!, color, 'Listen'),
          
          if (step.letter != null) ...[
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: AppTheme.cardShadow,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.volume_up, color: color, size: 28),
                  const SizedBox(width: 12),
                  Text(
                    step.letter!.sound,
                    style: GoogleFonts.baloo2(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
  
  Widget _buildListenStep(LessonStep step, Color color) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (step.title != null)
            Text(
              step.title!,
              style: GoogleFonts.baloo2(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
          const SizedBox(height: 32),
          
          Container(
            width: 280,
            height: 280,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(32),
              boxShadow: AppTheme.cardShadow,
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(32),
              child: step.imageAsset != null
                  ? Container(
                      color: Colors.grey[100],
                      child: Center(
                        child: Icon(
                          Icons.image,
                          size: 100,
                          color: Colors.grey[400],
                        ),
                      ),
                    )
                  : Container(
                      color: color.withOpacity(0.1),
                      child: Center(
                        child: Icon(
                          Icons.hearing,
                          size: 100,
                          color: color,
                        ),
                      ),
                    ),
            ),
          ),
          const SizedBox(height: 40),
          _buildPlayButton(step.audioAsset!, color, 'Tap to Listen'),
        ],
      ),
    );
  }
  
  Widget _buildTraceStep(LessonStep step, Color color) {
    if (step.letter == null) return _buildGenericStep(step, color);
    
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Text(
            'Trace the letter ${step.letter!.letter}',
            style: GoogleFonts.baloo2(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Draw along the dotted lines',
            style: GoogleFonts.inter(
              fontSize: 16,
              color: AppTheme.textColor.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 32),
          
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(32),
                boxShadow: AppTheme.cardShadow,
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(32),
                child: CustomPaint(
                  painter: LetterTracePainter(
                    letter: step.letter!.letter,
                    color: color,
                  ),
                  size: Size.infinite,
                ),
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.refresh),
                label: const Text('Clear'),
              ),
              const SizedBox(width: 16),
              _buildPlayButton('sound_${step.letter!.letter.toLowerCase()}', color, 'Hear Sound'),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildMatchStep(LessonStep step, Color color) {
    if (step.options == null || step.correctAnswer == null) {
      return _buildGenericStep(step, color);
    }
    
    final attempts = _stepAttempts[step.id] ?? 0;
    
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Text(
            step.title ?? 'Match the Sound',
            style: GoogleFonts.baloo2(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 24),
          
          if (step.audioAsset != null)
            _buildPlayButton(step.audioAsset!, color, 'Play Sound'),
          
          const SizedBox(height: 40),
          
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 1.5,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: step.options!.length,
              itemBuilder: (context, index) {
                final option = step.options![index];
                final isCorrect = option == step.correctAnswer;
                
                return GestureDetector(
                  onTap: () => _handleAnswer(step, isCorrect),
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: AppTheme.cardShadow,
                      border: Border.all(
                        color: isCorrect 
                            ? AppTheme.successColor 
                            : Colors.transparent,
                        width: 3,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        option,
                        style: GoogleFonts.baloo2(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textColor,
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          
          if (attempts > 0)
            Text(
              'Attempt ${attempts + 1}',
              style: GoogleFonts.inter(
                fontSize: 14,
                color: AppTheme.textColor.withOpacity(0.5),
              ),
            ),
        ],
      ),
    );
  }
  
  Widget _buildBlendStep(LessonStep step, Color color) {
    if (step.word == null) return _buildGenericStep(step, color);
    
    final letters = step.word!.split('');
    
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            step.title ?? 'Blend the Sounds',
            style: GoogleFonts.baloo2(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            step.content ?? 'Say each sound, then say them fast!',
            style: GoogleFonts.inter(
              fontSize: 16,
              color: AppTheme.textColor.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 40),
          
          // Letter tiles
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: letters.asMap().entries.map((entry) {
              final isLast = entry.key == letters.length - 1;
              return Row(
                children: [
                  Container(
                    width: 80,
                    height: 100,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [color.withOpacity(0.2), color.withOpacity(0.1)],
                      ),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: color.withOpacity(0.3),
                        width: 3,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        entry.value.toUpperCase(),
                        style: GoogleFonts.baloo2(
                          fontSize: 48,
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                    ),
                  ),
                  if (!isLast) ...[
                    const SizedBox(width: 12),
                    Icon(
                      Icons.add,
                      color: AppTheme.textColor.withOpacity(0.3),
                      size: 32,
                    ),
                    const SizedBox(width: 12),
                  ],
                ],
              );
            }).toList(),
          ),
          
          const SizedBox(height: 40),
          
          // Arrow pointing to result
          Icon(
            Icons.arrow_downward,
            size: 40,
            color: AppTheme.textColor.withOpacity(0.3),
          ),
          
          const SizedBox(height: 40),
          
          // Result
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: AppTheme.cardShadow,
            ),
            child: Text(
              step.word!.toUpperCase(),
              style: GoogleFonts.baloo2(
                fontSize: 48,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
          ),
          
          const SizedBox(height: 40),
          _buildPlayButton(step.audioAsset!, color, 'Listen'),
        ],
      ),
    );
  }
  
  Widget _buildReadStep(LessonStep step, Color color) {
    if (step.word == null) return _buildGenericStep(step, color);
    
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            step.title ?? 'Read the Word',
            style: GoogleFonts.baloo2(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 40),
          
          Container(
            width: 300,
            height: 300,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(32),
              boxShadow: AppTheme.cardShadow,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: step.imageAsset != null
                      ? Container(
                          width: 180,
                          height: 180,
                          color: Colors.grey[100],
                          child: Icon(
                            Icons.image,
                            size: 60,
                            color: Colors.grey[400],
                          ),
                        )
                      : Container(
                          width: 180,
                          height: 180,
                          color: color.withOpacity(0.1),
                          child: Center(
                            child: Text(
                              step.word![0].toUpperCase(),
                              style: GoogleFonts.baloo2(
                                fontSize: 100,
                                color: color,
                              ),
                            ),
                          ),
                        ),
                ),
                const SizedBox(height: 20),
                Text(
                  step.word!.toUpperCase(),
                  style: GoogleFonts.baloo2(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textColor,
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 40),
          _buildPlayButton(step.audioAsset!, color, 'Tap to Hear'),
        ],
      ),
    );
  }
  
  Widget _buildSpellStep(LessonStep step, Color color) {
    if (step.word == null || step.options == null) {
      return _buildGenericStep(step, color);
    }
    
    final word = step.word!;
    final letters = word.split('');
    
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Text(
            step.title ?? 'Spell the Word',
            style: GoogleFonts.baloo2(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 24),
          
          // Word blanks
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(word.length, (index) {
              return Container(
                width: 50,
                height: 60,
                margin: const EdgeInsets.symmetric(horizontal: 4),
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: color.withOpacity(0.3),
                    width: 2,
                  ),
                ),
                child: const Center(
                  child: Text('?'),
                ),
              );
            }),
          ),
          
          const SizedBox(height: 40),
          
          // Letter options
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: step.options!.map((letter) {
              return GestureDetector(
                onTap: () {},
                child: Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: color, width: 2),
                  ),
                  child: Center(
                    child: Text(
                      letter.toUpperCase(),
                      style: GoogleFonts.baloo2(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
  
  Widget _buildGenericStep(LessonStep step, Color color) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (step.title != null)
              Text(
                step.title!,
                style: GoogleFonts.baloo2(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColor,
                ),
                textAlign: TextAlign.center,
              ),
            const SizedBox(height: 16),
            if (step.content != null)
              Text(
                step.content!,
                style: GoogleFonts.inter(
                  fontSize: 18,
                  color: AppTheme.textColor.withOpacity(0.7),
                ),
                textAlign: TextAlign.center,
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildNavigationButtons(Lesson lesson, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            if (_currentStep > 0)
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _previousStep,
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Back'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppTheme.textColor,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              )
            else
              const Expanded(child: SizedBox()),
              
            const SizedBox(width: 16),
            
            if (_currentStep < lesson.steps.length - 1)
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _nextStep,
                  icon: const Icon(Icons.arrow_forward),
                  label: const Text('Next'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: color,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              )
            else
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _completeLesson(lesson),
                  icon: const Icon(Icons.check),
                  label: const Text('Complete'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.successColor,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildPlayButton(String audioId, Color color, String label) {
    return Consumer(
      builder: (context, ref, child) {
        final isPlaying = ref.watch(
          currentlyPlayingProvider.select((id) => id == audioId)
        );
        
        return ElevatedButton.icon(
          onPressed: () async {
            final notifier = ref.read(audioPlaybackProvider.notifier);
            if (isPlaying) {
              await notifier.pause();
            } else {
              await notifier.playAudio(audioId);
            }
          },
          icon: Icon(isPlaying ? Icons.pause : Icons.volume_up),
          label: Text(label),
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          ),
        );
      },
    );
  }
  
  Widget _buildCompletionOverlay(Lesson lesson) {
    return Container(
      color: Colors.black.withOpacity(0.8),
      child: Center(
        child: Container(
          margin: const EdgeInsets.all(32),
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(32),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Stars
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(3, (index) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    child: Icon(
                      index < _earnedStars ? Icons.star : Icons.star_border,
                      size: 60,
                      color: const Color(0xFFFFE66D),
                    ),
                  );
                }),
              ),
              const SizedBox(height: 24),
              
              Text(
                'Lesson Complete!',
                style: GoogleFonts.baloo2(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColor,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'You earned ${_earnedStars} stars!',
                style: GoogleFonts.inter(
                  fontSize: 18,
                  color: AppTheme.textColor.withOpacity(0.7),
                ),
              ),
              const SizedBox(height: 32),
              
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).pop();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.successColor,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text('Continue'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildLoading() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }
  
  Widget _buildError(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: AppTheme.errorColor),
          const SizedBox(height: 16),
          Text(
            message,
            style: GoogleFonts.inter(
              fontSize: 18,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Go Back'),
          ),
        ],
      ),
    );
  }
  
  void _nextStep() {
    HapticFeedback.mediumImpact();
    if (_currentStep < (_pageController.hasClients ? _pageController.positions.length : 0)) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }
  
  void _previousStep() {
    HapticFeedback.mediumImpact();
    if (_currentStep > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }
  
  void _handleAnswer(LessonStep step, bool isCorrect) async {
    HapticFeedback.mediumImpact();
    
    _stepAttempts[step.id] = (_stepAttempts[step.id] ?? 0) + 1;
    
    final soundEffects = ref.read(soundEffectsProvider);
    
    if (isCorrect) {
      await soundEffects.playCorrect();
      
      // Mark step as complete
      await ref.read(lessonProgressProvider.notifier).completeCurrentStep(
        step.id,
        progress: (_currentStep + 1) / ref.read(lessonProvider(widget.lessonId)).value!.steps.length,
      );
      
      // Small delay then next
      await Future.delayed(const Duration(milliseconds: 500));
      _nextStep();
    } else {
      await soundEffects.playIncorrect();
      // Shake animation or feedback
    }
  }
  
  Future<void> _completeLesson(Lesson lesson) async {
    HapticFeedback.heavyImpact();
    
    // Calculate stars based on attempts and accuracy
    final totalAttempts = _stepAttempts.values.fold(0, (a, b) => a + b);
    final perfectAttempts = totalAttempts == lesson.steps.length;
    
    _earnedStars = perfectAttempts ? 3 : (totalAttempts <= lesson.steps.length * 2) ? 2 : 1;
    
    // Play completion sound
    await ref.read(soundEffectsProvider).playComplete();
    
    // Save progress
    await ref.read(lessonProgressProvider.notifier).completeLesson(_earnedStars);
    
    setState(() {
      _showingCompletion = true;
    });
    
    _confettiController.play();
  }
  
  void _showExitDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Leave Lesson?'),
        content: const Text(
          'Your progress will be saved. You can resume this lesson later.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Stay'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('Leave'),
          ),
        ],
      ),
    );
  }
}

// Trace painter for letter tracing step
class LetterTracePainter extends CustomPainter {
  final String letter;
  final Color color;
  
  LetterTracePainter({
    required this.letter,
    required this.color,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    // This is a simplified implementation
    // In a real app, use proper font metrics or SVG paths
    
    final paint = Paint()
      ..color = color.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;
    
    // Draw guide dots or lines
    final center = Offset(size.width / 2, size.height / 2);
    
    // Draw crosshair guides
    canvas.drawLine(
      Offset(0, size.height / 2),
      Offset(size.width, size.height / 2),
      paint,
    );
    canvas.drawLine(
      Offset(size.width / 2, 0),
      Offset(size.width / 2, size.height),
      paint,
    );
  }
  
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}