import 'package:audioplayers/audioplayers.dart';
import 'dart:io';

class AudioService {
  final AudioPlayer _player = AudioPlayer();
  String _region = 'au'; // Default to Australia

  Future<void> init() async {
    await _player.setPlayerMode(PlayerMode.lowLatency);
  }

  void setRegion(String region) {
    _region = region.toLowerCase();
  }

  String get region => _region;

  Future<void> playLetterSound(String letter) async {
    try {
      final path = 'assets/audio/$_region/letters/${letter.toLowerCase()}.mp3';
      await _player.stop();
      await _player.play(AssetSource(path));
    } catch (e) {
      print('Audio error for letter $letter: $e');
      // Fallback: could use TTS here
    }
  }

  Future<void> playLetterName(String letter) async {
    try {
      final path =
          'assets/audio/$_region/letters/${letter.toLowerCase()}_name.mp3';
      await _player.stop();
      await _player.play(AssetSource(path));
    } catch (e) {
      print('Audio error for letter name $letter: $e');
    }
  }

  Future<void> playWord(String word) async {
    try {
      final path = 'assets/audio/$_region/words/${word.toLowerCase()}.mp3';
      await _player.stop();
      await _player.play(AssetSource(path));
    } catch (e) {
      print('Audio error for word $word: $e');
    }
  }

  Future<void> playPhonemes(String word) async {
    // Play each letter sound individually then blend
    final letters = word.split('');
    for (final letter in letters) {
      await playLetterSound(letter);
      await Future.delayed(const Duration(milliseconds: 500));
    }
    // Then play the blended word
    await Future.delayed(const Duration(milliseconds: 300));
    await playWord(word);
  }

  Future<void> playSuccess() async {
    try {
      await _player.play(AssetSource('assets/audio/ui/success.mp3'));
    } catch (e) {
      // Ignore if not found
    }
  }

  Future<void> playStar() async {
    try {
      await _player.play(AssetSource('assets/audio/ui/star.mp3'));
    } catch (e) {
      // Ignore if not found
    }
  }

  Future<void> playMascotSound() async {
    try {
      await _player.play(AssetSource('assets/audio/ui/mascot.mp3'));
    } catch (e) {
      // Ignore if not found
    }
  }

  Future<void> stop() async {
    await _player.stop();
  }

  void dispose() {
    _player.dispose();
  }
}
