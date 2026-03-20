import 'dart:math';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/data/models/phonics_letter.dart';
import 'package:vibration/vibration.dart';

import 'letter_tracing_screen.dart';

class LetterCard extends StatelessWidget {
  final PhonicsLetter letter;
  final VoidCallback? onTap;
  final bool isCompact;
  final bool showExample;

  const LetterCard({
    super.key,
    required this.letter,
    this.onTap,
    this.isCompact = false,
    this.showExample = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Vibration.hasVibrator().then((hasVibrator) {
          if (hasVibrator == true) {
            Vibration.vibrate(duration: 50);
          }
        });
        
        if (onTap != null) {
          onTap!();
        } else {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => LetterTracingScreen(letter: letter),
            ),
          );
        }
      },
      child: Container(
        decoration: BoxDecoration(
          gradient: letter.gradient,
          borderRadius: BorderRadius.circular(isCompact ? 16 : 24),
          boxShadow: [
            BoxShadow(
              color: letter.color.withOpacity(0.3),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(isCompact ? 16 : 24),
          child: Stack(
            children: [
              // Background pattern
              Positioned(
                right: -20,
                bottom: -20,
                child: Opacity(
                  opacity: 0.1,
                  child: Text(
                    letter.letter,
                    style: GoogleFonts.baloo2(
                      fontSize: isCompact ? 100 : 150,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
              
              // Main content
              Padding(
                padding: EdgeInsets.all(isCompact ? 12 : 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Letter display
                    Container(
                      padding: EdgeInsets.symmetric(
                        horizontal: isCompact ? 12 : 20,
                        vertical: isCompact ? 8 : 12,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        letter.letter,
                        style: GoogleFonts.baloo2(
                          fontSize: isCompact ? 36 : 48,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 4,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                      ),
                    ),
                    
                    const Spacer(),
                    
                    // Sound and example
                    if (!isCompact) ...[
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          letter.sound,
                          style: GoogleFonts.inter(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      if (showExample)
                        Text(
                          'as in "${letter.exampleWord}"',
                          style: GoogleFonts.inter(
                            fontSize: 14,
                            color: Colors.white.withOpacity(0.9),
                          ),
                        ),
                    ],
                    
                    if (isCompact)
                      Text(
                        letter.sound,
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                  ],
                ),
              ),
              
              // Play indicator
              Positioned(
                right: isCompact ? 8 : 12,
                top: isCompact ? 8 : 12,
                child: Container(
                  padding: EdgeInsets.all(isCompact ? 6 : 8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(50),
                  ),
                  child: Icon(
                    Icons.volume_up,
                    color: Colors.white,
                    size: isCompact ? 16 : 20,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Animated letter card for games
class AnimatedLetterCard extends StatefulWidget {
  final PhonicsLetter letter;
  final VoidCallback? onTap;
  final bool isSelected;
  final bool isCorrect;

  const AnimatedLetterCard({
    super.key,
    required this.letter,
    this.onTap,
    this.isSelected = false,
    this.isCorrect = false,
  });

  @override
  State<AnimatedLetterCard> createState() => _AnimatedLetterCardState();
}

class _AnimatedLetterCardState extends State<AnimatedLetterCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    _rotationAnimation = Tween<double>(begin: 0, end: 0.05).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Color cardColor = widget.letter.color;
    
    if (widget.isSelected) {
      cardColor = widget.isCorrect ? AppTheme.successColor : AppTheme.errorColor;
    }

    return GestureDetector(
      onTapDown: (_) {
        _controller.forward();
      },
      onTapUp: (_) {
        _controller.reverse();
        if (widget.onTap != null) {
          widget.onTap!();
        }
      },
      onTapCancel: () => _controller.reverse(),
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Transform.rotate(
              angle: widget.isSelected ? sin(_rotationAnimation.value * 3.14) * 0.05 : 0,
              child: child,
            ),
          );
        },
        child: Container(
          decoration: BoxDecoration(
            color: cardColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: cardColor,
              width: widget.isSelected ? 3 : 2,
            ),
            boxShadow: widget.isSelected
                ? [
                    BoxShadow(
                      color: cardColor.withOpacity(0.4),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : null,
          ),
          child: Center(
            child: Text(
              widget.letter.letter,
              style: GoogleFonts.baloo2(
                fontSize: 48,
                fontWeight: FontWeight.bold,
                color: cardColor,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// Word card for displaying CVC words
class WordCard extends StatelessWidget {
  final String word;
  final String? imageAsset;
  final String? audioAsset;
  final VoidCallback? onTap;
  final bool showBlendAnimation;

  const WordCard({
    super.key,
    required this.word,
    this.imageAsset,
    this.audioAsset,
    this.onTap,
    this.showBlendAnimation = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: AppTheme.cardShadow,
        ),
        child: Column(
          children: [
            // Word with individual letters
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: word.split('').map((letter) {
                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  width: 60,
                  height: 80,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: AppTheme.primaryColor.withOpacity(0.3),
                      width: 2,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      letter.toUpperCase(),
                      style: GoogleFonts.baloo2(
                        fontSize: 36,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            // Full word
            Text(
              word.toUpperCase(),
              style: GoogleFonts.baloo2(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
                letterSpacing: 4,
              ),
            ),
            const SizedBox(height: 8),
            // Play button
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(30),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.volume_up, color: AppTheme.primaryColor),
                  const SizedBox(width: 8),
                  Text(
                    'Listen',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.primaryColor,
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
}
