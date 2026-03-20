import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/data/models/lesson.dart';
import 'package:phonics_master_pro/presentation/providers/lesson_provider.dart';
import 'package:phonics_master_pro/presentation/screens/lesson_screen.dart';

/// Library Screen - Browse all available phonics lessons
/// 
/// Features:
/// - Grid/list view of all lessons
/// - Filter by difficulty level (1-4)
/// - Search functionality
/// - Completion status indicators with progress badges
/// - Responsive design for tablets and Fold 6
class LibraryScreen extends ConsumerStatefulWidget {
  const LibraryScreen({super.key});

  @override
  ConsumerState<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends ConsumerState<LibraryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  bool _isSearching = false;
  int _selectedLevel = 0; // 0 = All levels

  // Level colors for visual distinction
  final List<Color> _levelColors = [
    const Color(0xFF27AE60), // Level 1 - Green (Beginner)
    const Color(0xFF3498DB), // Level 2 - Blue (Easy)
    const Color(0xFFF39C12), // Level 3 - Orange (Intermediate)
    const Color(0xFFE74C3C), // Level 4 - Red (Advanced)
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _tabController.addListener(_handleTabChange);
  }

  @override
  void dispose() {
    _tabController.removeListener(_handleTabChange);
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _handleTabChange() {
    if (_tabController.indexIsChanging) {
      setState(() {
        _selectedLevel = _tabController.index;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final allLessonsAsync = ref.watch(allLessonsProvider);
    final searchQuery = ref.watch(lessonSearchQueryProvider);

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            // Custom header with search
            _buildHeader(),
            
            // Search bar (when active)
            if (_isSearching) _buildSearchBar(),
            
            // Level filter tabs
            _buildLevelTabs(),
            
            // Lesson grid
            Expanded(
              child: allLessonsAsync.when(
                data: (lessons) => _buildLessonsGrid(lessons, searchQuery),
                loading: () => _buildLoadingState(),
                error: (error, _) => _buildErrorState(error),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Builds the screen header with title and search button
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Back button
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back),
            style: IconButton.styleFrom(
              backgroundColor: Colors.grey[100],
            ),
          ),
          const SizedBox(width: 16),
          
          // Title
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Lesson Library',
                  style: GoogleFonts.baloo2(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textColor,
                  ),
                ),
                Text(
                  'Browse all phonics lessons',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: AppTheme.textColor.withOpacity(0.5),
                  ),
                ),
              ],
            ),
          ),
          
          // Search toggle button
          IconButton(
            onPressed: () {
              setState(() {
                _isSearching = !_isSearching;
                if (!_isSearching) {
                  _searchController.clear();
                  ref.read(lessonSearchQueryProvider.notifier).state = '';
                }
              });
              HapticFeedback.lightImpact();
            },
            icon: Icon(
              _isSearching ? Icons.close : Icons.search,
              color: AppTheme.primaryColor,
            ),
            style: IconButton.styleFrom(
              backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
            ),
          ),
        ],
      ),
    );
  }

  /// Builds the search input field
  Widget _buildSearchBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      color: Colors.white,
      child: TextField(
        controller: _searchController,
        onChanged: (value) {
          ref.read(lessonSearchQueryProvider.notifier).state = value;
        },
        decoration: InputDecoration(
          hintText: 'Search lessons...',
          hintStyle: GoogleFonts.inter(
            color: AppTheme.textColor.withOpacity(0.4),
          ),
          prefixIcon: const Icon(Icons.search, color: AppTheme.primaryColor),
          filled: true,
          fillColor: Colors.grey[100],
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        ),
        style: GoogleFonts.inter(
          fontSize: 16,
          color: AppTheme.textColor,
        ),
      ),
    );
  }

  /// Builds the level filter tabs
  Widget _buildLevelTabs() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.only(bottom: 16),
      child: TabBar(
        controller: _tabController,
        isScrollable: true,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        indicator: BoxDecoration(
          color: AppTheme.primaryColor,
          borderRadius: BorderRadius.circular(12),
        ),
        indicatorSize: TabBarIndicatorSize.tab,
        unselectedLabelColor: AppTheme.textColor.withOpacity(0.6),
        labelColor: Colors.white,
        labelStyle: GoogleFonts.inter(
          fontWeight: FontWeight.w600,
          fontSize: 14,
        ),
        tabs: [
          _buildTab('All', Icons.grid_view),
          _buildTab('Level 1', Icons.looks_one),
          _buildTab('Level 2', Icons.looks_two),
          _buildTab('Level 3', Icons.looks_3),
          _buildTab('Level 4', Icons.looks_4),
        ],
      ),
    );
  }

  /// Builds individual tab with icon
  Widget _buildTab(String label, IconData icon) {
    return Tab(
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18),
          const SizedBox(width: 6),
          Text(label),
        ],
      ),
    );
  }

  /// Builds the lessons grid based on selected filter
  Widget _buildLessonsGrid(List<Lesson> lessons, String searchQuery) {
    // Filter lessons by level and search query
    var filteredLessons = lessons;
    
    if (_selectedLevel > 0) {
      filteredLessons = filteredLessons
          .where((l) => l.level == _selectedLevel)
          .toList();
    }
    
    if (searchQuery.isNotEmpty) {
      filteredLessons = filteredLessons
          .where((l) => 
              l.title.toLowerCase().contains(searchQuery.toLowerCase()) ||
              l.description.toLowerCase().contains(searchQuery.toLowerCase()))
          .toList();
    }

    if (filteredLessons.isEmpty) {
      return _buildEmptyState();
    }

    // Determine cross axis count based on screen size
    final screenWidth = MediaQuery.of(context).size.width;
    final crossAxisCount = screenWidth >= 900 ? 3 : screenWidth >= 600 ? 2 : 1;

    return GridView.builder(
      padding: const EdgeInsets.all(20),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio: 1.4,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: filteredLessons.length,
      itemBuilder: (context, index) {
        final lesson = filteredLessons[index];
        return _buildLessonCard(lesson);
      },
    );
  }

  /// Builds individual lesson card
  Widget _buildLessonCard(Lesson lesson) {
    final color = Color(int.parse('0xFF${lesson.colorHex}'));
    final levelColor = _levelColors[(lesson.level - 1).clamp(0, 3)];
    final progress = lesson.progress;
    final isCompleted = lesson.isCompleted;

    return GestureDetector(
      onTap: () {
        HapticFeedback.mediumImpact();
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => LessonScreen(lessonId: lesson.id),
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: AppTheme.cardShadow,
          border: isCompleted
              ? Border.all(color: AppTheme.successColor, width: 2)
              : null,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with lesson icon and level badge
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [color.withOpacity(0.15), color.withOpacity(0.05)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(24),
                ),
              ),
              child: Row(
                children: [
                  // Lesson icon
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: color.withOpacity(0.2),
                          blurRadius: 8,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        lesson.title[0],
                        style: GoogleFonts.baloo2(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  // Lesson info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          lesson.title,
                          style: GoogleFonts.baloo2(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColor,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        // Level badge
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: levelColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: levelColor.withOpacity(0.3),
                            ),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.signal_cellular_alt,
                                size: 12,
                                color: levelColor,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                'Level ${lesson.level}',
                                style: GoogleFonts.inter(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: levelColor,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  // Completion status
                  if (isCompleted)
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.successColor.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.check_circle,
                        color: AppTheme.successColor,
                        size: 24,
                      ),
                    ),
                ],
              ),
            ),
            
            // Description
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                child: Text(
                  lesson.description,
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: AppTheme.textColor.withOpacity(0.6),
                    height: 1.4,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),
            
            // Progress bar and stars
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Row(
                children: [
                  // Progress indicator
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Progress',
                              style: GoogleFonts.inter(
                                fontSize: 11,
                                color: AppTheme.textColor.withOpacity(0.5),
                              ),
                            ),
                            Text(
                              '${(progress * 100).toInt()}%',
                              style: GoogleFonts.inter(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: color,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: progress,
                            backgroundColor: Colors.grey[200],
                            valueColor: AlwaysStoppedAnimation<Color>(color),
                            minHeight: 6,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  // Stars earned
                  Row(
                    children: List.generate(3, (index) {
                      return Icon(
                        index < lesson.stars ? Icons.star : Icons.star_border,
                        size: 18,
                        color: const Color(0xFFFFE66D),
                      );
                    }),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Builds loading state
  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(
            'Loading lessons...',
            style: GoogleFonts.inter(
              fontSize: 16,
              color: AppTheme.textColor.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }

  /// Builds error state
  Widget _buildErrorState(Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: AppTheme.errorColor.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'Failed to load lessons',
              style: GoogleFonts.baloo2(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Please try again later',
              style: GoogleFonts.inter(
                fontSize: 16,
                color: AppTheme.textColor.withOpacity(0.6),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                ref.refresh(allLessonsProvider);
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  /// Builds empty state when no lessons match filters
  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.search_off,
                size: 60,
                color: AppTheme.primaryColor.withOpacity(0.5),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'No lessons found',
              style: GoogleFonts.baloo2(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _isSearching
                  ? 'Try adjusting your search terms'
                  : 'No lessons available for this level yet',
              style: GoogleFonts.inter(
                fontSize: 16,
                color: AppTheme.textColor.withOpacity(0.6),
              ),
              textAlign: TextAlign.center,
            ),
            if (_isSearching) ...[
              const SizedBox(height: 24),
              TextButton(
                onPressed: () {
                  _searchController.clear();
                  ref.read(lessonSearchQueryProvider.notifier).state = '';
                },
                child: const Text('Clear Search'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
