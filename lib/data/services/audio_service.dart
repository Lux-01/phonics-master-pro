import 'dart:async';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:audio_service/audio_service.dart';
import 'package:phonics_master_pro/data/repositories/audio_repository.dart';

class AudioService extends BaseAudioHandler with SeekHandler {
  final AudioPlayer _player = AudioPlayer();
  final AudioRepository _audioRepository;
  
  // State management
  final _playbackStateController = StreamController<AudioState>.broadcast();
  Stream<AudioState> get audioStateStream => _playbackStateController.stream;
  
  AudioState _currentState = AudioState.idle;
  String? _currentAudioId;
  
  AudioService(this._audioRepository) {
    _init();
  }
  
  void _init() {
    // Listen to player state changes
    _player.playerStateStream.listen((state) {
      _updatePlaybackState();
      
      if (state.processingState == ProcessingState.completed) {
        _currentState = AudioState.completed;
        _playbackStateController.add(_currentState);
      }
    });
    
    // Listen to position changes
    _player.positionStream.listen((position) {
      // Update position for UI
    });
  }
  
  void _updatePlaybackState() {
    final isPlaying = _player.playing;
    final processingState = _player.processingState;
    
    playbackState.add(PlaybackState(
      controls: [
        MediaControl.rewind,
        if (isPlaying) MediaControl.pause else MediaControl.play,
        MediaControl.stop,
        MediaControl.fastForward,
      ],
      systemActions: const {
        MediaAction.seek,
        MediaAction.seekForward,
        MediaAction.seekBackward,
      },
      androidCompactActionIndices: const [0, 1, 3],
      processingState: _mapProcessingState(processingState),
      playing: isPlaying,
      updatePosition: _player.position,
      bufferedPosition: _player.bufferedPosition,
      speed: _player.speed,
      queueIndex: 0,
    ));
  }
  
  AudioProcessingState _mapProcessingState(ProcessingState state) {
    switch (state) {
      case ProcessingState.idle:
        return AudioProcessingState.idle;
      case ProcessingState.loading:
        return AudioProcessingState.loading;
      case ProcessingState.buffering:
        return AudioProcessingState.buffering;
      case ProcessingState.ready:
        return AudioProcessingState.ready;
      case ProcessingState.completed:
        return AudioProcessingState.completed;
    }
  }
  
  // Play audio by ID
  Future<void> playAudio(String audioId, {bool loop = false}) async {
    try {
      _currentState = AudioState.loading;
      _playbackStateController.add(_currentState);
      
      final path = await _audioRepository.getAudioPath(audioId);
      if (path == null) {
        throw Exception('Audio not found: $audioId');
      }
      
      _currentAudioId = audioId;
      
      // Set audio source
      if (path.startsWith('assets/')) {
        await _player.setAsset(path);
      } else {
        await _player.setFilePath(path);
      }
      
      if (loop) {
        await _player.setLoopMode(LoopMode.one);
      } else {
        await _player.setLoopMode(LoopMode.off);
      }
      
      // Update media item
      mediaItem.add(MediaItem(
        id: audioId,
        title: _getDisplayTitle(audioId),
        artUri: null,
        duration: _player.duration,
      ));
      
      await _player.play();
      _currentState = AudioState.playing;
      _playbackStateController.add(_currentState);
      
    } catch (e) {
      _currentState = AudioState.error;
      _playbackStateController.add(_currentState);
      debugPrint('Error playing audio: $e');
    }
  }
  
  // Play letter sound
  Future<void> playLetterSound(String letter) async {
    final audioId = 'sound_${letter.toLowerCase()}';
    await playAudio(audioId);
  }
  
  // Play word
  Future<void> playWord(String word) async {
    final audioId = 'word_$word';
    await playAudio(audioId);
  }
  
  // Play feedback sound
  Future<void> playFeedback(String feedbackType) async {
    final audioId = 'feedback_$feedbackType';
    await playAudio(audioId);
  }
  
  // Play UI sound
  Future<void> playUISound(String uiSound) async {
    final audioId = 'ui_$uiSound';
    await playAudio(audioId);
  }
  
  // Play blend (for word building)
  Future<void> playBlend(String word) async {
    final audioId = 'blend_$word';
    await playAudio(audioId);
  }
  
  // Text to speech fallback
  Future<void> speak(String text) async {
    // In a real implementation, integrate with TTS
    // For now, play a generic audio
    await playFeedback('click');
  }
  
  @override
  Future<void> play() async {
    await _player.play();
    _currentState = AudioState.playing;
    _playbackStateController.add(_currentState);
  }
  
  @override
  Future<void> pause() async {
    await _player.pause();
    _currentState = AudioState.paused;
    _playbackStateController.add(_currentState);
  }
  
  @override
  Future<void> stop() async {
    await _player.stop();
    _currentState = AudioState.stopped;
    _currentAudioId = null;
    _playbackStateController.add(_currentState);
  }
  
  @override
  Future<void> seek(Duration position) async {
    await _player.seek(position);
  }
  
  Future<void> seekForward() async {
    final newPosition = _player.position + const Duration(seconds: 5);
    await _player.seek(newPosition);
  }
  
  Future<void> seekBackward() async {
    final newPosition = _player.position - const Duration(seconds: 5);
    if (newPosition > Duration.zero) {
      await _player.seek(newPosition);
    } else {
      await _player.seek(Duration.zero);
    }
  }
  
  // Set volume
  Future<void> setVolume(double volume) async {
    await _player.setVolume(volume.clamp(0.0, 1.0));
  }
  
  // Set speed
  Future<void> setSpeed(double speed) async {
    await _player.setSpeed(speed.clamp(0.5, 2.0));
  }
  
  // Get current position
  Duration get currentPosition => _player.position;
  
  // Get duration
  Duration? get duration => _player.duration;
  
  // Get current audio ID
  String? get currentAudioId => _currentAudioId;
  
  // Check if currently playing
  bool get isPlaying => _player.playing;
  
  // Check if currently playing specific audio
  bool isPlayingAudio(String audioId) => 
      _player.playing && _currentAudioId == audioId;
  
  // Preload audio (for better performance)
  Future<void> preloadAudio(List<String> audioIds) async {
    await _audioRepository.preloadAudioFiles(audioIds);
  }
  
  String _getDisplayTitle(String audioId) {
    final parts = audioId.split('_');
    if (parts.length > 1) {
      return parts.sublist(1).join(' ').toUpperCase();
    }
    return audioId;
  }
  
  Future<void> dispose() async {
    await _player.dispose();
    await _playbackStateController.close();
  }
}

// Audio state enum
enum AudioState {
  idle,
  loading,
  playing,
  paused,
  stopped,
  completed,
  error,
}

// Extension for easy access
extension AudioStateExtension on AudioState {
  bool get isPlaying => this == AudioState.playing;
  bool get isLoading => this == AudioState.loading;
  bool get isCompleted => this == AudioState.completed;
  bool get hasError => this == AudioState.error;
}

// Audio completion callback
typedef AudioCompletionCallback = void Function(String audioId);

// Audio service wrapper for Riverpod
class AudioServiceManager {
  AudioService? _service;
  AudioCompletionCallback? _onComplete;
  StreamSubscription? _stateSubscription;
  
  AudioService? get service => _service;
  bool get isInitialized => _service != null;
  
  Future<void> init(AudioRepository repository) async {
    _service = AudioService(repository);
    
    // Listen for completions
    _stateSubscription = _service!.audioStateStream.listen((state) {
      if (state == AudioState.completed) {
        _onComplete?.call(_service!.currentAudioId ?? '');
      }
    });
  }
  
  void setOnComplete(AudioCompletionCallback callback) {
    _onComplete = callback;
  }
  
  Future<void> dispose() async {
    await _stateSubscription?.cancel();
    await _service?.dispose();
    _service = null;
  }
}