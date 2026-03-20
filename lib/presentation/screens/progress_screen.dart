import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/data/models/user_progress.dart';
import 'package:phonics_master_pro/data/repositories/progress_repository.dart';
import 'package:phonics_master_pro/presentation/providers/lesson_provider.dart';
import 'package:phonics_master_pro/presentation/providers/settings_provider.dart';

/// Progress Screen - Track learning achievements and statistics
/// 
/// Features:
/// - Overall user stats (lessons completed, streak days, total stars)
/// - Skill breakdown chart (radar chart)
/// - Weekly learning activity (bar chart)
/// - Achievements grid with locked/unlocked states
/// - Time spent learning
/// - Dyslexia-friendly font support
class ProgressScreen extends ConsumerStatefulWidget {
  const ProgressScreen({super.key});

  @override
  ConsumerState<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends ConsumerState<ProgressScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isLoading = true;
  Map<String, dynamic>? _stats;
  List<Achievement>? _achievements;
  UserProgress? _userProgress;

  // Sample user ID - in real app this would come from auth
  static const String _userId = 'user_001';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    try {
      final repository = ProgressRepository();
      await repository.init();

      // Load stats
      final stats = await repository.getProgressStats(_userId);
      final achievements = await repository.getAllAchievements();
      final userProgress = await repository.getOrCreateUserProgress(_userId);

      setState(() {
        _stats = stats;
        _achievements = achievements;
        _userProgress = userProgress;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dyslexiaMode = ref.watch(dyslexiaModeProvider);
    final isFold = context.isFold;

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            _buildHeader(),
            
            // Tab bar
            _buildTabBar(),
            
            // Content
            Expanded(
              child: _isLoading
                  ? _buildLoadingState()
                  : TabBarView(
                      controller: _tabController,
                      children: [
                        _buildOverviewTab(),
                        _buildSkillsTab(),
                        _buildAchievementsTab(),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  /// Builds the screen header
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppTheme.primaryGradient,
        borderRadius: const BorderRadius.vertical(
          bottom: Radius.circular(32),
        ),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: SafeArea(
        child: Column(
          children: [
            Row(
              children: [
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.arrow_back, color: Colors.white),
                  style: IconButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.2),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Your Progress',
                        style: GoogleFonts.baloo2(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        'Keep learning and growing!',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Quick stats row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildQuickStat(
                  icon: Icons.star,
                  value: '${_stats?['totalStarsEarned'] ?? 0}',
                  label: 'Stars',
                  color: const Color(0xFFFFE66D),
                ),
                _buildQuickStat(
                  icon: Icons.local_fire_department,
                  value: '${_stats?['currentStreak'] ?? 0}',
                  label: 'Day Streak',
                  color: Colors.orange,
                ),
                _buildQuickStat(
                  icon: Icons.menu_book,
                  value: '${_stats?['totalLessonsCompleted'] ?? 0}',
                  label: 'Lessons',
                  color: Colors.white,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Builds quick stat item
  Widget _buildQuickStat({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.2),
        ),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 8),
          Text(
            value,
            style: GoogleFonts.baloo2(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 12,
              color: Colors.white.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }

  /// Builds tab bar
  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(16),
      ),
      child: TabBar(
        controller: _tabController,
        indicator: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 4,
            ),
          ],
        ),
        labelColor: AppTheme.primaryColor,
        unselectedLabelColor: Colors.grey,
        labelStyle: GoogleFonts.inter(
          fontWeight: FontWeight.w600,
          fontSize: 14,
        ),
        tabs: const [
          Tab(text: 'Overview'),
          Tab(text: 'Skills'),
          Tab(text: 'Achievements'),
        ],
      ),
    );
  }

  /// Builds overview tab with weekly activity and time stats
  Widget _buildOverviewTab() {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth >= 600;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Weekly activity chart
          _buildSectionTitle('Weekly Activity'),
          const SizedBox(height: 16),
          _buildWeeklyChart(),
          const SizedBox(height: 32),
          
          // Time spent section
          _buildSectionTitle('Learning Time'),
          const SizedBox(height: 16),
          _buildTimeStats(),
          const SizedBox(height: 32),
          
          // Level progress
          _buildSectionTitle('Level Progress'),
          const SizedBox(height: 16),
          _buildLevelProgress(),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  /// Builds skills tab with radar chart
  Widget _buildSkillsTab() {
    final skillLevels = _stats?['skillLevels'] as Map<String, dynamic>? ?? {};

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Skill Breakdown'),
          const SizedBox(height: 8),
          Text(
            'Your strengths across different phonics skills',
            style: GoogleFonts.inter(
              fontSize: 14,
              color: AppTheme.textColor.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 24),
          
          // Radar chart
          AspectRatio(
            aspectRatio: 1.3,
            child: _buildSkillsRadarChart(skillLevels),
          ),
          const SizedBox(height: 32),
          
          // Individual skill bars
          _buildSectionTitle('Skill Levels'),
          const SizedBox(height: 16),
          _buildSkillBars(skillLevels),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  /// Builds achievements tab
  Widget _buildAchievementsTab() {
    if (_achievements == null) {
      return const Center(child: Text('No achievements data'));
    }

    final unlockedCount = _achievements!
        .where((a) => _userProgress?.unlockedAchievements.contains(a.id) ?? false)
        .length;

    return CustomScrollView(
      slivers: [
        // Achievement stats header
        SliverToBoxAdapter(
          child: Container(
            margin: const EdgeInsets.all(20),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  const Color(0xFFFFE66D),
                  const Color(0xFFFFD93D),
                ],
              ),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFFFFE66D).withOpacity(0.4),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.emoji_events,
                    size: 40,
                    color: Color(0xFFF39C12),
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$unlockedCount / ${_achievements!.length}',
                        style: GoogleFonts.baloo2(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textColor,
                        ),
                      ),
                      Text(
                        'Achievements Unlocked',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          color: AppTheme.textColor.withOpacity(0.7),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        
        // Achievement grid
        SliverPadding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          sliver: SliverGrid(
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.85,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final achievement = _achievements![index];
                final isUnlocked = _userProgress?.unlockedAchievements
                        .contains(achievement.id) ??
                    false;
                return _buildAchievementCard(achievement, isUnlocked);
              },
              childCount: _achievements!.length,
            ),
          ),
        ),
        
        const SliverPadding(padding: EdgeInsets.only(bottom: 32)),
      ],
    );
  }

  /// Builds achievement card
  Widget _buildAchievementCard(Achievement achievement, bool isUnlocked) {
    final badgeColor = isUnlocked
        ? Color(int.parse('0xFF${achievement.badgeColor ?? 'FF6B6B'}'))
        : Colors.grey;

    return Container(
      decoration: BoxDecoration(
        color: isUnlocked ? Colors.white : Colors.grey[100],
        borderRadius: BorderRadius.circular(20),
        boxShadow: isUnlocked ? AppTheme.cardShadow : null,
        border: Border.all(
          color: isUnlocked ? badgeColor.withOpacity(0.3) : Colors.grey[300]!,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Achievement badge
          Container(
            width: 70,
            height: 70,
            decoration: BoxDecoration(
              color: isUnlocked ? badgeColor.withOpacity(0.1) : Colors.grey[200],
              shape: BoxShape.circle,
            ),
            child: Icon(
              isUnlocked ? Icons.emoji_events : Icons.lock_outline,
              size: 35,
              color: isUnlocked ? badgeColor : Colors.grey,
            ),
          ),
          const SizedBox(height: 16),
          
          // Title
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Text(
              achievement.title,
              style: GoogleFonts.baloo2(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: isUnlocked ? AppTheme.textColor : Colors.grey,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(height: 8),
          
          // Description
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Text(
              achievement.description,
              style: GoogleFonts.inter(
                fontSize: 12,
                color: isUnlocked
                    ? AppTheme.textColor.withOpacity(0.6)
                    : Colors.grey.withOpacity(0.6),
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  /// Builds section title
  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.baloo2(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: AppTheme.textColor,
      ),
    );
  }

  /// Builds weekly activity bar chart
  Widget _buildWeeklyChart() {
    // Sample data - in real app would come from repository
    final days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    final activities = [2, 3, 1, 4, 2, 5, 3]; // Lessons completed per day

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        children: [
          AspectRatio(
            aspectRatio: 1.8,
            child: BarChart(
              BarChartData(
                alignment: BarChartAlignment.spaceAround,
                maxY: 6,
                barGroups: List.generate(7, (index) {
                  return BarChartGroupData(
                    x: index,
                    barRods: [
                      BarChartRodData(
                        toY: activities[index].toDouble(),
                        color: AppTheme.primaryColor,
                        width: 20,
                        borderRadius: const BorderRadius.vertical(
                          top: Radius.circular(6),
                        ),
                      ),
                    ],
                  );
                }),
                titlesData: FlTitlesData(
                  show: true,
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        return Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text(
                            days[value.toInt()],
                            style: GoogleFonts.inter(
                              fontSize: 12,
                              color: AppTheme.textColor.withOpacity(0.6),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                  leftTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  rightTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  topTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                ),
                gridData: const FlGridData(show: false),
                borderData: FlBorderData(show: false),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Lessons completed this week',
            style: GoogleFonts.inter(
              fontSize: 14,
              color: AppTheme.textColor.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }

  /// Builds skills radar chart
  Widget _buildSkillsRadarChart(Map<String, dynamic> skillLevels) {
    final skills = [
      'Letter Sounds',
      'Blending',
      'Sight Words',
      'Tracing',
      'Pronunciation',
    ];
    
    final values = [
      (skillLevels['letter_sounds'] ?? 0.4) * 100,
      (skillLevels['blending'] ?? 0.3) * 100,
      (skillLevels['sight_words'] ?? 0.2) * 100,
      (skillLevels['tracing'] ?? 0.5) * 100,
      (skillLevels['pronunciation'] ?? 0.25) * 100,
    ];

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: AppTheme.cardShadow,
      ),
      child: RadarChart(
        RadarChartData(
          dataSets: [
            RadarDataSet(
              entryAngle: 0,
              dataEntries: values
                  .map((v) => RadarEntry(value: v))
                  .toList(),
              borderColor: AppTheme.primaryColor,
              fillColor: AppTheme.primaryColor.withOpacity(0.3),
              borderWidth: 2,
            ),
          ],
          radarShape: RadarShape.polygon,
          getTitle: (index, angle) {
            return RadarChartTitle(
              text: skills[index],
              angle: angle,
            );
          },
          titleTextStyle: GoogleFonts.inter(
            fontSize: 11,
            color: AppTheme.textColor.withOpacity(0.7),
          ),
          radarBorderData: BorderSide(
            color: Colors.grey.withOpacity(0.3),
          ),
          gridBorderData: BorderSide(
            color: Colors.grey.withOpacity(0.2),
          ),
          tickBorderData: BorderSide.none,
          ticksTextStyle: const TextStyle(color: Colors.transparent),
          tickCount: 5,
        ),
      ),
    );
  }

  /// Builds skill progress bars
  Widget _buildSkillBars(Map<String, dynamic> skillLevels) {
    final skills = [
      {'name': 'Letter Sounds', 'key': 'letter_sounds', 'icon': Icons.record_voice_over},
      {'name': 'Blending', 'key': 'blending', 'icon': Icons.merge_type},
      {'name': 'Sight Words', 'key': 'sight_words', 'icon': Icons.visibility},
      {'name': 'Tracing', 'key': 'tracing', 'icon': Icons.edit},
      {'name': 'Pronunciation', 'key': 'pronunciation', 'icon': Icons.mic},
    ];

    return Column(
      children: skills.map((skill) {
        final value = (skillLevels[skill['key']] ?? 0.0) as double;
        final color = _getSkillColor(value);
        
        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: AppTheme.cardShadow,
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  skill['icon'] as IconData,
                  color: color,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      skill['name'] as String,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textColor,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: value,
                        backgroundColor: Colors.grey[200],
                        valueColor: AlwaysStoppedAnimation<Color>(color),
                        minHeight: 8,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Text(
                '${(value * 100).toInt()}%',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  /// Builds time statistics
  Widget _buildTimeStats() {
    final totalMinutes = _stats?['totalTimeSpentMinutes'] ?? 0;
    final hours = totalMinutes ~/ 60;
    final minutes = totalMinutes % 60;

    return Row(
      children: [
        Expanded(
          child: _buildTimeCard(
            icon: Icons.timer,
            value: '$hours',
            label: 'Hours',
            color: const Color(0xFF3498DB),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildTimeCard(
            icon: Icons.schedule,
            value: '$minutes',
            label: 'Minutes',
            color: const Color(0xFF27AE60),
          ),
        ),
      ],
    );
  }

  /// Builds time stat card
  Widget _buildTimeCard({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: GoogleFonts.baloo2(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 14,
              color: AppTheme.textColor.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }

  /// Builds level progress cards
  Widget _buildLevelProgress() {
    return Column(
      children: [
        _buildLevelProgressCard(
          level: 1,
          title: 'Single Letters',
          description: 'A - M',
          color: const Color(0xFF27AE60),
          progress: 0.7,
        ),
        const SizedBox(height: 12),
        _buildLevelProgressCard(
          level: 2,
          title: 'Simple Words',
          description: 'CAT, DOG, SUN',
          color: const Color(0xFF3498DB),
          progress: 0.3,
        ),
        const SizedBox(height: 12),
        _buildLevelProgressCard(
          level: 3,
          title: 'Blends',
          description: 'TR-, ST-, CL-',
          color: const Color(0xFFF39C12),
          progress: 0.0,
          locked: true,
        ),
        const SizedBox(height: 12),
        _buildLevelProgressCard(
          level: 4,
          title: 'Complex Words',
          description: 'Multi-syllable',
          color: const Color(0xFFE74C3C),
          progress: 0.0,
          locked: true,
        ),
      ],
    );
  }

  /// Builds level progress card
  Widget _buildLevelProgressCard({
    required int level,
    required String title,
    required String description,
    required Color color,
    required double progress,
    bool locked = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: locked ? Colors.grey[100] : Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: locked ? null : AppTheme.cardShadow,
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: locked ? Colors.grey[300] : color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(
                '$level',
                style: GoogleFonts.baloo2(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: locked ? Colors.grey : color,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: GoogleFonts.baloo2(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: locked ? Colors.grey : AppTheme.textColor,
                  ),
                ),
                Text(
                  description,
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: AppTheme.textColor.withOpacity(0.5),
                  ),
                ),
                if (!locked) ...[
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: progress,
                      backgroundColor: Colors.grey[200],
                      valueColor: AlwaysStoppedAnimation<Color>(color),
                      minHeight: 8,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (locked)
            Icon(Icons.lock, color: Colors.grey[400])
          else
            Text(
              '${(progress * 100).toInt()}%',
              style: GoogleFonts.inter(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
        ],
      ),
    );
  }

  /// Gets color based on skill level
  Color _getSkillColor(double value) {
    if (value >= 0.8) return AppTheme.successColor;
    if (value >= 0.5) return AppTheme.secondaryColor;
    if (value >= 0.3) return const Color(0xFFF39C12);
    return AppTheme.primaryColor;
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
            'Loading your progress...',
            style: GoogleFonts.inter(
              fontSize: 16,
              color: AppTheme.textColor.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }
}
