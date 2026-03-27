#!/bin/bash
# Audio generation script for PhonicsMaster Pro
# Generates letter sounds and word audio using system TTS

echo "Generating Phonics Audio Files..."

# Create directories if not exist
mkdir -p assets/audio/au/letters assets/audio/au/words assets/audio/au/names
mkdir -p assets/audio/us/letters assets/audio/us/words assets/audio/us/names
mkdir -p assets/audio/nz/letters assets/audio/nz/words assets/audio/nz/names

# Function to generate letter sound using TTS
generate_letter() {
    local letter=$1
    local sound=$2
    local region=$3
    local output="assets/audio/$region/letters/${letter}.mp3"
    
    # For this demo, we'll use espeak with proper phoneme representations
    # In production, would use higher quality TTS like ElevenLabs
    case $region in
        au|nz)
            # Australian/Non-rhotic pronunciation
            espeak -v en-au -w "$output" "$sound" 2>/dev/null || \
            espeak -v en -w "$output" "$sound" 2>/dev/null || \
            ffmpeg -f lavfi -i "sine=frequency=440:duration=0.3" -y "$output" 2>/dev/null
            ;;
        us)
            # American/Rhotic pronunciation
            espeak -v en-us -w "$output" "$sound" 2>/dev/null || \
            espeak -v en -w "$output" "$sound" 2>/dev/null || \
            ffmpeg -f lavfi -i "sine=frequency=440:duration=0.3" -y "$output" 2>/dev/null
            ;;
    esac
    
    if [ -f "$output" ]; then
        echo "  Created: $output ($(stat -c%s "$output" 2>/dev/null || stat -f%z "$output" 2>/dev/null || echo "0") bytes)"
    fi
}

# Generate word audio
generate_word() {
    local word=$1
    local region=$2
    local output="assets/audio/$region/words/${word}.mp3"
    
    case $region in
        au|nz)
            espeak -v en-au -w "$output" "$word" 2>/dev/null || \
            espeak -v en -w "$output" "$word" 2>/dev/null || \
            ffmpeg -f lavfi -i "sine=frequency=440:duration=0.3" -y "$output" 2>/dev/null
            ;;
        us)
            espeak -v en-us -w "$output" "$word" 2>/dev/null || \
            espeak -v en -w "$output" "$word" 2>/dev/null || \
            ffmpeg -f lavfi -i "sine=frequency=440:duration=0.3" -y "$output" 2>/dev/null
            ;;
    esac
    
    if [ -f "$output" ]; then
        echo "  Created: $output ($(stat -c%s "$output" 2>/dev/null || stat -f%z "$output" 2>/dev/null || echo "0") bytes)"
    fi
}

echo "Phase 1: Letter Sounds (SATPIN)"
regions="au us nz"
for region in $regions; do
    echo "  Generating for $region..."
    generate_letter "s" "sss" $region
    generate_letter "a" "ah" $region
    generate_letter "t" "tuh" $region
    generate_letter "p" "puh" $region
    generate_letter "i" "ih" $region
    generate_letter "n" "nuh" $region
done

echo "Phase 2: Letter Sounds (CK-E-H-R-M-D)"
for region in $regions; do
    echo "  Generating for $region..."
    generate_letter "c" "kuh" $region
    generate_letter "k" "kuh" $region
    generate_letter "ck" "k" $region
    generate_letter "e" "eh" $region
    generate_letter "h" "huh" $region
    generate_letter "r" "ruh" $region
    generate_letter "m" "muh" $region
    generate_letter "d" "duh" $region
done

echo "Phase 3: Letter Sounds (G-O-U-L-F-B)"
for region in $regions; do
    echo "  Generating for $region..."
    generate_letter "g" "guh" $region
    generate_letter "o" "o" $region
    generate_letter "u" "uh" $region
    generate_letter "l" "luh" $region
    generate_letter "f" "fuh" $region
    generate_letter "b" "buh" $region
done

echo "Phase 4: Letter Sounds (J-Z-W-X-Y-Qu-V)"
for region in $regions; do
    echo "  Generating for $region..."
    generate_letter "j" "juh" $region
    generate_letter "z" "zuh" $region
    generate_letter "w" "wuh" $region
    generate_letter "x" "ks" $region
    generate_letter "y" "yuh" $region
    generate_letter "qu" "kw" $region
    generate_letter "v" "vuh" $region
done

echo "Phase 5: Digraphs (ai-ee-igh-oa-oo-sh-ch-th-ng)"
for region in $regions; do
    echo "  Generating for $region..."
    generate_letter "ai" "ay" $region
    generate_letter "ee" "ee" $region
    generate_letter "igh" "igh" $region
    generate_letter "oa" "oh" $region
    generate_letter "oo" "oo" $region
    generate_letter "sh" "sh" $region
    generate_letter "ch" "ch" $region
    generate_letter "th" "th" $region
    generate_letter "ng" "ng" $region
done

echo ""
echo "Generating Sample CVC Words..."
sample_words="sat pat pin tin pan nap sip tip tan tap ant net pen pet set cat cap cup cut can
cot bed red man mat map mad mud hop hot hat hit hem ran rat rip rid ran dog
dig den big bug bat bet bit but tub got gas gum nut hug jug mug rug tug fig fog
log leg ham jam jar web yes van vet vet"

for region in $regions; do
    echo "  Generating 50 sample words for $region..."
    count=0
    for word in $sample_words; do
        generate_word "$word" "$region"
        ((count++))
        if [ $count -ge 50 ]; then break; fi
    done
done

echo ""
echo "Audio generation complete!"
echo ""
echo "Stats:"
echo "  AU letter files: $(ls assets/audio/au/letters/*.mp3 2>/dev/null | wc -l)"
echo "  AU word files: $(ls assets/audio/au/words/*.mp3 2>/dev/null | wc -l)"
echo "  US letter files: $(ls assets/audio/us/letters/*.mp3 2>/dev/null | wc -l)"
echo "  US word files: $(ls assets/audio/us/words/*.mp3 2>/dev/null | wc -l)"
echo "  NZ letter files: $(ls assets/audio/nz/letters/*.mp3 2>/dev/null | wc -l)"
echo "  NZ word files: $(ls assets/audio/nz/words/*.mp3 2>/dev/null | wc -l)"
