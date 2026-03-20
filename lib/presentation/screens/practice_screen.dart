import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:phonics_master_pro/core/theme/app_theme.dart';
import 'package:phonics_master_pro/data/models/phonics_letter.dart';
import 'package:phonics_master_pro/data/models/word_tile.dart';
import 'package:phonics_master_pro/presentation/providers/lesson_provider.dart';
import 'package:phonics_master_pro/presentation/providers/audio_provider.dart';
import 'package:phonics_master_pro/presentation/screens/letter_tracing_screen.dart';
import 'package:phonics_master_pro/presentation/widgets/letter_card.dart';

class PracticeScreen extends ConsumerStatefulWidget {
  const PracticeScreen({super.key});

  @override
  ConsumerState<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends ConsumerState<PracticeScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _selectedCategory = 'All';
  int _selectedLevel = 1;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final words = ref.watch(wordLibraryProvider);
    
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            _buildHeader(),
            
            // Tab bar
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(12),
              ),
              child: TabBar(
                controller: _tabController,
                indicator: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(10),
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
                ),
                tabs: const [
                  Tab(text: 'Letters'),
                  Tab(text: 'Words'),
                  Tab(text: 'Games'),
                ],
              ),
            ),
            
            // Tab content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildLettersTab(),
                  _buildWordsTab(words),
                  _buildGamesTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back),
            style: IconButton.styleFrom(
              backgroundColor: Colors.white,
            ),
          ),
          const SizedBox(width: 16),
          Text(
            'Practice',
            style: GoogleFonts.baloo2(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildLettersTab() {
    final letters = PhonicsLetter.allLetters;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Instructions
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.secondaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: AppTheme.secondaryColor.withOpacity(0.3),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.touch_app,
                  color: AppTheme.secondaryColor,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Tap a letter to practice tracing with S Pen',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      color: AppTheme.textColor.withOpacity(0.8),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Vowels section
          Text(
            'Vowels',
            style: GoogleFonts.baloo2(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 3,
              childAspectRatio: 0.85,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: letters.where((l) => l.isVowel).length,
            itemBuilder: (context, index) {
              final vowels = letters.where((l) => l.isVowel).toList();
              return LetterCard(
                letter: vowels[index],
                isCompact: true,
                showExample: true,
              );
            },
          ),
          
          const SizedBox(height: 32),
          
          // Consonants section
          Text(
            'Consonants',
            style: GoogleFonts.baloo2(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 3,
              childAspectRatio: 0.85,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: letters.where((l) => !l.isVowel).length,
            itemBuilder: (context, index) {
              final consonants = letters.where((l) => !l.isVowel).toList();
              return LetterCard(
                letter: consonants[index],
                isCompact: true,
                showExample: true,
              );
            },
          ),
        ],
      ),
    );
  }
  
  Widget _buildWordsTab(List<WordTile> words) {
    final categories = ['All'] + WordLibrary.categories;
    
    return Column(
      children: [
        // Category filter
        Container(
          height: 50,
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final category = categories[index];
              final isSelected = _selectedCategory == category;
              
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(category),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      _selectedCategory = selected ? category : 'All';
                    });
                  },
                  selectedColor: AppTheme.primaryColor,
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : AppTheme.textColor,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              );
            },
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Words grid
        Expanded(
          child: GridView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 1.2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            itemCount: _getFilteredWords(words).length,
            itemBuilder: (context, index) {
              final word = _getFilteredWords(words)[index];
              return _buildWordCard(word);
            },
          ),
        ),
      ],
    );
  }
  
  List<WordTile> _getFilteredWords(List<WordTile> words) {
    if (_selectedCategory == 'All') return words;
    return words.where((w) => w.category == _selectedCategory).toList();
  }
  
  Widget _buildWordCard(WordTile word) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.mediumImpact();
        ref.read(soundEffectsProvider).playClick();
        ref.read(audioPlaybackProvider.notifier).playWord(word.word);
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: AppTheme.cardShadow,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: AppTheme.secondaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: Text(
                  word.word[0].toUpperCase(),
                  style: GoogleFonts.baloo2(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.secondaryColor,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              word.displayWord,
              style: GoogleFonts.baloo2(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
            if (word.category != null)
              Text(
                word.category!,
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: AppTheme.textColor.withOpacity(0.5),
                ),
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildGamesTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Practice Games',
            style: GoogleFonts.baloo2(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          
          // Game cards
          _buildGameCard(
            title: 'Letter Match',
            description: 'Match letters with their sounds',
            icon: Icons.matching_game,
            color: const Color(0xFFFF6B6B),
            onTap: () {},
          ),
          const SizedBox(height: 16),
          
          _buildGameCard(
            title: 'Word Builder',
            description: 'Build words from letters',
            icon: Icons.build,
            color: const Color(0xFF4ECDC4),
            onTap: () {},
          ),
          const SizedBox(height: 16),
          
          _buildGameCard(
            title: 'Sound Detective',
            description: 'Listen and identify sounds',
            icon: Icons.hearing,
            color: const Color(0xFF9B59B6),
            onTap: () {},
          ),
          const SizedBox(height: 16),
          
          _buildGameCard(
            title: 'Speed Challenge',
            description: 'How fast can you read?',
            icon: Icons.speed,
            color: const Color(0xFFE67E22),
            onTap: () {},
          ),
        ],
      ),
    );
  }
  
  Widget _buildGameCard({
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.mediumImpact();
        onTap();
      },
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: AppTheme.cardShadow,
        ),
        child: Row(
          children: [
            Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(
                icon,
                size: 32,
                color: color,
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
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textColor,
                    ),
                  ),
                  Text(
                    description,
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      color: AppTheme.textColor.withOpacity(0.6),
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              color: color,
            ),
          ],
        ),
      ),
    );
  }
}