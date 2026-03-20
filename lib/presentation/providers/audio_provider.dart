import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phonics_master_pro/data/repositories/audio_repository.dart';
import 'package:phonics_master_pro/data/services/audio_service.dart';

// Repository provider
final audioRepositoryProvider = Provider<AudioRepository>((ref) {
  return AudioRepository();
});

// Audio service provider
final audioServiceProvider = Provider<AudioService?>((ref) {
  final repository = ref.watch(audioRepositoryProvider);
  final service = ref.watch(audioServiceManagerProvider);
  return service.service;
});

// Audio service manager provider
final audioServiceManagerProvider = Provider<AudioServiceManager>((ref) {
  final repository = ref.read(audioRepositoryProvider);
  final manager = AudioServiceManager();
  
  // Initialize on first use
  Future(() async {
    await repository.init();
    await manager.init(repository);
  });
  
  ref.onDispose(() async {
    await manager.dispose();
  });
  
  return manager;
});

// Audio state provider
final audioStateProvider = StreamProvider<AudioState>((ref) {
  final service = ref.watch(audioServiceProvider);
  if (service == null) return Stream.value(AudioState.idle);
  return service.audioStateStream;
});

// Current playing audio provider
final currentlyPlayingProvider = StateProvider<String?>((ref) => null);

// Volume provider
final volumeProvider = StateNotifierProvider<VolumeNotifier, double>(
  (ref) => VolumeNotifier(1.0),
);

class VolumeNotifier extends StateNotifier<double> {
  VolumeNotifier(super.initialValue);
  
  final _minVolume = 0.0;
  final _maxVolume = 1.0;
  
  void setVolume(double volume) {
    state = volume.clamp(_minVolume, _maxVolume);
  }
  
  void increase() {
    state = (state + 0.1).clamp(_minVolume, _maxVolume);
  }
  
  void decrease() {
    state = (state - 0.1).clamp(_minVolume, _maxVolume);
  }
  
  void mute() => state = 0.0;
  void unmute() => state = 0.5;
}

// Audio playback notifier
class AudioPlaybackNotifier extends StateNotifier<AudioPlaybackState> {
  final ProviderRef _ref;
  StreamSubscription? _stateSubscription;
  
  AudioPlaybackNotifier(this._ref) 
    : super(AudioPlaybackState()) {
    _initListener();
  }
  
  void _initListener() {
    final service = _ref.read(audioServiceProvider);
    _stateSubscription = service?.audioStateStream.listen((audioState) {
      state = state.copyWith(
        playbackState: audioState,
        isPlaying: audioState == AudioState.playing,
        isCompleted: audioState == AudioState.completed,
      );
    });
  }
  
  Future<void> playAudio(String audioId, {bool loop = false}) async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    
    _ref.read(currentlyPlayingProvider.notifier).state = audioId;
    
    try {
      await service.playAudio(audioId, loop: loop);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
  
  Future<void> playLetter(String letter) async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    
    _ref.read(currentlyPlayingProvider.notifier).state = 'sound_$letter';
    
    try {
      await service.playLetterSound(letter);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
  
  Future<void> playWord(String word) async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    
    _ref.read(currentlyPlayingProvider.notifier).state = 'word_$word';
    
    try {
      await service.playWord(word);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
  
  Future<void> playFeedback(String feedbackType) async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    
    try {
      await service.playFeedback(feedbackType);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
  
  Future<void> playBlend(String word) async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    
    try {
      await service.playBlend(word);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
  
  Future<void> pause() async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    await service.pause();
  }
  
  Future<void> resume() async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    await service.play();
  }
  
  Future<void> stop() async {
    final service = _ref.read(audioServiceProvider);
    if (service == null) return;
    _ref.read(currentlyPlayingProvider.notifier).state = null;
    await service.stop();
  }
  
  Future<void> setVolume(double volume) async {
    final service = _ref.read(audioServiceProvider);
    if (service != null) {
      await service.setVolume(volume);
    }
    _ref.read(volumeProvider.notifier).setVolume(volume);
  }
  
  bool isCurrentlyPlaying(String audioId) {
    return _ref.read(currentlyPlayingProvider) == audioId && 
           state.isPlaying;
  }
  
  @override
  void dispose() {
    _stateSubscription?.cancel();
    super.dispose();
  }
}

// Audio playback provider
final audioPlaybackProvider = StateNotifierProvider<AudioPlaybackNotifier, AudioPlaybackState>(
  (ref) => AudioPlaybackNotifier(ref),
);

// Audio playback state
class AudioPlaybackState {
  final AudioState playbackState;
  final bool isPlaying;
  final bool isCompleted;
  final String? error;
  final Duration? position;
  final Duration? duration;
  
  AudioPlaybackState({
    this.playbackState = AudioState.idle,
    this.isPlaying = false,
    this.isCompleted = false,
    this.error,
    this.position,
    this.duration,
  });
  
  AudioPlaybackState copyWith({
    AudioState? playbackState,
    bool? isPlaying,
    bool? isCompleted,
    String? error,
    Duration? position,
    Duration? duration,
  }) {
    return AudioPlaybackState(
      playbackState: playbackState ?? this.playbackState,
      isPlaying: isPlaying ?? this.isPlaying,
      isCompleted: isCompleted ?? this.isCompleted,
      error: error,
      position: position ?? this.position,
      duration: duration ?? this.duration,
    );
  }
}

// Preloaded audio provider for lessons
final preloadedAudioProvider = FutureProvider.family<void, List<String>>((ref, audioIds) async {
  final service = ref.read(audioServiceProvider);
  if (service == null) return;
  await service.preloadAudio(audioIds);
});

// Audio queue for lesson playback
final audioQueueProvider = StateNotifierProvider<AudioQueueNotifier, List<String>>(
  (ref) => AudioQueueNotifier(ref),
);

class AudioQueueNotifier extends StateNotifier<List<String>> {
  final ProviderRef _ref;
  int _currentIndex = 0;
  StreamSubscription? _completionSubscription;
  
  AudioQueueNotifier(this._ref) : super([]) {
    _initCompletionListener();
  }
  
  void _initCompletionListener() {
    final service = _ref.read(audioServiceProvider);
    service?.setOnComplete((audioId) {
      playNext();
    });
  }
  
  void setQueue(List<String> audioIds) {
    state = List.from(audioIds);
    _currentIndex = 0;
  }
  
  Future<void> playQueue() async {
    if (state.isEmpty) return;
    _currentIndex = 0;
    await _playCurrent();
  }
  
  Future<void> playNext() async {
    if (_currentIndex < state.length - 1) {
      _currentIndex++;
      await _playCurrent();
    }
  }
  
  Future<void> playPrevious() async {
    if (_currentIndex > 0) {
      _currentIndex--;
      await _playCurrent();
    }
  }
  
  Future<void> _playCurrent() async {
    if (_currentIndex >= state.length) return;
    
    final audioId = state[_currentIndex];
    final playback = _ref.read(audioPlaybackProvider.notifier);
    await playback.playAudio(audioId);
  }
  
  void clearQueue() {
    state = [];
    _currentIndex = 0;
  }
  
  int get currentIndex => _currentIndex;
  bool get hasNext => _currentIndex < state.length - 1;
  bool get hasPrevious => _currentIndex > 0;
  String? get currentAudio => state.isNotEmpty && _currentIndex < state.length 
      ? state[_currentIndex] 
      : null;
}

// Sound effects helper
class SoundEffects {
  static const String correct = 'correct';
  static const String incorrect = 'incorrect';
  static const String complete = 'complete';
  static const String star = 'star';
  static const String achievement = 'achievement';
  static const String click = 'click';
}

// Convenience provider for sound effects
final soundEffectsProvider = Provider((ref) {
  return SoundEffectsHelper(ref);
});

class SoundEffectsHelper {
  final ProviderRef _ref;
  
  SoundEffectsHelper(this._ref);
  
  Future<void> playCorrect() async {
    await _ref.read(audioPlaybackProvider.notifier).playFeedback(SoundEffects.correct);
  }
  
  Future<void> playIncorrect() async {
    await _ref.read(audioPlaybackProvider.notifier).playFeedback(SoundEffects.incorrect);
  }
  
  Future<void> playComplete() async {
    await _ref.read(audioPlaybackProvider.notifier).playFeedback(SoundEffects.complete);
  }
  
  Future<void> playStar() async {
    await _ref.read(audioPlaybackProvider.notifier).playFeedback(SoundEffects.star);
  }
  
  Future<void> playAchievement() async {
    await _ref.read(audioPlaybackProvider.notifier).playFeedback(SoundEffects.achievement);
  }
  
  Future<void> playClick() async {
    await _ref.read(audioPlaybackProvider.notifier).playFeedback(SoundEffects.click);
  }
}

// Mute provider
final muteProvider = StateNotifierProvider<MuteNotifier, bool>(
  (ref) => MuteNotifier(),
);

class MuteNotifier extends StateNotifier<bool> {
  MuteNotifier() : super(false);
  
  void toggle() {
    state = !state;
  }
  
  void mute() => state = true;
  void unmute() => state = false;
}