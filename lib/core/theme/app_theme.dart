import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Primary Colors
  static const Color primaryColor = Color(0xFFFF6B6B); // Coral Red
  static const Color secondaryColor = Color(0xFF4ECDC4); // Turquoise
  static const Color accentColor = Color(0xFFFFE66D); // Yellow
  static const Color backgroundColor = Color(0xFFFAFAFA); // Off-white
  static const Color cardColor = Colors.white;
  static const Color textColor = Color(0xFF2C3E50); // Dark blue-gray
  static const Color successColor = Color(0xFF27AE60); // Green
  static const Color errorColor = Color(0xFFE74C3C); // Red
  
  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFFFF6B6B), Color(0xFFFF8E8E)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient backgroundGradient = LinearGradient(
    colors: [Color(0xFFFAFAFA), Color(0xFFF5F5F5)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
  
  // Shadows
  static List<BoxShadow> get cardShadow => [
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 12,
      offset: const Offset(0, 4),
    ),
    BoxShadow(
      color: Colors.black.withOpacity(0.02),
      blurRadius: 24,
      offset: const Offset(0, 8),
    ),
  ];
  
  static List<BoxShadow> get buttonShadow => [
    BoxShadow(
      color: primaryColor.withOpacity(0.3),
      blurRadius: 12,
      offset: const Offset(0, 4),
    ),
  ];

  // Typography
  static TextTheme get textTheme => TextTheme(
    displayLarge: GoogleFonts.baloo2(
      fontSize: 48,
      fontWeight: FontWeight.bold,
      color: textColor,
      height: 1.2,
    ),
    displayMedium: GoogleFonts.baloo2(
      fontSize: 36,
      fontWeight: FontWeight.bold,
      color: textColor,
      height: 1.2,
    ),
    displaySmall: GoogleFonts.baloo2(
      fontSize: 28,
      fontWeight: FontWeight.w600,
      color: textColor,
      height: 1.3,
    ),
    headlineLarge: GoogleFonts.inter(
      fontSize: 32,
      fontWeight: FontWeight.bold,
      color: textColor,
      height: 1.3,
    ),
    headlineMedium: GoogleFonts.inter(
      fontSize: 26,
      fontWeight: FontWeight.w600,
      color: textColor,
      height: 1.3,
    ),
    headlineSmall: GoogleFonts.inter(
      fontSize: 20,
      fontWeight: FontWeight.w600,
      color: textColor,
      height: 1.4,
    ),
    titleLarge: GoogleFonts.inter(
      fontSize: 18,
      fontWeight: FontWeight.w600,
      color: textColor,
      height: 1.4,
    ),
    titleMedium: GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: textColor,
      height: 1.4,
    ),
    titleSmall: GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.w600,
      color: textColor,
      height: 1.4,
    ),
    bodyLarge: GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.normal,
      color: textColor,
      height: 1.6,
    ),
    bodyMedium: GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.normal,
      color: textColor,
      height: 1.6,
    ),
    bodySmall: GoogleFonts.inter(
      fontSize: 12,
      fontWeight: FontWeight.normal,
      color: textColor.withOpacity(0.8),
      height: 1.5,
    ),
    labelLarge: GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: textColor,
      letterSpacing: 0.5,
    ),
    labelMedium: GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.w600,
      color: textColor,
      letterSpacing: 0.5,
    ),
  );

  // Light Theme
  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryColor,
      brightness: Brightness.light,
      primary: primaryColor,
      secondary: secondaryColor,
      surface: cardColor,
      background: backgroundColor,
      error: errorColor,
    ),
    scaffoldBackgroundColor: backgroundColor,
    cardTheme: CardTheme(
      color: cardColor,
      elevation: 0,
      shadowColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
    ),
    textTheme: textTheme,
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        elevation: 0,
        textStyle: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: primaryColor,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        side: const BorderSide(color: primaryColor, width: 2),
        textStyle: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: primaryColor,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        textStyle: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.grey[100],
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
    ),
    appBarTheme: AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: backgroundColor,
      foregroundColor: textColor,
      titleTextStyle: GoogleFonts.baloo2(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: textColor,
      ),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Colors.white,
      selectedItemColor: primaryColor,
      unselectedItemColor: Colors.grey,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
    iconTheme: const IconThemeData(
      color: textColor,
      size: 24,
    ),
  );

  // Dark Theme
  static ThemeData get darkTheme => lightTheme.copyWith(
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryColor,
      brightness: Brightness.dark,
      primary: primaryColor,
      secondary: secondaryColor,
      surface: const Color(0xFF1A1A1A),
      background: const Color(0xFF121212),
      error: errorColor,
    ),
    scaffoldBackgroundColor: const Color(0xFF121212),
    cardTheme: CardTheme(
      color: const Color(0xFF1A1A1A),
      elevation: 0,
      shadowColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
    ),
    textTheme: textTheme.copyWith(
      displayLarge: textTheme.displayLarge?.copyWith(color: Colors.white),
      displayMedium: textTheme.displayMedium?.copyWith(color: Colors.white),
      displaySmall: textTheme.displaySmall?.copyWith(color: Colors.white),
      headlineLarge: textTheme.headlineLarge?.copyWith(color: Colors.white),
      headlineMedium: textTheme.headlineMedium?.copyWith(color: Colors.white),
      headlineSmall: textTheme.headlineSmall?.copyWith(color: Colors.white),
      titleLarge: textTheme.titleLarge?.copyWith(color: Colors.white),
      titleMedium: textTheme.titleMedium?.copyWith(color: Colors.white),
      titleSmall: textTheme.titleSmall?.copyWith(color: Colors.white),
      bodyLarge: textTheme.bodyLarge?.copyWith(color: Colors.white70),
      bodyMedium: textTheme.bodyMedium?.copyWith(color: Colors.white70),
      bodySmall: textTheme.bodySmall?.copyWith(color: Colors.white60),
      labelLarge: textTheme.labelLarge?.copyWith(color: Colors.white),
      labelMedium: textTheme.labelMedium?.copyWith(color: Colors.white),
    ),
    appBarTheme: AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: Colors.transparent,
      foregroundColor: Colors.white,
      titleTextStyle: GoogleFonts.baloo2(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF1A1A1A),
      selectedItemColor: primaryColor,
      unselectedItemColor: Colors.grey,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
    iconTheme: const IconThemeData(
      color: Colors.white70,
      size: 24,
    ),
  );
}

// Extension for convenient access
extension ThemeExtension on BuildContext {
  ThemeData get theme => Theme.of(this);
  TextTheme get textTheme => theme.textTheme;
  ColorScheme get colors => theme.colorScheme;
  Size get screenSize => MediaQuery.of(this).size;
  bool get isTablet => screenSize.width >= 600;
  bool get isFold => screenSize.width >= 700 && screenSize.height > 800;
}
