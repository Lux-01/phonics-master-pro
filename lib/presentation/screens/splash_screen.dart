import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/presentation/screens/home_screen.dart';
import 'package:rive/rive.dart';
import 'dart:math' as math;

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late AnimationController _mainController;
  late AnimationController _bounceController;
  late AnimationController _rotateController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _bounceAnimation;
  late Animation<double> _rotateAnimation;

  bool _isLoaded = false;
  String _loadingText = 'Loading...';

  @override
  void initState() {
    super.initState();
    
    // Main animation controller
    _mainController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Bounce controller for mascot
    _bounceController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    // Rotate controller for letters
    _rotateController = AnimationController(
      duration: const Duration(milliseconds: 3000),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainController,
        curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainController,
        curve: const Interval(0.0, 0.5, curve: Curves.elasticOut),
      ),
    );

    _bounceAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _bounceController,
        curve: Curves.elasticOut,
      ),
    );

    _rotateAnimation = Tween<double>(begin: 0.0, end: 2 * math.pi).animate(
      CurvedAnimation(
        parent: _rotateController,
        curve: Curves.linear,
      ),
    );

    // Start animations
    _mainController.forward();
    _bounceController.repeat(reverse: true);
    _rotateController.repeat();

    // Simulate loading
    _loadApp();
  }

  Future<void> _loadApp() async {
    await Future.delayed(const Duration(milliseconds: 500));
    setState(() => _loadingText = 'Preparing lessons...');
    
    await Future.delayed(const Duration(milliseconds: 800));
    setState(() => _loadingText = 'Loading sounds...');
    
    await Future.delayed(const Duration(milliseconds: 700));
    setState(() => _loadingText = 'Ready!');
    setState(() => _isLoaded = true);
    
    await Future.delayed(const Duration(milliseconds: 500));
    
    if (mounted) {
      Navigator.of(context).pushReplacement(
        PageRouteBuilder(
          pageBuilder: (context, animation, secondaryAnimation) =>
              const HomeScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: animation,
              child: child,
            );
          },
          transitionDuration: const Duration(milliseconds: 800),
        ),
      );
    }
  }

  @override
  void dispose() {
    _mainController.dispose();
    _bounceController.dispose();
    _rotateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Stack(
            children: [
              // Animated background letters
              ...List.generate(8, (index) {
                return AnimatedBuilder(
                  animation: _rotateController,
                  builder: (context, child) {
                    return Positioned(
                      left: (index * 80) % MediaQuery.of(context).size.width,
                      top: 100 + (index * 60) % 300,
                      child: Transform.rotate(
                        angle: _rotateAnimation.value * 0.3,
                        child: Opacity(
                          opacity: 0.1,
                          child: Text(
                            _getLetter(index),
                            style: GoogleFonts.baloo2(
                              fontSize: 60 + (index * 5),
                              fontWeight: FontWeight.bold,
                              color: AppTheme.primaryColor,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                );
              }),
              
              // Main content
              Center(
                child: AnimatedBuilder(
                  animation: _mainController,
                  builder: (context, child) {
                    return FadeTransition(
                      opacity: _fadeAnimation,
                      child: ScaleTransition(
                        scale: _scaleAnimation,
                        child: child,
                      ),
                    );
                  },
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Mascot container
                      Container(
                        width: 200,
                        height: 200,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(40),
                          boxShadow: AppTheme.cardShadow,
                        ),
                        child: AnimatedBuilder(
                          animation: _bounceAnimation,
                          builder: (context, child) {
                            return Transform.translate(
                              offset: Offset(
                                0,
                                -10 * _bounceAnimation.value,
                              ),
                              child: const Center(
                                child: Text(
                                  '🦊',
                                  style: TextStyle(fontSize: 100),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // App name
                      Text(
                        'PhonicsMaster',
                        style: GoogleFonts.baloo2(
                          fontSize: 48,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textColor,
                          shadows: [
                            Shadow(
                              color: AppTheme.primaryColor.withOpacity(0.2),
                              blurRadius: 8,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 8),
                      
                      // Tagline
                      Text(
                        'Learn to read, one sound at a time',
                        style: GoogleFonts.inter(
                          fontSize: 16,
                          color: AppTheme.textColor.withOpacity(0.6),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      
                      const SizedBox(height: 60),
                      
                      // Loading indicator
                      if (!_isLoaded)
                        Column(
                          children: [
                            SizedBox(
                              width: 200,
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(10),
                                child: LinearProgressIndicator(
                                  backgroundColor: Colors.grey[200],
                                  valueColor: const AlwaysStoppedAnimation<Color>(
                                    AppTheme.primaryColor,
                                  ),
                                  minHeight: 8,
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              _loadingText,
                              style: GoogleFonts.inter(
                                fontSize: 14,
                                color: AppTheme.textColor.withOpacity(0.5),
                              ),
                            ),
                          ],
                        ),
                      
                      if (_isLoaded)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 12,
                          ),
                          decoration: BoxDecoration(
                            color: AppTheme.successColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(30),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.check_circle,
                                color: AppTheme.successColor,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Ready to learn!',
                                style: GoogleFonts.inter(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: AppTheme.successColor,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              
              // Version info
              Positioned(
                bottom: 24,
                left: 0,
                right: 0,
                child: Center(
                  child: Text(
                    'v1.0.0 • Made for Samsung Fold 6',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      color: AppTheme.textColor.withOpacity(0.4),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  String _getLetter(int index) {
    const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    return letters[index % letters.length];
  }
}
