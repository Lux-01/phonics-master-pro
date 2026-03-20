import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phonics_master_pro/data/models/lesson.dart';
import 'package:phonics_master_pro/data/models/word_tile.dart';
import 'package:phonics_master_pro/data/repositories/lesson_repository.dart';

// Repository provider
final lessonRepositoryProvider = Provider<LessonRepository>((ref) {
  return LessonRepository();
});

// All lessons provider
final allLessonsProvider = FutureProvider<List<Lesson>>((ref) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getAllLessons();
});

// Lessons by level provider
final lessonsByLevelProvider = FutureProvider.family<List<Lesson>, int>((ref, level) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getLessonsByLevel(level);
});

// Single lesson provider
final lessonProvider = FutureProvider.family<Lesson?, String>((ref, lessonId) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getLessonById(lessonId);
});

// Next lesson provider
final nextLessonProvider = FutureProvider<Lesson?>((ref) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getNextLesson();
});

// Recommended lessons provider
final recommendedLessonsProvider = FutureProvider<List<Lesson>>((ref) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getRecommendedLessons();
});

// Progress stats provider
final lessonStatsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getLessonStats();
});

// Lesson progress state
class LessonProgressState {
  final String currentLessonId;
  final int currentStepIndex;
  final Map<String, double> lessonProgress;
  final bool isLoading;
  final String? error;
  
  LessonProgressState({
    this.currentLessonId = '',
    this.currentStepIndex = 0,
    this.lessonProgress = const {},
    this.isLoading = false,
    this.error,
  });
  
  LessonProgressState copyWith({
    String? currentLessonId,
    int? currentStepIndex,
    Map<String, double>? lessonProgress,
    bool? isLoading,
    String? error,
  }) {
    return LessonProgressState(
      currentLessonId: currentLessonId ?? this.currentLessonId,
      currentStepIndex: currentStepIndex ?? this.currentStepIndex,
      lessonProgress: lessonProgress ?? this.lessonProgress,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
  
  double getProgress(String lessonId) => lessonProgress[lessonId] ?? 0.0;
  bool canProceed => !isLoading && error == null;
}

// Lesson progress notifier
class LessonProgressNotifier extends StateNotifier<LessonProgressState> {
  final LessonRepository _repository;
  
  LessonProgressNotifier(this._repository) : super(LessonProgressState());
  
  Future<void> startLesson(String lessonId) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      await _repository.init();
      final lesson = await _repository.getLessonById(lessonId);
      
      if (lesson == null) {
        throw Exception('Lesson not found');
      }
      
      state = state.copyWith(
        currentLessonId: lessonId,
        currentStepIndex: 0,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }
  
  void nextStep() {
    state = state.copyWith(currentStepIndex: state.currentStepIndex + 1);
  }
  
  void previousStep() {
    if (state.currentStepIndex > 0) {
      state = state.copyWith(currentStepIndex: state.currentStepIndex - 1);
    }
  }
  
  Future<void> completeCurrentStep(String stepId, {double progress = 1.0}) async {
    await _repository.updateStepProgress(
      state.currentLessonId,
      stepId,
      true,
    );
    
    // Update local progress
    final updatedProgress = Map<String, double>.from(state.lessonProgress);
    updatedProgress[state.currentLessonId] = progress;
    
    state = state.copyWith(lessonProgress: updatedProgress);
  }
  
  Future<void> completeLesson(int stars) async {
    await _repository.completeLesson(state.currentLessonId, stars);
    
    state = state.copyWith(
      currentLessonId: '',
      currentStepIndex: 0,
    );
  }
  
  Future<void> updateProgress(double progress) async {
    await _repository.updateLessonProgress(state.currentLessonId, progress);
    
    final updatedProgress = Map<String, double>.from(state.lessonProgress);
    updatedProgress[state.currentLessonId] = progress;
    
    state = state.copyWith(lessonProgress: updatedProgress);
  }
  
  void clearError() {
    state = state.copyWith(error: null);
  }
}

// Lesson progress provider
final lessonProgressProvider = StateNotifierProvider<LessonProgressNotifier, LessonProgressState>(
  (ref) => LessonProgressNotifier(ref.read(lessonRepositoryProvider)),
);

// Current step provider
final currentStepProvider = Provider.family<LessonStep?, String>((ref, lessonId) {
  final lessonAsync = ref.watch(lessonProvider(lessonId));
  final progressState = ref.watch(lessonProgressProvider);
  
  return lessonAsync.when(
    data: (lesson) {
      if (lesson == null) return null;
      if (progressState.currentStepIndex >= lesson.steps.length) return null;
      return lesson.steps[progressState.currentStepIndex];
    },
    loading: () => null,
    error: (_, __) => null,
  );
});

// Word library provider
final wordLibraryProvider = Provider<List<WordTile>>((ref) {
  return WordLibrary.allWords;
});

// Words by difficulty provider
final wordsByDifficultyProvider = Provider.family<List<WordTile>, int>((ref, difficulty) {
  return WordLibrary.getByDifficulty(difficulty);
});

// Words by category provider
final wordsByCategoryProvider = Provider.family<List<WordTile>, String>((ref, category) {
  return WordLibrary.getByCategory(category);
});

// Word categories provider
final wordCategoriesProvider = Provider<List<String>>((ref) {
  return WordLibrary.categories;
});

// Search lessons provider
final searchLessonsProvider = StateProvider<List<Lesson>>((ref) => []);

// Search function
final lessonSearchProvider = Provider<FutureProvider<List<Lesson>>>((ref) {
  return FutureProvider((ref) async {
    final query = ref.watch(lessonSearchQueryProvider);
    if (query.isEmpty) return [];
    
    final repository = ref.read(lessonRepositoryProvider);
    await repository.init();
    return repository.searchLessons(query);
  });
});

final lessonSearchQueryProvider = StateProvider<String>((ref) => '');

// Overall progress provider
final overallProgressProvider = FutureProvider<double>((ref) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getOverallProgress();
});

// Completed lessons count provider
final completedLessonsCountProvider = FutureProvider<int>((ref) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getCompletedLessonsCount();
});

// Total stars provider
final totalStarsProvider = FutureProvider<int>((ref) async {
  final repository = ref.read(lessonRepositoryProvider);
  await repository.init();
  return repository.getTotalStars();
});

// Utility provider for lesson selection
final lessonSelectionProvider = StateProvider<Set<String>>((ref) => {});

final lessonSelectionNotifierProvider = StateNotifierProvider<LessonSelectionNotifier, Set<String>>(
  (ref) => LessonSelectionNotifier(),
);

class LessonSelectionNotifier extends StateNotifier<Set<String>> {
  LessonSelectionNotifier() : super({});
  
  void toggleSelection(String lessonId) {
    if (state.contains(lessonId)) {
      state = {...state}..remove(lessonId);
    } else {
      state = {...state, lessonId};
    }
  }
  
  void selectAll(List<String> lessonIds) {
    state = {...lessonIds};
  }
  
  void clearSelection() {
    state = {};
  }
  
  bool isSelected(String lessonId) => state.contains(lessonId);
}