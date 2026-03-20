import 'dart:math';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/data/models/phonics_letter.dart';

class LetterTracingScreen extends StatefulWidget {
  final PhonicsLetter letter;

  const LetterTracingScreen({
    super.key,
    required this.letter,
  });

  @override
  State<LetterTracingScreen> createState() => _LetterTracingScreenState();
}

class _LetterTracingScreenState extends State<LetterTracingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _confettiController;
  
  // Tracing data
  final List<List<Offset>> _userStrokes = [];
  List<Offset> _currentStroke = [];
  bool _isTracing = false;
  double _accuracy = 0.0;
  int _currentStrokeIndex = 0;
  bool _isFolded = false; // Would detect from Fold 6 sensors
  
  // Canvas for path comparison
  late TracingCanvasController _tracingController;

  @override
  void initState() {
    super.initState();
    _tracingController = TracingCanvasController(
      referencePath: _generateLetterPath(widget.letter.letter),
    );
    
    // Set landscape for better tracing experience on Fold 6 unfolded
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);
    
    _confettiController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
  }

  @override
  void dispose() {
    // Reset orientation
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
    _confettiController.dispose();
    super.dispose();
  }

  Path _generateLetterPath(String letter) {
    // Simplified path generation - in real app would use proper font paths
    final path = Path();
    
    switch (letter.toUpperCase()) {
      case 'A':
        path.moveTo(100, 300);
        path.lineTo(200, 50);
        path.lineTo(300, 300);
        path.moveTo(150, 175);
        path.lineTo(250, 175);
        break;
      case 'B':
        path.moveTo(100, 50);
        path.lineTo(100, 300);
        path.moveTo(100, 50);
        path.quadraticBezierTo(250, 50, 250, 125);
        path.quadraticBezierTo(250, 200, 100, 175);
        path.moveTo(100, 175);
        path.quadraticBezierTo(250, 175, 250, 240);
        path.quadraticBezierTo(250, 320, 100, 300);
        break;
      case 'C':
        path.moveTo(250, 50);
        path.quadraticBezierTo(100, 50, 100, 175);
        path.quadraticBezierTo(100, 300, 250, 300);
        break;
      default:
        // Generic circle for other letters
        path.addOval(Rect.fromCircle(
          center: const Offset(200, 175),
          radius: 125,
        ));
    }
    
    return path;
  }

  void _onPanStart(DragStartDetails details) {
    setState(() {
      _isTracing = true;
      _currentStroke = [details.localPosition];
    });
  }

  void _onPanUpdate(DragUpdateDetails details) {
    if (_isTracing) {
      setState(() {
        _currentStroke.add(details.localPosition);
        _checkTracingProgress();
      });
    }
  }

  void _onPanEnd(DragEndDetails details) {
    if (_currentStroke.isNotEmpty) {
      setState(() {
        _userStrokes.add(List.from(_currentStroke));
        _isTracing = false;
        _currentStroke = [];
        _currentStrokeIndex++;
        _calculateAccuracy();
      });
      
      // Check if complete
      if (_currentStrokeIndex >= widget.letter.strokeCount) {
        _onTracingComplete();
      }
    }
  }

  void _checkTracingProgress() {
    // Simplified progress check
    // In real app would do path comparison
  }

  void _calculateAccuracy() {
    // Calculate tracing accuracy based on path similarity
    // This is a simplified version
    setState(() {
      _accuracy = min(1.0, _userStrokes.length / widget.letter.strokeCount * 0.8 + 0.2);
    });
  }

  void _onTracingComplete() {
    _confettiController.forward();
    
    HapticFeedback.heavyImpact();
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => _buildCompletionDialog(),
    );
  }

  Widget _buildCompletionDialog() {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        padding: const EdgeInsets.all(32),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(32),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Star animation
            ...List.generate(3, (index) {
              return AnimatedBuilder(
                animation: _confettiController,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _confettiController.value,
                    child: Icon(
                      Icons.star,
                      color: index == 0
                          ? const Color(0xFFFFE66D)
                          : index == 1
                              ? const Color(0xFFFFE66D).withOpacity(0.7)
                              : const Color(0xFFFFE66D).withOpacity(0.4),
                      size: 60.0 - index * 10,
                    ),
                  );
                },
              );
            }),
            const SizedBox(height: 24),
            Text(
              'Great Job!',
              style: GoogleFonts.baloo2(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'You traced "${widget.letter.letter}" with ${(_accuracy * 100).toInt()}% accuracy!',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 16,
                color: AppTheme.textColor.withOpacity(0.7),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      Navigator.pop(context);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: Text(
                      'Continue',
                      style: GoogleFonts.inter(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _clearCanvas() {
    setState(() {
      _userStrokes.clear();
      _currentStroke.clear();
      _currentStrokeIndex = 0;
      _accuracy = 0.0;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Detect if Fold 6 is unfolded (wide screen)
    final screenSize = MediaQuery.of(context).size;
    final isUnfolded = screenSize.width > 700;
    
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: Row(
          children: [
            // Sidebar with controls
            Container(
              width: 80,
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Back button
                  IconButton(
                    icon: const Icon(Icons.arrow_back),
                    onPressed: () => Navigator.pop(context),
                  ),
                  
                  // Clear button
                  IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: _clearCanvas,
                    tooltip: 'Clear',
                  ),
                  
                  // Instructions
                  RotatedBox(
                    quarterTurns: -1,
                    child: Text(
                      'Trace the letter',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: AppTheme.textColor.withOpacity(0.5),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 20),
                ],
              ),
            ),
            
            // Main content area
            Expanded(
              child: Column(
                children: [
                  // Header
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      boxShadow: AppTheme.cardShadow,
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 10,
                          ),
                          decoration: BoxDecoration(
                            color: widget.letter.color.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Text(
                            widget.letter.letter,
                            style: GoogleFonts.baloo2(
                              fontSize: 48,
                              fontWeight: FontWeight.bold,
                              color: widget.letter.color,
                            ),
                          ),
                        ),
                        const SizedBox(width: 20),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Trace Letter ${widget.letter.letter}',
                                style: GoogleFonts.baloo2(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: AppTheme.textColor,
                                ),
                              ),
                              Text(
                                'Sound: ${widget.letter.sound}',
                                style: GoogleFonts.inter(
                                  fontSize: 16,
                                  color: AppTheme.textColor.withOpacity(0.6),
                                ),
                              ),
                            ],
                          ),
                        ),
                        
                        // Progress indicator
                        Column(
                          children: [
                            CircularProgressIndicator(
                              value: _accuracy,
                              backgroundColor: Colors.grey[200],
                              valueColor: AlwaysStoppedAnimation<Color>(
                                _accuracy > 0.8
                                    ? AppTheme.successColor
                                    : AppTheme.primaryColor,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '${(_accuracy * 100).toInt()}%',
                              style: GoogleFonts.inter(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  
                  // Canvas area
                  Expanded(
                    child: Container(
                      margin: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: AppTheme.cardShadow,
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(24),
                        child: GestureDetector(
                          onPanStart: _onPanStart,
                          onPanUpdate: _onPanUpdate,
                          onPanEnd: _onPanEnd,
                          child: CustomPaint(
                            painter: TracingPainter(
                              referencePath: _tracingController.referencePath,
                              userStrokes: _userStrokes,
                              currentStroke: _currentStroke,
                              isDarkBackground: false,
                            ),
                            size: Size.infinite,
                          ),
                        ),
                      ),
                    ),
                  ),
                  
                  // Bottom controls
                  Container(
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
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildControlButton(
                          icon: Icons.undo,
                          label: 'Undo',
                          onTap: () {
                            if (_userStrokes.isNotEmpty) {
                              setState(() {
                                _userStrokes.removeLast();
                                _currentStrokeIndex--;
                                _calculateAccuracy();
                              });
                            }
                          },
                        ),
                        _buildControlButton(
                          icon: Icons.replay,
                          label: 'Replay',
                          color: AppTheme.secondaryColor,
                          onTap: () {
                            // Replay animation
                          },
                        ),
                        _buildControlButton(
                          icon: Icons.lightbulb,
                          label: 'Hint',
                          color: const Color(0xFFFFE66D),
                          onTap: () {
                            // Show hint
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    Color color = AppTheme.textColor,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class TracingCanvasController {
  final Path referencePath;
  final List<Path> userPaths = [];
  
  TracingCanvasController({
    required this.referencePath,
  });
  
  double calculateAccuracy(Path userPath) {
    // Simplified accuracy calculation
    // In real app: path comparison using Frechet distance or similar
    return 1.0;
  }
}

class TracingPainter extends CustomPainter {
  final Path referencePath;
  final List<List<Offset>> userStrokes;
  final List<Offset> currentStroke;
  final bool isDarkBackground;

  TracingPainter({
    required this.referencePath,
    required this.userStrokes,
    required this.currentStroke,
    this.isDarkBackground = false,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Draw reference path (dotted line)
    final referencePaint = Paint()
      ..color = (isDarkBackground ? Colors.white : Colors.grey).withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round;
    
    // Draw dotted effect
    const dashWidth = 10.0;
    const dashSpace = 10.0;
    final pathMetrics = referencePath.computeMetrics();
    
    for (final metric in pathMetrics) {
      var distance = 0.0;
      while (distance < metric.length) {
        final start = metric.getTangentForOffset(distance)?.position;
        final end = metric.getTangentForOffset(min(distance + dashWidth, metric.length))?.position;
        if (start != null && end != null) {
          canvas.drawLine(start, end, referencePaint);
        }
        distance += dashWidth + dashSpace;
      }
    }
    
    // Draw user strokes
    final userPaint = Paint()
      ..color = AppTheme.primaryColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 2);
    
    for (final stroke in userStrokes) {
      if (stroke.length > 1) {
        final path = Path();
        path.moveTo(stroke[0].dx, stroke[0].dy);
        for (int i = 1; i < stroke.length; i++) {
          path.lineTo(stroke[i].dx, stroke[i].dy);
        }
        canvas.drawPath(path, userPaint);
      }
    }
    
    // Draw current stroke
    if (currentStroke.length > 1) {
      final activePaint = Paint()
        ..color = AppTheme.primaryColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 12
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round;
      
      final path = Path();
      path.moveTo(currentStroke[0].dx, currentStroke[0].dy);
      for (int i = 1; i < currentStroke.length; i++) {
        path.lineTo(currentStroke[i].dx, currentStroke[i].dy);
      }
      canvas.drawPath(path, activePaint);
    }
    
    // Draw start point indicator
    final startPoint = referencePath.getBounds().center;
    canvas.drawCircle(
      startPoint,
      8,
      Paint()..color = AppTheme.successColor,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
