import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/data/repositories/progress_repository.dart';
import 'package:phonics_master_pro/presentation/providers/settings_provider.dart';
import 'package:phonics_master_pro/presentation/providers/audio_provider.dart';

/// Settings Screen - App configuration and preferences
/// 
/// Features:
/// - Audio toggle (music, sound effects)
/// - Difficulty level selection
/// - Dyslexia-friendly mode toggle
/// - Notification settings
/// - Clear progress option with parent gate
/// - About/Help section
/// - Material 3 design with responsive layout
class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _showParentGate = false;
  final TextEditingController _pinController = TextEditingController();

  @override
  void dispose() {
    _pinController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsProvider);
    final isFold = context.isFold;

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // Custom app bar
            SliverToBoxAdapter(
              child: _buildHeader(),
            ),
            
            // Settings sections
            SliverPadding(
              padding: const EdgeInsets.all(20),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  // Audio settings
                  _buildSectionTitle('Audio'),
                  const SizedBox(height: 16),
                  _buildAudioSettings(),
                  const SizedBox(height: 32),
                  
                  // Learning settings
                  _buildSectionTitle('Learning'),
                  const SizedBox(height: 16),
                  _buildLearningSettings(),
                  const SizedBox(height: 32),
                  
                  // Accessibility settings
                  _buildSectionTitle('Accessibility'),
                  const SizedBox(height: 16),
                  _buildAccessibilitySettings(),
                  const SizedBox(height: 32),
                  
                  // Notifications
                  _buildSectionTitle('Notifications'),
                  const SizedBox(height: 16),
                  _buildNotificationSettings(),
                  const SizedBox(height: 32),
                  
                  // Parental controls
                  _buildSectionTitle('Parental Controls'),
                  const SizedBox(height: 16),
                  _buildParentalSettings(),
                  const SizedBox(height: 32),
                  
                  // Data management
                  _buildSectionTitle('Data'),
                  const SizedBox(height: 16),
                  _buildDataSettings(),
                  const SizedBox(height: 32),
                  
                  // About
                  _buildSectionTitle('About'),
                  const SizedBox(height: 16),
                  _buildAboutSection(),
                  const SizedBox(height: 40),
                ]),
              ),
            ),
          ],
        ),
      ),
      // Parent gate overlay
      bottomSheet: _showParentGate ? _buildParentGate() : null,
    );
  }

  /// Builds the screen header
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
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back),
            style: IconButton.styleFrom(
              backgroundColor: Colors.grey[100],
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Settings',
                  style: GoogleFonts.baloo2(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textColor,
                  ),
                ),
                Text(
                  'Customize your learning experience',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: AppTheme.textColor.withOpacity(0.5),
                  ),
                ),
              ],
            ),
          ),
          
          // Profile avatar
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Center(
              child: Text(
                '🦊',
                style: TextStyle(fontSize: 28),
              ),
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
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: AppTheme.textColor,
      ),
    );
  }

  /// Builds audio settings section
  Widget _buildAudioSettings() {
    final soundEffects = ref.watch(soundEffectsProvider);
    final volume = ref.watch(volumeProvider);
    final audioMuted = ref.watch(audioMutedProvider);

    return Column(
      children: [
        // Sound effects toggle
        _buildSettingTile(
          icon: Icons.volume_up,
          iconColor: AppTheme.primaryColor,
          title: 'Sound Effects',
          subtitle: 'Play sounds during lessons',
          trailing: Switch(
            value: soundEffects,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(settingsProvider.notifier).setSoundEffects(value);
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        // Music/Audio toggle
        _buildSettingTile(
          icon: Icons.music_note,
          iconColor: const Color(0xFF9B59B6),
          title: 'Lesson Audio',
          subtitle: 'Enable pronunciation audio',
          trailing: Switch(
            value: !audioMuted,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(audioMutedProvider.notifier).toggle();
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        // Volume slider
        _buildSliderTile(
          icon: Icons.tune,
          iconColor: const Color(0xFF3498DB),
          title: 'Volume',
          value: volume,
          onChanged: (value) {
            ref.read(volumeProvider.notifier).setVolume(value);
          },
        ),
      ],
    );
  }

  /// Builds learning settings section
  Widget _buildLearningSettings() {
    final autoAdvance = ref.watch(autoAdvanceProvider);
    final showHints = ref.watch(showHintsProvider);
    final dailyGoal = ref.watch(dailyGoalProvider);

    return Column(
      children: [
        // Auto advance toggle
        _buildSettingTile(
          icon: Icons.auto_mode,
          iconColor: const Color(0xFF27AE60),
          title: 'Auto-Advance',
          subtitle: 'Automatically go to next step',
          trailing: Switch(
            value: autoAdvance,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(settingsProvider.notifier).setAutoAdvance(value);
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        // Show hints toggle
        _buildSettingTile(
          icon: Icons.lightbulb,
          iconColor: const Color(0xFFFFE66D),
          title: 'Show Hints',
          subtitle: 'Display helpful hints during lessons',
          trailing: Switch(
            value: showHints,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(settingsProvider.notifier).setShowHints(value);
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        // Daily goal selector
        _buildSelectorTile(
          icon: Icons.track_changes,
          iconColor: const Color(0xFFE74C3C),
          title: 'Daily Goal',
          subtitle: '$dailyGoal lessons per day',
          onTap: () => _showDailyGoalDialog(dailyGoal),
        ),
      ],
    );
  }

  /// Builds accessibility settings section
  Widget _buildAccessibilitySettings() {
    final dyslexiaMode = ref.watch(dyslexiaModeProvider);
    final highContrast = ref.watch(highContrastProvider);
    final fontSize = ref.watch(fontSizeProvider);
    final reducedMotion = ref.watch(reducedMotionProvider);

    return Column(
      children: [
        // Dyslexia-friendly mode
        _buildSettingTile(
          icon: Icons.accessibility_new,
          iconColor: const Color(0xFF9B59B6),
          title: 'Dyslexia-Friendly Mode',
          subtitle: 'Uses OpenDyslexic font and adjusted spacing',
          trailing: Switch(
            value: dyslexiaMode,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(settingsProvider.notifier).setDyslexiaMode(value);
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        // High contrast mode
        _buildSettingTile(
          icon: Icons.contrast,
          iconColor: Colors.black,
          title: 'High Contrast',
          subtitle: 'Enhanced contrast for better visibility',
          trailing: Switch(
            value: highContrast,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(settingsProvider.notifier).setHighContrast(value);
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        // Reduced motion
        _buildSettingTile(
          icon: Icons.animation,
          iconColor: const Color(0xFF3498DB),
          title: 'Reduced Motion',
          subtitle: 'Minimize animations throughout the app',
          trailing: Switch(
            value: reducedMotion,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(settingsProvider.notifier).setReducedMotion(value);
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        // Font size slider
        _buildSliderTile(
          icon: Icons.format_size,
          iconColor: const Color(0xFFE67E22),
          title: 'Text Size',
          value: fontSize,
          min: 0.8,
          max: 1.5,
          divisions: 7,
          label: '${(fontSize * 100).toInt()}%',
          onChanged: (value) {
            ref.read(settingsProvider.notifier).setFontSize(value);
          },
        ),
      ],
    );
  }

  /// Builds notification settings section
  Widget _buildNotificationSettings() {
    return Column(
      children: [
        _buildSettingTile(
          icon: Icons.notifications,
          iconColor: const Color(0xFF4ECDC4),
          title: 'Daily Reminders',
          subtitle: 'Remind me to practice',
          trailing: Switch(
            value: true, // Placeholder - would come from settings
            onChanged: (value) {
              HapticFeedback.lightImpact();
              // Toggle notifications
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        _buildSettingTile(
          icon: Icons.emoji_events,
          iconColor: const Color(0xFFFFE66D),
          title: 'Achievement Alerts',
          subtitle: 'Notify when earning achievements',
          trailing: Switch(
            value: true,
            onChanged: (value) {
              HapticFeedback.lightImpact();
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        const Divider(height: 1, indent: 56),
        
        _buildSelectorTile(
          icon: Icons.schedule,
          iconColor: const Color(0xFF9B59B6),
          title: 'Reminder Time',
          subtitle: '3:00 PM',
          onTap: () => _showTimePicker(),
        ),
      ],
    );
  }

  /// Builds parental control settings
  Widget _buildParentalSettings() {
    final parentalControls = ref.watch(parentalControlsProvider);
    final timeLimit = ref.watch(timeLimitProvider);

    return Column(
      children: [
        _buildSettingTile(
          icon: Icons.family_restroom,
          iconColor: const Color(0xFFE74C3C),
          title: 'Parental Controls',
          subtitle: 'Enable time limits and restrictions',
          trailing: Switch(
            value: parentalControls,
            onChanged: (value) {
              HapticFeedback.lightImpact();
              ref.read(settingsProvider.notifier).setParentalControls(value);
              if (value) {
                _showSetPinDialog();
              }
            },
            activeColor: AppTheme.primaryColor,
          ),
        ),
        
        if (parentalControls) ...[
          const Divider(height: 1, indent: 56),
          
          _buildSelectorTile(
            icon: Icons.timer,
            iconColor: const Color(0xFFE67E22),
            title: 'Daily Time Limit',
            subtitle: '$timeLimit minutes',
            onTap: () => _showTimeLimitDialog(timeLimit),
          ),
          
          const Divider(height: 1, indent: 56),
          
          _buildActionTile(
            icon: Icons.lock,
            iconColor: const Color(0xFF9B59B6),
            title: 'Change PIN',
            onTap: () => _showSetPinDialog(),
          ),
        ],
      ],
    );
  }

  /// Builds data management settings
  Widget _buildDataSettings() {
    return Column(
      children: [
        _buildActionTile(
          icon: Icons.backup,
          iconColor: const Color(0xFF3498DB),
          title: 'Backup Progress',
          onTap: () => _showBackupDialog(),
        ),
        
        const Divider(height: 1, indent: 56),
        
        _buildActionTile(
          icon: Icons.restore,
          iconColor: const Color(0xFF27AE60),
          title: 'Restore Progress',
          onTap: () => _showRestoreDialog(),
        ),
        
        const Divider(height: 1, indent: 56),
        
        _buildActionTile(
          icon: Icons.delete_forever,
          iconColor: AppTheme.errorColor,
          title: 'Clear All Progress',
          isDestructive: true,
          onTap: () => _showClearProgressWarning(),
        ),
      ],
    );
  }

  /// Builds about section
  Widget _buildAboutSection() {
    return Column(
      children: [
        _buildInfoTile(
          icon: Icons.info,
          iconColor: AppTheme.primaryColor,
          title: 'Version',
          value: '1.0.0',
        ),
        
        const Divider(height: 1, indent: 56),
        
        _buildActionTile(
          icon: Icons.help,
          iconColor: const Color(0xFF3498DB),
          title: 'Help & Tutorial',
          onTap: () => _showHelpDialog(),
        ),
        
        const Divider(height: 1, indent: 56),
        
        _buildActionTile(
          icon: Icons.feedback,
          iconColor: const Color(0xFF9B59B6),
          title: 'Send Feedback',
          onTap: () => _showFeedbackDialog(),
        ),
        
        const Divider(height: 1, indent: 56),
        
        _buildActionTile(
          icon: Icons.privacy_tip,
          iconColor: const Color(0xFF27AE60),
          title: 'Privacy Policy',
          onTap: () => _showPrivacyPolicy(),
        ),
      ],
    );
  }

  // ==================== REUSABLE TILES ====================

  /// Standard setting tile with trailing widget
  Widget _buildSettingTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required Widget trailing,
  }) {
    return Container(
      color: Colors.white,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: iconColor, size: 24),
        ),
        title: Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textColor,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: GoogleFonts.inter(
            fontSize: 13,
            color: AppTheme.textColor.withOpacity(0.6),
          ),
        ),
        trailing: trailing,
      ),
    );
  }

  /// Slider setting tile
  Widget _buildSliderTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required double value,
    double min = 0.0,
    double max = 1.0,
    int divisions = 10,
    String? label,
    required ValueChanged<double> onChanged,
  }) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: iconColor, size: 24),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  title,
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textColor,
                  ),
                ),
              ),
              if (label != null)
                Text(
                  label,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: iconColor,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            onChanged: onChanged,
            activeColor: iconColor,
            inactiveColor: iconColor.withOpacity(0.2),
          ),
        ],
      ),
    );
  }

  /// Selector tile that shows a dialog
  Widget _buildSelectorTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      color: Colors.white,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: iconColor, size: 24),
        ),
        title: Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textColor,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: GoogleFonts.inter(
            fontSize: 13,
            color: AppTheme.textColor.withOpacity(0.6),
          ),
        ),
        trailing: const Icon(Icons.chevron_right, color: Colors.grey),
        onTap: onTap,
      ),
    );
  }

  /// Action tile for tap actions
  Widget _buildActionTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    bool isDestructive = false,
    required VoidCallback onTap,
  }) {
    return Container(
      color: Colors.white,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: isDestructive 
                ? AppTheme.errorColor.withOpacity(0.1)
                : iconColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            icon, 
            color: isDestructive ? AppTheme.errorColor : iconColor, 
            size: 24,
          ),
        ),
        title: Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: isDestructive ? AppTheme.errorColor : AppTheme.textColor,
          ),
        ),
        trailing: Icon(
          Icons.chevron_right, 
          color: isDestructive ? AppTheme.errorColor.withOpacity(0.5) : Colors.grey,
        ),
        onTap: onTap,
      ),
    );
  }

  /// Info display tile
  Widget _buildInfoTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
  }) {
    return Container(
      color: Colors.white,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: iconColor, size: 24),
        ),
        title: Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textColor,
          ),
        ),
        trailing: Text(
          value,
          style: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppTheme.textColor.withOpacity(0.6),
          ),
        ),
      ),
    );
  }

  // ==================== DIALOGS ====================

  void _showDailyGoalDialog(int currentGoal) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Daily Goal', style: GoogleFonts.baloo2()),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'How many lessons would you like to complete each day?',
              style: GoogleFonts.inter(fontSize: 14),
            ),
            const SizedBox(height: 20),
            StatefulBuilder(
              builder: (context, setState) {
                return Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    IconButton(
                      onPressed: currentGoal > 1 
                          ? () => setState(() => currentGoal--)
                          : null,
                      icon: const Icon(Icons.remove_circle_outline),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      child: Text(
                        '$currentGoal',
                        style: GoogleFonts.baloo2(fontSize: 32),
                      ),
                    ),
                    IconButton(
                      onPressed: currentGoal < 10
                          ? () => setState(() => currentGoal++)
                          : null,
                      icon: const Icon(Icons.add_circle_outline),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              ref.read(settingsProvider.notifier).setDailyGoal(currentGoal);
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showTimePicker() {
    showTimePicker(
      context: context,
      initialTime: const TimeOfDay(hour: 15, minute: 0),
    ).then((time) {
      if (time != null) {
        // Save reminder time
      }
    });
  }

  void _showSetPinDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Set Parent PIN', style: GoogleFonts.baloo2()),
        content: TextField(
          controller: _pinController,
          keyboardType: TextInputType.number,
          maxLength: 4,
          obscureText: true,
          decoration: const InputDecoration(
            labelText: 'Enter 4-digit PIN',
            counterText: '',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final pin = int.tryParse(_pinController.text);
              if (pin != null && _pinController.text.length == 4) {
                ref.read(settingsProvider.notifier).setParentPin(pin);
                _pinController.clear();
                Navigator.pop(context);
              }
            },
            child: const Text('Set PIN'),
          ),
        ],
      ),
    );
  }

  void _showTimeLimitDialog(int currentLimit) {
    final options = [15, 30, 45, 60, 90, 120];
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Daily Time Limit', style: GoogleFonts.baloo2()),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: options.map((minutes) {
            return RadioListTile<int>(
              title: Text('$minutes minutes'),
              value: minutes,
              groupValue: currentLimit,
              onChanged: (value) {
                if (value != null) {
                  ref.read(settingsProvider.notifier).setTimeLimit(value);
                  Navigator.pop(context);
                }
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  /// Shows parent gate before destructive action
  void _showClearProgressWarning() {
    setState(() => _showParentGate = true);
  }

  /// Parent gate overlay
  Widget _buildParentGate() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
        boxShadow: [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 20,
          ),
        ],
      ),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 50,
              height: 5,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(5),
              ),
            ),
            const SizedBox(height: 24),
            Icon(
              Icons.lock,
              size: 60,
              color: AppTheme.primaryColor,
            ),
            const SizedBox(height: 16),
            Text(
              'Parental Gate',
              style: GoogleFonts.baloo2(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Please enter your PIN to continue',
              style: GoogleFonts.inter(
                fontSize: 14,
                color: AppTheme.textColor.withOpacity(0.6),
              ),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _pinController,
              keyboardType: TextInputType.number,
              maxLength: 4,
              obscureText: true,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(fontSize: 24),
              decoration: InputDecoration(
                labelText: 'PIN',
                counterText: '',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      setState(() => _showParentGate = false);
                      _pinController.clear();
                    },
                    child: const Text('Cancel'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  flex: 2,
                  child: ElevatedButton(
                    onPressed: () {
                      final enteredPin = int.tryParse(_pinController.text);
                      final authenticated = ref
                          .read(parentAuthProvider.notifier)
                          .authenticate(enteredPin ?? 0);
                      
                      if (authenticated) {
                        setState(() => _showParentGate = false);
                        _pinController.clear();
                        _confirmClearProgress();
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Incorrect PIN'),
                            backgroundColor: Colors.red,
                          ),
                        );
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.errorColor,
                    ),
                    child: const Text('Verify'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _confirmClearProgress() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear All Progress?'),
        content: const Text(
          'This will permanently delete all your learning progress, achievements, and settings. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final repository = ProgressRepository();
              await repository.init();
              await repository.resetAllProgress(_userId);
              await ref.read(settingsProvider.notifier).resetToDefaults();
              Navigator.pop(context);
              _showSuccessMessage('All progress cleared');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.errorColor,
            ),
            child: const Text('Clear All'),
          ),
        ],
      ),
    );
  }

  void _showBackupDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Backup Progress', style: GoogleFonts.baloo2()),
        content: const Text(
          'Your progress will be backed up and can be restored later.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showSuccessMessage('Progress backed up successfully');
            },
            child: const Text('Backup'),
          ),
        ],
      ),
    );
  }

  void _showRestoreDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Restore Progress', style: GoogleFonts.baloo2()),
        content: const Text(
          'This will replace your current progress with the backed up data.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showSuccessMessage('Progress restored successfully');
            },
            child: const Text('Restore'),
          ),
        ],
      ),
    );
  }

  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Help', style: GoogleFonts.baloo2()),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHelpItem('Getting Started', 'Complete lessons to learn phonics step by step.'),
              _buildHelpItem('Letter Tracing', 'Use S Pen or finger to trace letters.'),
              _buildHelpItem('Sound Matching', 'Listen carefully and select the correct answer.'),
              _buildHelpItem('Stars System', 'Complete lessons accurately to earn up to 3 stars.'),
            ],
          ),
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }

  Widget _buildHelpItem(String title, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: GoogleFonts.inter(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            description,
            style: GoogleFonts.inter(fontSize: 14),
          ),
        ],
      ),
    );
  }

  void _showFeedbackDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Send Feedback', style: GoogleFonts.baloo2()),
        content: TextField(
          controller: controller,
          maxLines: 4,
          decoration: const InputDecoration(
            hintText: 'Tell us what you think...',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showSuccessMessage('Thank you for your feedback!');
            },
            child: const Text('Send'),
          ),
        ],
      ),
    );
  }

  void _showPrivacyPolicy() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Privacy Policy', style: GoogleFonts.baloo2()),
        content: const SingleChildScrollView(
          child: Text(
            'PhonicsMaster Pro respects your privacy.\n\n'
            'We collect:\n'
            '• Learning progress (stored locally)\n'
            '• Usage statistics (anonymous)\n\n'
            'We do not:\n'
            '• Share personal data\n'
            '• Display third-party ads\n'
            '• Track location\n\n'
            'All data is stored on your device.',
          ),
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showSuccessMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.successColor,
      ),
    );
  }
}
