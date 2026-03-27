#!/bin/bash
# Generate placeholder audio files for PhonicsMaster Pro
# In production, replace with real TTS-generated audio

echo "Creating placeholder audio files..."

# Function to create placeholder MP3
create_placeholder() {
    local file=$1
    local freq=$2  # Frequency for different sounds
    ffmpeg -f lavfi -i "sine=frequency=${freq}:duration=0.5" -y "$file" 2>/dev/null
    echo "Created: $file"
}

# Create directories
echo "Setting up directories..."
for region in au us nz; do
    mkdir -p assets/audio/$region/letters
    mkdir -p assets/audio/$region/words
    mkdir -p assets/audio/$region/names
done

# Phase 1: SATPIN (6 letters)
echo "Phase 1: Letter sounds (S-A-T-P-I-N)"
declare -a phase1=("s" "a" "t" "p" "i" "n")
declare -a freq1=(440 466 494 523 554 587)  # Different frequencies

for region in au us nz; do
    idx=0
    for letter in "${phase1[@]}"; do
        create_placeholder "assets/audio/$region/letters/${letter}.mp3" ${freq1[$idx]}
        ((idx++))
    done
done

# Phase 2: CK-E-H-R-M-D (8 items including digraph CK)
echo "Phase 2: Letter sounds (C-K-CK-E-H-R-M-D)"
declare -a phase2=("c" "k" "ck" "e" "h" "r" "m" "d")
declare -a freq2=(329 349 369 392 415 440 466 494)

for region in au us nz; do
    idx=0
    for letter in "${phase2[@]}"; do
        # Remove problematic chars for filename
        safe_letter=$(echo $letter | tr -cd '[:alnum:]')
        create_placeholder "assets/audio/$region/letters/${safe_letter}.mp3" ${freq2[$idx]}
        ((idx++))
    done
done

# Phase 3: G-O-U-L-F-B
echo "Phase 3: Letter sounds (G-O-U-L-F-B)"
declare -a phase3=("g" "o" "u" "l" "f" "b")
declare -a freq3=(349 370 392 415 440 466)

for region in au us nz; do
    idx=0
    for letter in "${phase3[@]}"; do
        create_placeholder "assets/audio/$region/letters/${letter}.mp3" ${freq3[$idx]}
        ((idx++))
    done
done

# Phase 4: J-Z-W-X-Y-Qu-V
echo "Phase 4: Letter sounds (J-Z-W-X-Y-Qu-V)"
declare -a phase4=("j" "z" "w" "x" "y" "qu" "v")
declare -a freq4=(523 554 587 622 659 494 440)

for region in au us nz; do
    idx=0
    for letter in "${phase4[@]}"; do
        safe_letter=$(echo $letter | tr -cd '[:alnum:]')
        create_placeholder "assets/audio/$region/letters/${safe_letter}.mp3" ${freq4[$idx]}
        ((idx++))
    done
done

# Phase 5: Digraphs (ai-ee-igh-oa-oo-sh-ch-th-ng)
echo "Phase 5: Digraph sounds"
declare -a phase5=("ai" "ee" "igh" "oa" "oo" "sh" "ch" "th" "ng")
declare -a freq5=(523 554 587 622 349 415 659 392 440)

for region in au us nz; do
    idx=0
    for letter in "${phase5[@]}"; do
        safe_letter=$(echo $letter | tr -cd '[:alnum:]')
        create_placeholder "assets/audio/$region/letters/${safe_letter}.mp3" ${freq5[$idx]}
        ((idx++))
    done
done

# Create sample CVC words
echo ""
echo "Creating sample CVC word audio..."

declare -a sample_words=(
    # Phase 1 words (SATPIN only)
    "sat" "pat" "pin" "tin" "pan" "nap" "sip" "tip" "tan" "tap" 
    "ant" "net" "nip" "pit" "sit" "sap" "sin" "inn"
    # Phase 2 words (adds C K E H R M D)
    "cat" "cap" "cup" "cut" "can" "cot" "bed" "red" "hen" "hat"
    "hit" "hot" "hop" "man" "mat" "map" "mad" "mud" "mop" "ran"
    "rat" "rip" "rid" "dog" "dip" "dot" "den" "dig" "egg" "end"
    # Phase 3 words (adds G O U L F B)
    "got" "gas" "gum" "gut" "big" "bug" "bag" "bat" "bet" "bit"
    "but" "tub" "cub" "rub" "hug" "jug" "mug" "rug" "tug" "pug"
    "fig" "gig" "pig" "bun" "fun" "gun" "run" "sun" "cut" "hut"
    # Phase 4 words (adds J Z W X Y Qu V)
    "jam" "jet" "jug" "zip" "zap" "zoo" "wet" "win" "web" "wax"
    "won" "box" "fox" "six" "mix" "yes" "yak" "yap" "yum" "van"
    "vet" "queen" "quack" "quit" "quiz"
)

declare -a word_freqs=(
    262 277 294 311 330 349 370 392 415 440
    466 494 523 554 587 622 659 698 740 784
    831 880 932 988 1047 1109 1175 1245 1319 1397
    1480 1568 1661 1760 1865 1976 2093 2217 2349 2489
    2637 2794 2960 3136 3322 3520 3729 3951 4186 4435
)

for region in au us nz; do
    idx=0
    for word in "${sample_words[@]}"; do
        freq_idx=$((idx % ${#word_freqs[@]}))
        create_placeholder "assets/audio/$region/words/${word}.mp3" ${word_freqs[$freq_idx]}
        ((idx++))
    done
done

echo ""
echo "Audio generation complete!"
echo ""
echo "Summary:"
for region in au us nz; do
    letter_count=$(ls assets/audio/$region/letters/*.mp3 2>/dev/null | wc -l)
    word_count=$(ls assets/audio/$region/words/*.mp3 2>/dev/null | wc -l)
    echo "  $region: $letter_count letters + $word_count words"
done

echo ""
echo "Note: These are placeholder audio files."
echo "Replace with real TTS audio for production use."

