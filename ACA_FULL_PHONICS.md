# ACA Plan: Full Phonics App with Audio

## 1. Requirements Gathering
- Extend to ALL phonics phases (1-5)
- Generate ALL possible CVC words
- Create real audio files for letters + words
- AU/NZ/US regional variants

## 2. Architecture Design
```
phonics_data.dart (extended)
  ├── Phase 1: SATPIN (6 letters)
  ├── Phase 2: CK-E-H-R-M-D (7 letters + digraph)
  ├── Phase 3: G-O-U-L-F-B (6 letters)
  ├── Phase 4: J-Z-W-X-Y-Qu-V (7 letters + digraph)
  └── Phase 5: Long vowels + digraphs

CVC Word Generator
  └── All consonant-vowel-consonant combinations

Audio Generation Pipeline
  └── TTS → MP3 → assets/audio/{region}/
```

## 3. Data Flow
1. Generate letter list
2. Generate CVC word list (per phase, decodable)
3. TTS generate letter sounds
4. TTS generate word pronunciations
5. Copy to Flutter assets structure

## 4. Edge Cases
- TTS service unavailable → log error, continue
- Word list too long → batch processing
- Disk space → warn if >50MB
- Duplicate words → deduplicate

## 5. Tool Constraints
- TTS: elevenlabs or system TTS
- Format: MP3, 44.1kHz, mono
- Size: ~500 files × 50KB = ~25MB

## 6. Error Handling
- Try-catch on each TTS call
- Continue on failure, don't stop batch
- Log failures for manual retry

## 7. Testing
- Verify file count
- Play sample audio
- Check file sizes

## Phase Breakdown

**Phase 1 (Letters 1-6):** S, A, T, P, I, N - SATPIN
**Phase 2 (Letters 7-13):** C, K, CK, E, H, R, M, D
**Phase 3 (Letters 14-19):** G, O, U, L, F, B
**Phase 4 (Letters 20-26):** J, Z, W, X, Y, Qu, V
**Phase 5:** Long vowels, sh, ch, th, ng, ai, ee, oa, oo

## CVC Word Calculation
- 20 consonants × 5 short vowels × 20 consonants = ~2,000 possible
- Realistic decodable: ~200-500 words per phase
- Total: ~1,500-2,000 CVC words across all phases
