import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;

class AudioRepository {
  static const String _cacheDir = 'audio_cache';
  
  late Directory _cacheDirectory;
  final Map<String, String> _localPathCache = {};
  
  // Audio asset mappings
  static const Map<String, String> _audioAssets = {
    // Letter sounds
    'sound_a': 'assets/audio/sounds/a_sound.mp3',
    'sound_b': 'assets/audio/sounds/b_sound.mp3',
    'sound_c': 'assets/audio/sounds/c_sound.mp3',
    'sound_d': 'assets/audio/sounds/d_sound.mp3',
    'sound_e': 'assets/audio/sounds/e_sound.mp3',
    'sound_f': 'assets/audio/sounds/f_sound.mp3',
    'sound_g': 'assets/audio/sounds/g_sound.mp3',
    'sound_h': 'assets/audio/sounds/h_sound.mp3',
    'sound_i': 'assets/audio/sounds/i_sound.mp3',
    'sound_j': 'assets/audio/sounds/j_sound.mp3',
    'sound_k': 'assets/audio/sounds/k_sound.mp3',
    'sound_l': 'assets/audio/sounds/l_sound.mp3',
    'sound_m': 'assets/audio/sounds/m_sound.mp3',
    'sound_n': 'assets/audio/sounds/n_sound.mp3',
    'sound_o': 'assets/audio/sounds/o_sound.mp3',
    'sound_p': 'assets/audio/sounds/p_sound.mp3',
    'sound_q': 'assets/audio/sounds/q_sound.mp3',
    'sound_r': 'assets/audio/sounds/r_sound.mp3',
    'sound_s': 'assets/audio/sounds/s_sound.mp3',
    'sound_t': 'assets/audio/sounds/t_sound.mp3',
    'sound_u': 'assets/audio/sounds/u_sound.mp3',
    'sound_v': 'assets/audio/sounds/v_sound.mp3',
    'sound_w': 'assets/audio/sounds/w_sound.mp3',
    'sound_x': 'assets/audio/sounds/x_sound.mp3',
    'sound_y': 'assets/audio/sounds/y_sound.mp3',
    'sound_z': 'assets/audio/sounds/z_sound.mp3',
    
    // Word sounds
    'word_apple': 'assets/audio/words/apple.mp3',
    'word_ball': 'assets/audio/words/ball.mp3',
    'word_cat': 'assets/audio/words/cat.mp3',
    'word_dog': 'assets/audio/words/dog.mp3',
    'word_elephant': 'assets/audio/words/elephant.mp3',
    'word_fish': 'assets/audio/words/fish.mp3',
    'word_goat': 'assets/audio/words/goat.mp3',
    'word_hat': 'assets/audio/words/hat.mp3',
    'word_igloo': 'assets/audio/words/igloo.mp3',
    'word_jam': 'assets/audio/words/jam.mp3',
    'word_kite': 'assets/audio/words/kite.mp3',
    'word_lion': 'assets/audio/words/lion.mp3',
    'word_moon': 'assets/audio/words/moon.mp3',
    'word_nest': 'assets/audio/words/nest.mp3',
    'word_orange': 'assets/audio/words/orange.mp3',
    'word_pig': 'assets/audio/words/pig.mp3',
    'word_queen': 'assets/audio/words/queen.mp3',
    'word_rat': 'assets/audio/words/rat.mp3',
    'word_sun': 'assets/audio/words/sun.mp3',
    'word_tree': 'assets/audio/words/tree.mp3',
    'word_umbrella': 'assets/audio/words/umbrella.mp3',
    'word_violin': 'assets/audio/words/violin.mp3',
    'word_water': 'assets/audio/words/water.mp3',
    'word_box': 'assets/audio/words/box.mp3',
    'word_yellow': 'assets/audio/words/yellow.mp3',
    'word_zebra': 'assets/audio/words/zebra.mp3',
    
    // Blends
    'blend_cat': 'assets/audio/words/cat_blend.mp3',
    'blend_dog': 'assets/audio/words/dog_blend.mp3',
    
    // Feedback sounds
    'feedback_correct': 'assets/audio/feedback/correct.mp3',
    'feedback_incorrect': 'assets/audio/feedback/incorrect.mp3',
    'feedback_complete': 'assets/audio/feedback/complete.mp3',
    'feedback_star': 'assets/audio/feedback/star.mp3',
    'feedback_achievement': 'assets/audio/feedback/achievement.mp3',
    'feedback_click': 'assets/audio/feedback/click.mp3',
    
    // UI sounds
    'ui_start': 'assets/audio/ui/start.mp3',
    'ui_success': 'assets/audio/ui/success.mp3',
    'ui_complete': 'assets/audio/ui/lesson_complete.mp3',
  };
  
  // Remote audio URLs (for fallback or additional content)
  static const Map<String, String> _remoteUrls = {};
  
  Future<void> init() async {
    final appDir = await getApplicationDocumentsDirectory();
    _cacheDirectory = Directory('${appDir.path}/$_cacheDir');
    
    if (!await _cacheDirectory.exists()) {
      await _cacheDirectory.create(recursive: true);
    }
  }
  
  // Get audio path - returns bundle path or cached path
  Future<String?> getAudioPath(String audioId) async {
    // Check cache first
    if (_localPathCache.containsKey(audioId)) {
      final file = File(_localPathCache[audioId]!);
      if (await file.exists()) {
        return _localPathCache[audioId];
      }
    }
    
    // Check if it's a bundled asset
    final assetPath = _audioAssets[audioId];
    if (assetPath != null) {
      return assetPath;
    }
    
    // Check if it's a cached file
    final cachedFile = File('${_cacheDirectory.path}/$audioId.mp3');
    if (await cachedFile.exists()) {
      _localPathCache[audioId] = cachedFile.path;
      return cachedFile.path;
    }
    
    // Try to download if remote URL exists
    final remoteUrl = _remoteUrls[audioId];
    if (remoteUrl != null) {
      try {
        final path = await downloadAudio(audioId, remoteUrl);
        return path;
      } catch (e) {
        return null;
      }
    }
    
    return null;
  }
  
  // Check if audio exists locally
  Future<bool> hasAudioLocally(String audioId) async {
    if (_audioAssets.containsKey(audioId)) {
      return true; // Bundle asset
    }
    
    final cachedFile = File('${_cacheDirectory.path}/$audioId.mp3');
    return await cachedFile.exists();
  }
  
  // Download audio from remote
  Future<String> downloadAudio(String audioId, String url) async {
    final file = File('${_cacheDirectory.path}/$audioId.mp3');
    
    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        await file.writeAsBytes(response.bodyBytes);
        _localPathCache[audioId] = file.path;
        return file.path;
      }
      throw Exception('Failed to download: ${response.statusCode}');
    } catch (e) {
      throw Exception('Download failed: $e');
    }
  }
  
  // Preload audio files
  Future<void> preloadAudioFiles(List<String> audioIds) async {
    for (var audioId in audioIds) {
      await getAudioPath(audioId);
    }
  }
  
  // Get audio IDs for a lesson
  List<String> getLessonAudioIds(String lessonId) {
    final ids = <String>[];
    
    // Add relevant sounds based on lesson ID
    if (lessonId == 'lesson_a') {
      ids.addAll(['sound_a', 'word_apple', 'feedback_correct', 'feedback_incorrect']);
    } else if (lessonId == 'lesson_b') {
      ids.addAll(['sound_b', 'word_ball', 'feedback_correct', 'feedback_incorrect']);
    } else if (lessonId == 'lesson_cat') {
      ids.addAll(['sound_c', 'sound_a', 'sound_t', 'word_cat', 'blend_cat', 
                  'feedback_correct', 'feedback_incorrect', 'feedback_complete']);
    }
    
    return ids;
  }
  
  // Cache size management
  Future<int> getCacheSize() async {
    int totalSize = 0;
    
    if (await _cacheDirectory.exists()) {
      await for (final file in _cacheDirectory.list()) {
        if (file is File) {
          totalSize += await file.length();
        }
      }
    }
    
    return totalSize;
  }
  
  Future<void> clearCache() async {
    if (await _cacheDirectory.exists()) {
      await for (final file in _cacheDirectory.list()) {
        if (file is File) {
          await file.delete();
        }
      }
    }
    _localPathCache.clear();
  }
  
  // Batch operations
  Future<Map<String, String?>> getMultipleAudioPaths(List<String> audioIds) async {
    final result = <String, String?>{};
    
    for (var audioId in audioIds) {
      result[audioId] = await getAudioPath(audioId);
    }
    
    return result;
  }
  
  // Get audio metadata
  AudioMetadata? getAudioMetadata(String audioId) {
    final assetPath = _audioAssets[audioId];
    if (assetPath == null) return null;
    
    // Parse metadata from audio ID
    final parts = audioId.split('_');
    
    return AudioMetadata(
      id: audioId,
      type: parts[0],
      content: parts.length > 1 ? parts.sublist(1).join('_') : '',
      assetPath: assetPath,
      isBundled: true,
    );
  }
  
  // Search audio by type
  List<String> getAudioIdsByType(String type) {
    return _audioAssets.keys.where((id) => id.startsWith('${type}_')).toList();
  }
  
  // Get all available audio IDs
  List<String> getAllAudioIds() {
    return _audioAssets.keys.toList();
  }
  
  // Add custom audio (from user recording)
  Future<String> addCustomAudio(String audioId, List<int> bytes) async {
    final file = File('${_cacheDirectory.path}/custom_$audioId.mp3');
    await file.writeAsBytes(bytes);
    _localPathCache[audioId] = file.path;
    return file.path;
  }
  
  // Delete custom audio
  Future<void> deleteCustomAudio(String audioId) async {
    final file = File('${_cacheDirectory.path}/custom_$audioId.mp3');
    if (await file.exists()) {
      await file.delete();
    }
    _localPathCache.remove(audioId);
  }
}

class AudioMetadata {
  final String id;
  final String type;
  final String content;
  final String assetPath;
  final bool isBundled;
  final Duration? duration;
  
  AudioMetadata({
    required this.id,
    required this.type,
    required this.content,
    required this.assetPath,
    required this.isBundled,
    this.duration,
  });
  
  bool get isLetterSound => type == 'sound';
  bool get isWord => type == 'word';
  bool get isFeedback => type == 'feedback';
  bool get isUI => type == 'ui';
  bool get isBlend => type == 'blend';
}