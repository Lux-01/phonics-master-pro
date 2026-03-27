import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/audio_service.dart';
import 'services/progress_service.dart';
import 'services/storage_service.dart';
import 'screens/splash_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  final storageService = StorageService();
  await storageService.init();
  
  final audioService = AudioService();
  await audioService.init();
  
  final progressService = ProgressService(storageService);
  await progressService.loadProgress();
  
  runApp(
    MultiProvider(
      providers: [
        Provider.value(value: storageService),
        Provider.value(value: audioService),
        ChangeNotifierProvider.value(value: progressService),
      ],
      child: const PhonicsMasterApp(),
    ),
  );
}

class PhonicsMasterApp extends StatelessWidget {
  const PhonicsMasterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PhonicsMaster Pro',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        fontFamily: 'Nunito',
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6C63FF),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF8F9FD),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Color(0xFF2D2D3A),
          ),
        ),
      ),
      home: const SplashScreen(),
    );
  }
}
