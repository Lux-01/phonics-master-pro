class PhonicsData {
  // =====================================================
  // PHASE 1: SATPIN (Letters 1-6)
  // First 6 letters that create 20+ CVC words immediately
  // =====================================================
  static const List<Map<String, dynamic>> phase1 = [
    {
      'letter': 'S',
      'sound': 'sss',
      'exampleWords': ['sun', 'sip', 'sat'],
      'animal': {'name': 'Snake', 'emoji': '🐍'},
      'action': 'slither',
      'phase': 1,
    },
    {
      'letter': 'A',
      'sound': 'a',
      'exampleWords': ['ant', 'apple', 'sat'],
      'animal': {'name': 'Ant', 'emoji': '🐜'},
      'action': 'march',
      'phase': 1,
    },
    {
      'letter': 'T',
      'sound': 't',
      'exampleWords': ['tiger', 'top', 'tin'],
      'animal': {'name': 'Tiger', 'emoji': '🐯'},
      'action': 'pounce',
      'phase': 1,
    },
    {
      'letter': 'P',
      'sound': 'p',
      'exampleWords': ['pig', 'pan', 'pat'],
      'animal': {'name': 'Penguin', 'emoji': '🐧'},
      'action': 'waddle',
      'phase': 1,
    },
    {
      'letter': 'I',
      'sound': 'i',
      'exampleWords': ['iguana', 'in', 'pin'],
      'animal': {'name': 'Iguana', 'emoji': '🦎'},
      'action': 'crawl',
      'phase': 1,
    },
    {
      'letter': 'N',
      'sound': 'n',
      'exampleWords': ['nut', 'nap', 'tin'],
      'animal': {'name': 'Newt', 'emoji': '🦎'},
      'action': 'creep',
      'phase': 1,
    },
  ];

  // =====================================================
  // PHASE 2: CK-E-H-R-M-D + C/K split (Letters 7-13)
  // =====================================================
  static const List<Map<String, dynamic>> phase2 = [
    {
      'letter': 'C',
      'sound': 'k',
      'exampleWords': ['cat', 'cup', 'cap'],
      'animal': {'name': 'Crocodile', 'emoji': '🐊'},
      'action': 'snap',
      'phase': 2,
    },
    {
      'letter': 'K',
      'sound': 'k',
      'exampleWords': ['kite', 'kid', 'kit'],
      'animal': {'name': 'Koala', 'emoji': '🐨'},
      'action': 'climb',
      'phase': 2,
    },
    {
      'letter': 'CK',
      'sound': 'k',
      'exampleWords': ['duck', 'sock', 'sick'],
      'animal': {'name': 'Chicken', 'emoji': '🐔'},
      'action': 'peck',
      'phase': 2,
      'isDigraph': true,
    },
    {
      'letter': 'E',
      'sound': 'e',
      'exampleWords': ['egg', 'end', 'pen'],
      'animal': {'name': 'Elephant', 'emoji': '🐘'},
      'action': 'stomp',
      'phase': 2,
    },
    {
      'letter': 'H',
      'sound': 'h',
      'exampleWords': ['hat', 'hen', 'hop'],
      'animal': {'name': 'Hippo', 'emoji': '🦛'},
      'action': 'splash',
      'phase': 2,
    },
    {
      'letter': 'R',
      'sound': 'r',
      'exampleWords': ['rat', 'red', 'rip'],
      'animal': {'name': 'Rabbit', 'emoji': '🐰'},
      'action': 'hop',
      'phase': 2,
    },
    {
      'letter': 'M',
      'sound': 'm',
      'exampleWords': ['man', 'mat', 'map'],
      'animal': {'name': 'Monkey', 'emoji': '🐵'},
      'action': 'swing',
      'phase': 2,
    },
    {
      'letter': 'D',
      'sound': 'd',
      'exampleWords': ['dog', 'dad', 'dip'],
      'animal': {'name': 'Dolphin', 'emoji': '🐬'},
      'action': 'leap',
      'phase': 2,
    },
  ];

  // =====================================================
  // PHASE 3: G-O-U-L-F-B (Letters 14-19)
  // =====================================================
  static const List<Map<String, dynamic>> phase3 = [
    {
      'letter': 'G',
      'sound': 'g',
      'exampleWords': ['goat', 'gas', 'got'],
      'animal': {'name': 'Gorilla', 'emoji': '🦍'},
      'action': 'beat',
      'phase': 3,
    },
    {
      'letter': 'O',
      'sound': 'o',
      'exampleWords': ['octopus', 'on', 'pot'],
      'animal': {'name': 'Owl', 'emoji': '🦉'},
      'action': 'hoot',
      'phase': 3,
    },
    {
      'letter': 'U',
      'sound': 'u',
      'exampleWords': ['umbrella', 'up', 'cup'],
      'animal': {'name': 'Unicorn', 'emoji': '🦄'},
      'action': 'gallop',
      'phase': 3,
    },
    {
      'letter': 'L',
      'sound': 'l',
      'exampleWords': ['leg', 'lip', 'lot'],
      'animal': {'name': 'Lion', 'emoji': '🦁'},
      'action': 'roar',
      'phase': 3,
    },
    {
      'letter': 'F',
      'sound': 'f',
      'exampleWords': ['fox', 'fan', 'fat'],
      'animal': {'name': 'Fox', 'emoji': '🦊'},
      'action': 'dash',
      'phase': 3,
    },
    {
      'letter': 'B',
      'sound': 'b',
      'exampleWords': ['bat', 'bed', 'big'],
      'animal': {'name': 'Bear', 'emoji': '🐻'},
      'action': 'growl',
      'phase': 3,
    },
  ];

  // =====================================================
  // PHASE 4: J-Z-W-X-Y-Qu-V (Letters 20-26 + digraphs)
  // =====================================================
  static const List<Map<String, dynamic>> phase4 = [
    {
      'letter': 'J',
      'sound': 'j',
      'exampleWords': ['jam', 'jet', 'jump'],
      'animal': {'name': 'Jellyfish', 'emoji': '🎐'},
      'action': 'float',
      'phase': 4,
    },
    {
      'letter': 'Z',
      'sound': 'z',
      'exampleWords': ['zip', 'zap', 'zoo'],
      'animal': {'name': 'Zebra', 'emoji': '🦓'},
      'action': 'gallop',
      'phase': 4,
    },
    {
      'letter': 'W',
      'sound': 'w',
      'exampleWords': ['wet', 'win', 'web'],
      'animal': {'name': 'Whale', 'emoji': '🐋'},
      'action': 'spout',
      'phase': 4,
    },
    {
      'letter': 'X',
      'sound': 'ks',
      'exampleWords': ['box', 'fox', 'six'],
      'animal': {'name': 'X-ray Fish', 'emoji': '🐟'},
      'action': 'swim',
      'phase': 4,
    },
    {
      'letter': 'Y',
      'sound': 'y',
      'exampleWords': ['yes', 'yak', 'yap'],
      'animal': {'name': 'Yak', 'emoji': '🦬'},
      'action': 'grunt',
      'phase': 4,
    },
    {
      'letter': 'Qu',
      'sound': 'kw',
      'exampleWords': ['queen', 'quit', 'quiz'],
      'animal': {'name': 'Quail', 'emoji': '🦆'},
      'action': 'flutter',
      'phase': 4,
      'isDigraph': true,
    },
    {
      'letter': 'V',
      'sound': 'v',
      'exampleWords': ['vet', 'van', 'vase'],
      'animal': {'name': 'Vulture', 'emoji': '🦅'},
      'action': 'soar',
      'phase': 4,
    },
  ];

  // =====================================================
  // PHASE 5: Long Vowels + Digraphs
  // =====================================================
  static const List<Map<String, dynamic>> phase5 = [
    {
      'letter': 'ai',
      'sound': 'ay',
      'exampleWords': ['rain', 'train', 'pain'],
      'animal': {'name': 'Ape', 'emoji': '🐒'},
      'action': 'swing',
      'phase': 5,
      'isDigraph': true,
      'type': 'long_vowel',
    },
    {
      'letter': 'ee',
      'sound': 'ee',
      'exampleWords': ['tree', 'bee', 'see'],
      'animal': {'name': 'Eagle', 'emoji': '🦅'},
      'action': 'soar',
      'phase': 5,
      'isDigraph': true,
      'type': 'long_vowel',
    },
    {
      'letter': 'igh',
      'sound': 'i',
      'exampleWords': ['night', 'light', 'fight'],
      'animal': {'name': 'Firefly', 'emoji': '✨'},
      'action': 'glow',
      'phase': 5,
      'isTrigraph': true,
      'type': 'long_vowel',
    },
    {
      'letter': 'oa',
      'sound': 'o',
      'exampleWords': ['boat', 'coat', 'goat'],
      'animal': {'name': 'Otter', 'emoji': '🦦'},
      'action': 'float',
      'phase': 5,
      'isDigraph': true,
      'type': 'long_vowel',
    },
    {
      'letter': 'oo',
      'sound': 'oo',
      'exampleWords': ['moon', 'soon', 'spoon'],
      'animal': {'name': 'Ostrich', 'emoji': '🐦'},
      'action': 'run',
      'phase': 5,
      'isDigraph': true,
      'type': 'long_vowel',
    },
    {
      'letter': 'sh',
      'sound': 'sh',
      'exampleWords': ['ship', 'shop', 'fish'],
      'animal': {'name': 'Sheep', 'emoji': '🐑'},
      'action': 'baa',
      'phase': 5,
      'isDigraph': true,
      'type': 'consonant_digraph',
    },
    {
      'letter': 'ch',
      'sound': 'ch',
      'exampleWords': ['chip', 'chop', 'chin'],
      'animal': {'name': 'Cheetah', 'emoji': '🐆'},
      'action': 'chirp',
      'phase': 5,
      'isDigraph': true,
      'type': 'consonant_digraph',
    },
    {
      'letter': 'th',
      'sound': 'th',
      'exampleWords': ['thin', 'this', 'that'],
      'animal': {'name': 'Thorny Devil', 'emoji': '🦎'},
      'action': 'crawl',
      'phase': 5,
      'isDigraph': true,
      'type': 'consonant_digraph',
    },
    {
      'letter': 'ng',
      'sound': 'ng',
      'exampleWords': ['sing', 'song', 'ring'],
      'animal': {'name': 'Nightingale', 'emoji': '🐦'},
      'action': 'sing',
      'phase': 5,
      'isDigraph': true,
      'type': 'consonant_digraph',
    },
  ];

  // =====================================================
  // ALL PHASES COMBINED
  // =====================================================
  static List<Map<String, dynamic>> get allLetters => [
    ...phase1,
    ...phase2,
    ...phase3,
    ...phase4,
    ...phase5,
  ];

  static List<Map<String, dynamic>> getLettersForPhase(int phase) {
    switch (phase) {
      case 1:
        return phase1;
      case 2:
        return phase2;
      case 3:
        return phase3;
      case 4:
        return phase4;
      case 5:
        return phase5;
      default:
        return allLetters;
    }
  }

  static int get totalLetters => allLetters.length;
  static int get totalPhases => 5;

  // =====================================================
  // PHASE 1 CVC WORDS (letters: S A T P I N)
  // =====================================================
  static const List<Map<String, dynamic>> phase1CVCWords = [
    {'word': 'sat', 'image': '💺', 'meaning': 'Past tense of sit', 'decodable': true},
    {'word': 'pat', 'image': '👋', 'meaning': 'Gentle touch', 'decodable': true},
    {'word': 'pin', 'image': '📌', 'meaning': 'Small sharp fastener', 'decodable': true},
    {'word': 'tin', 'image': '🥫', 'meaning': 'Metal container', 'decodable': true},
    {'word': 'pan', 'image': '🍳', 'meaning': 'Cooking container', 'decodable': true},
    {'word': 'nap', 'image': '😴', 'meaning': 'Short sleep', 'decodable': true},
    {'word': 'sip', 'image': '🍵', 'meaning': 'Small drink', 'decodable': true},
    {'word': 'tip', 'image': '💰', 'meaning': 'Money for service', 'decodable': true},
    {'word': 'tan', 'image': '🏖️', 'meaning': 'Brown from sun', 'decodable': true},
    {'word': 'tap', 'image': '🚿', 'meaning': 'Faucet or light hit', 'decodable': true},
    {'word': 'pit', 'image': '🕳️', 'meaning': 'Hole in ground', 'decodable': true},
    {'word': 'sit', 'image': '🪑', 'meaning': 'Rest on seat', 'decodable': true},
    {'word': 'nip', 'image': '🤏', 'meaning': 'Small bite', 'decodable': true},
    {'word': 'sap', 'image': '🌳', 'meaning': 'Liquid from trees', 'decodable': true},
    {'word': 'sin', 'image': '😈', 'meaning': 'Wrong doing', 'decodable': true},
    {'word': 'ant', 'image': '🐜', 'meaning': 'Small insect', 'decodable': true},
    {'word': 'inn', 'image': '🏨', 'meaning': 'Small hotel', 'decodable': true},
    {'word': 'sap', 'image': '🌲', 'meaning': 'Tree juice', 'decodable': true},
    {'word': 'tan', 'image': '🏜️', 'meaning': 'Sun brown', 'decodable': true},
    {'word': 'tin', 'image': '🔩', 'meaning': 'Silvery metal', 'decodable': true},
    {'word': 'tip', 'image': '💵', 'meaning': 'Extra money', 'decodable': true},
    {'word': 'tins', 'image': '🥫', 'meaning': 'Many cans', 'decodable': false},
    {'word': 'pans', 'image': '🍳', 'meaning': 'Many pans', 'decodable': false},
    {'word': 'pins', 'image': '📌', 'meaning': 'Many pins', 'decodable': false},
    {'word': 'naps', 'image': '😴', 'meaning': 'Many naps', 'decodable': false},
    {'word': 'pets', 'image': '🐕', 'meaning': 'Animal friends', 'decodable': false},
    {'word': 'net', 'image': '🕸️', 'meaning': 'Web trap', 'decodable': true},
    {'word': 'ten', 'image': '🔟', 'meaning': 'Number 10', 'decodable': true},
    {'word': 'pen', 'image': '🖊️', 'meaning': 'Writing tool', 'decodable': true},
    {'word': 'pet', 'image': '🐶', 'meaning': 'Animal friend', 'decodable': true},
    {'word': 'set', 'image': '⚙️', 'meaning': 'Put in place', 'decodable': true},
    {'word': 'sad', 'image': '😢', 'meaning': 'Not happy', 'decodable': false},
    {'word': 'mad', 'image': '😡', 'meaning': 'Very angry', 'decodable': false},
    {'word': 'bad', 'image': '👎', 'meaning': 'Not good', 'decodable': false},
    {'word': 'dad', 'image': '👨', 'meaning': 'Father', 'decodable': false},
    {'word': 'pad', 'image': '📝', 'meaning': 'Paper block', 'decodable': true},
    {'word': 'had', 'image': '🤲', 'meaning': 'Owned', 'decodable': false},
    {'word': 'sag', 'image': '📉', 'meaning': 'Droop down', 'decodable': false},
    {'word': 'tag', 'image': '🏷️', 'meaning': 'Label', 'decodable': false},
    {'word': 'wag', 'image': '🐕', 'meaning': 'Tail move', 'decodable': false},
    {'word': 'bag', 'image': '🛍️', 'meaning': 'Carrying case', 'decodable': false},
    {'word': 'gag', 'image': '🤢', 'meaning': 'Choke', 'decodable': false},
    {'word': 'nag', 'image': '💬', 'meaning': 'Complain', 'decodable': false},
    {'word': 'gap', 'image': '↔️', 'meaning': 'Space', 'decodable': false},
    {'word': 'lap', 'image': '🦵', 'meaning': 'Leg top', 'decodable': true},
    {'word': 'map', 'image': '🗺️', 'meaning': 'Shows places', 'decodable': true},
    {'word': 'nap', 'image': '💤', 'meaning': 'Short sleep', 'decodable': true},
    {'word': 'rap', 'image': '🎤', 'meaning': 'Music talk', 'decodable': false},
    {'word': 'sap', 'image': '🌿', 'meaning': 'Tree juice', 'decodable': true},
    {'word': 'tap', 'image': '👆', 'meaning': 'Light hit', 'decodable': true},
    {'word': 'cap', 'image': '🧢', 'meaning': 'Hat', 'decodable': false},
    {'word': 'lap dog', 'image': '🐕', 'meaning': 'Small pet', 'decodable': false},
  ];

  // =====================================================
  // PHASE 2 CVC WORDS (adds: C K E H R M D)
  // =====================================================
  static const List<Map<String, dynamic>> phase2CVCWords = [
    {'word': 'cat', 'image': '🐱', 'meaning': 'Pet animal', 'decodable': true},
    {'word': 'cap', 'image': '🧢', 'meaning': 'Hat', 'decodable': true},
    {'word': 'cup', 'image': '☕', 'meaning': 'Drinking container', 'decodable': true},
    {'word': 'cut', 'image': '✂️', 'meaning': 'Slice', 'decodable': true},
    {'word': 'can', 'image': '🥫', 'meaning': 'Metal container', 'decodable': true},
    {'word': 'cot', 'image': '🛏️', 'meaning': 'Baby bed', 'decodable': true},
    {'word': 'cop', 'image': '👮', 'meaning': 'Police officer', 'decodable': true},
    {'word': 'car', 'image': '🚗', 'meaning': 'Vehicle', 'decodable': true},
    {'word': 'cab', 'image': '🚕', 'meaning': 'Taxi', 'decodable': true},
    {'word': 'cad', 'image': '😠', 'meaning': 'Rude man', 'decodable': false},
    {'word': 'kit', 'image': '🧰', 'meaning': 'Tool set', 'decodable': true},
    {'word': 'kid', 'image': '👶', 'meaning': 'Child', 'decodable': true},
    {'word': 'keg', 'image': '🛢️', 'meaning': 'Small barrel', 'decodable': false},
    {'word': 'ken', 'image': '🏠', 'meaning': 'Dog house', 'decodable': false},
    {'word': 'deck', 'image': '🎴', 'meaning': 'Cards', 'decodable': false},
    {'word': 'duck', 'image': '🦆', 'meaning': 'Water bird', 'decodable': true},
    {'word': 'sick', 'image': '🤒', 'meaning': 'Not well', 'decodable': true},
    {'word': 'pick', 'image': '👆', 'meaning': 'Choose', 'decodable': true},
    {'word': 'kick', 'image': '🦵', 'meaning': 'Hit with foot', 'decodable': true},
    {'word': 'lick', 'image': '👅', 'meaning': 'Taste', 'decodable': true},
    {'word': 'sock', 'image': '🧦', 'meaning': 'Foot clothing', 'decodable': true},
    {'word': 'rock', 'image': '🪨', 'meaning': 'Stone', 'decodable': true},
    {'word': 'pack', 'image': '🎒', 'meaning': 'Carry', 'decodable': true},
    {'word': 'tack', 'image': '📌', 'meaning': 'Small nail', 'decodable': true},
    {'word': 'sack', 'image': '🛍️', 'meaning': 'Big bag', 'decodable': true},
    {'word': 'deck', 'image': '🛳️', 'meaning': 'Ship floor', 'decodable': false},
    {'word': 'hen', 'image': '🐔', 'meaning': 'Female chicken', 'decodable': true},
    {'word': 'hat', 'image': '🎩', 'meaning': 'Head wear', 'decodable': true},
    {'word': 'hit', 'image': '👊', 'meaning': 'Strike', 'decodable': true},
    {'word': 'hot', 'image': '🔥', 'meaning': 'Very warm', 'decodable': true},
    {'word': 'hop', 'image': '🦘', 'meaning': 'Jump', 'decodable': true},
    {'word': 'hut', 'image': '⛺', 'meaning': 'Small house', 'decodable': true},
    {'word': 'ham', 'image': '🥓', 'meaning': 'Pork meat', 'decodable': true},
    {'word': 'hem', 'image': '🧵', 'meaning': 'Edge of cloth', 'decodable': false},
    {'word': 'had', 'image': '✋', 'meaning': 'Owned', 'decodable': true},
    {'word': 'hid', 'image': '🙈', 'meaning': 'Concealed', 'decodable': true},
    {'word': 'red', 'image': '🔴', 'meaning': 'Color', 'decodable': true},
    {'word': 'rat', 'image': '🐀', 'meaning': 'Rodent', 'decodable': true},
    {'word': 'rip', 'image': '📄', 'meaning': 'Tear', 'decodable': true},
    {'word': 'rod', 'image': '🎣', 'meaning': 'Fishing pole', 'decodable': false},
    {'word': 'ram', 'image': '🐏', 'meaning': 'Male sheep', 'decodable': false},
    {'word': 'rug', 'image': '🧶', 'meaning': 'Floor cover', 'decodable': false},
    {'word': 'rot', 'image': '🍎', 'meaning': 'Decay', 'decodable': false},
    {'word': 'rid', 'image': '🗑️', 'meaning': 'Remove', 'decodable': true},
    {'word': 'ran', 'image': '🏃', 'meaning': 'Moved fast', 'decodable': true},
    {'word': 'man', 'image': '👨', 'meaning': 'Adult male', 'decodable': true},
    {'word': 'mat', 'image': '🧘', 'meaning': 'Floor cover', 'decodable': true},
    {'word': 'map', 'image': '🗺️', 'meaning': 'Shows places', 'decodable': true},
    {'word': 'mad', 'image': '😠', 'meaning': 'Angry', 'decodable': true},
    {'word': 'mud', 'image': '💩', 'meaning': 'Wet dirt', 'decodable': true},
    {'word': 'mop', 'image': '🧹', 'meaning': 'Cleaning tool', 'decodable': true},
    {'word': 'men', 'image': '👨‍👨‍👦', 'meaning': 'Multiple males', 'decodable': false},
    {'word': 'mom', 'image': '👩', 'meaning': 'Mother', 'decodable': false},
    {'word': 'met', 'image': '🤝', 'meaning': 'Encountered', 'decodable': true},
    {'word': 'dog', 'image': '🐕', 'meaning': 'Pet animal', 'decodable': true},
    {'word': 'dad', 'image': '👨', 'meaning': 'Father', 'decodable': true},
    {'word': 'dip', 'image': '🍿', 'meaning': 'Lower briefly', 'decodable': true},
    {'word': 'dot', 'image': '⭕', 'meaning': 'Small spot', 'decodable': true},
    {'word': 'den', 'image': '🐻', 'meaning': 'Animal home', 'decodable': true},
    {'word': 'dig', 'image': '⛏️', 'meaning': 'Move earth', 'decodable': true},
    {'word': 'dug', 'image': '🕳️', 'meaning': 'Past of dig', 'decodable': true},
    {'word': 'dim', 'image': '💡', 'meaning': 'Not bright', 'decodable': true},
    {'word': 'dab', 'image': '💦', 'meaning': 'Pat lightly', 'decodable': false},
    {'word': 'egg', 'image': '🥚', 'meaning': 'Breakfast food', 'decodable': true},
    {'word': 'end', 'image': '🏁', 'meaning': 'Finish', 'decodable': true},
    {'word': 'eat', 'image': '🍽️', 'meaning': 'Consume food', 'decodable': false},
    {'word': 'ear', 'image': '👂', 'meaning': 'Hearing organ', 'decodable': true},
    {'word': 'elk', 'image': '🦌', 'meaning': 'Large deer', 'decodable': false},
    {'word': 'elf', 'image': '🧝', 'meaning': 'Small magical being', 'decodable': false},
    {'word': 'hem', 'image': '👗', 'meaning': 'Cloth edge', 'decodable': false},
    {'word': 'hen', 'image': '🐔', 'meaning': 'Chicken', 'decodable': true},
    {'word': 'her', 'image': '👩', 'meaning': 'Belonging to girl', 'decodable': true},
    {'word': 'bed', 'image': '🛏️', 'meaning': 'Sleep furniture', 'decodable': true},
    {'word': 'fed', 'image': '🍽️', 'meaning': 'Gave food', 'decodable': true},
    {'word': 'led', 'image': '🎯', 'meaning': 'Guided', 'decodable': true},
    {'word': 'led', 'image': '💡', 'meaning': 'Shone', 'decodable': true},
    {'word': 'wed', 'image': '💍', 'meaning': 'Married', 'decodable': true},
    {'word': 'wed', 'image': '🔒', 'meaning': 'Stuck', 'decodable': true},
    {'word': 'pen', 'image': '✒️', 'meaning': 'Writing tool', 'decodable': true},
    {'word': 'hen', 'image': '🐓', 'meaning': 'Chicken', 'decodable': true},
    {'word': 'men', 'image': '👨‍👨‍👦', 'meaning': 'Adult males', 'decodable': false},
    {'word': 'ten', 'image': '🔟', 'meaning': 'Number 10', 'decodable': true},
    {'word': 'den', 'image': '🏠', 'meaning': 'Home', 'decodable': true},
    {'word': 'get', 'image': '🎁', 'meaning': 'Receive', 'decodable': true},
    {'word': 'let', 'image': '✅', 'meaning': 'Allow', 'decodable': true},
    {'word': 'met', 'image': '🤝', 'meaning': 'Saw someone', 'decodable': true},
    {'word': 'net', 'image': '🕸️', 'meaning': 'Mesh trap', 'decodable': true},
    {'word': 'pet', 'image': '🐶', 'meaning': 'Animal friend', 'decodable': true},
    {'word': 'set', 'image': '🎯', 'meaning': 'Put', 'decodable': true},
    {'word': 'vet', 'image': '👨‍⚕️', 'meaning': 'Animal doctor', 'decodable': true},
    {'word': 'wet', 'image': '💧', 'meaning': 'Not dry', 'decodable': true},
    {'word': 'yet', 'image': '⏰', 'meaning': 'Still', 'decodable': false},
    {'word': 'red', 'image': '🟥', 'meaning': 'Color', 'decodable': true},
    {'word': 'web', 'image': '🕸️', 'meaning': 'Spider home', 'decodable': true},
  ];

  // =====================================================
  // PHASE 3 CVC WORDS (adds: G O U L F B)
  // =====================================================
  static const List<Map<String, dynamic>> phase3CVCWords = [
    {'word': 'got', 'image': '🎁', 'meaning': 'Received', 'decodable': true},
    {'word': 'gut', 'image': '🫀', 'meaning': 'Intestine', 'decodable': true},
    {'word': 'gap', 'image': '↔️', 'meaning': 'Space', 'decodable': true},
    {'word': 'gas', 'image': '⛽', 'meaning': 'Fuel', 'decodable': true},
    {'word': 'gum', 'image': '🍬', 'meaning': 'Chewy candy', 'decodable': true},
    {'word': 'gun', 'image': '🔫', 'meaning': 'Weapon', 'decodable': true},
    {'word': 'gig', 'image': '🎸', 'meaning': 'Music job', 'decodable': true},
    {'word': 'gag', 'image': '🤢', 'meaning': 'Choke', 'decodable': true},
    {'word': 'beg', 'image': '🙏', 'meaning': 'Ask urgently', 'decodable': true},
    {'word': 'bag', 'image': '🛍️', 'meaning': 'Container', 'decodable': true},
    {'word': 'big', 'image': '🐘', 'meaning': 'Large', 'decodable': true},
    {'word': 'bug', 'image': '🐛', 'meaning': 'Small insect', 'decodable': true},
    {'word': 'bog', 'image': '🏞️', 'meaning': 'Swamp', 'decodable': true},
    {'word': 'bat', 'image': '🦇', 'meaning': 'Flying mammal', 'decodable': true},
    {'word': 'bet', 'image': '💰', 'meaning': 'Wager', 'decodable': true},
    {'word': 'bit', 'image': '🤏', 'meaning': 'Small piece', 'decodable': true},
    {'word': 'but', 'image': '⚖️', 'meaning': 'Except', 'decodable': true},
    {'word': 'bot', 'image': '🤖', 'meaning': 'Robot', 'decodable': false},
    {'word': 'tub', 'image': '🛁', 'meaning': 'Bath container', 'decodable': true},
    {'word': 'cub', 'image': '🦁', 'meaning': 'Baby animal', 'decodable': true},
    {'word': 'rub', 'image': '👐', 'meaning': 'Move friction', 'decodable': true},
    {'word': 'sub', 'image': '🥪', 'meaning': 'Sandwich', 'decodable': false},
    {'word': 'pub', 'image': '🍺', 'meaning': 'Bar', 'decodable': false},
    {'word': 'hub', 'image': '⚙️', 'meaning': 'Center', 'decodable': false},
    {'word': 'hug', 'image': '🤗', 'meaning': 'Embrace', 'decodable': true},
    {'word': 'jug', 'image': '🏺', 'meaning': 'Container', 'decodable': true},
    {'word': 'mug', 'image': '☕', 'meaning': 'Cup', 'decodable': true},
    {'word': 'rug', 'image': '🧶', 'meaning': 'Floor cover', 'decodable': true},
    {'word': 'tug', 'image': '🚢', 'meaning': 'Pull boat', 'decodable': true},
    {'word': 'pug', 'image': '🐕', 'meaning': 'Dog breed', 'decodable': true},
    {'word': 'cub', 'image': '🐻', 'meaning': 'Bear baby', 'decodable': true},
    {'word': 'fib', 'image': '🤥', 'meaning': 'Small lie', 'decodable': false},
    {'word': 'mob', 'image': '👥', 'meaning': 'Crowd', 'decodable': true},
    {'word': 'sob', 'image': '😭', 'meaning': 'Cry', 'decodable': true},
    {'word': 'job', 'image': '💼', 'meaning': 'Work', 'decodable': false},
    {'word': 'rob', 'image': '🦹', 'meaning': 'Steal', 'decodable': true},
    {'word': 'lob', 'image': '🎾', 'meaning': 'Hit high', 'decodable': false},
    {'word': 'dog', 'image': '🐶', 'meaning': 'Pet', 'decodable': true},
    {'word': 'fog', 'image': '🌫️', 'meaning': 'Thick mist', 'decodable': true},
    {'word': 'log', 'image': '🪵', 'meaning': 'Wood piece', 'decodable': true},
    {'word': 'bog', 'image': '🏞️', 'meaning': 'Wetland', 'decodable': true},
    {'word': 'cog', 'image': '⚙️', 'meaning': 'Gear tooth', 'decodable': true},
    {'word': 'hog', 'image': '🐷', 'meaning': 'Pig', 'decodable': true},
    {'word': 'jog', 'image': '🏃', 'meaning': 'Run slow', 'decodable': true},
    {'word': 'leg', 'image': '🦵', 'meaning': 'Body part', 'decodable': true},
    {'word': 'log', 'image': '📓', 'meaning': 'Record', 'decodable': true},
    {'word': 'mug', 'image': '🥤', 'meaning': 'Big cup', 'decodable': true},
    {'word': 'hug', 'image': '🤗', 'meaning': 'Cuddle', 'decodable': true},
    {'word': 'jug', 'image': '🏺', 'meaning': 'Pitcher', 'decodable': true},
    {'word': 'rug', 'image': '🧸', 'meaning': 'Carpet', 'decodable': true},
    {'word': 'tug', 'image': '🚤', 'meaning': 'Pull', 'decodable': true},
    {'word': 'mug', 'image': '😠', 'meaning': 'Funny face', 'decodable': true},
    {'word': 'pug', 'image': '🐕', 'meaning': 'Dog type', 'decodable': true},
    {'word': 'bug', 'image': '🐞', 'meaning': 'Insect', 'decodable': true},
    {'word': 'dug', 'image': '🕳️', 'meaning': 'Past tense dig', 'decodable': true},
    {'word': 'lug', 'image': '🧳', 'meaning': 'Carry heavy', 'decodable': true},
    {'word': 'fig', 'image': '🍇', 'meaning': 'Fruit', 'decodable': true},
    {'word': 'gig', 'image': '🎤', 'meaning': 'Performance', 'decodable': true},
    {'word': 'jig', 'image': '💃', 'meaning': 'Dance', 'decodable': false},
    {'word': 'pig', 'image': '🐷', 'meaning': 'Farm animal', 'decodable': true},
    {'word': 'rig', 'image': '🏗️', 'meaning': 'Equipment', 'decodable': false},
    {'word': 'wig', 'image': '👩‍🦲', 'meaning': 'Hair piece', 'decodable': true},
    {'word': 'big', 'image': '🐋', 'meaning': 'Large', 'decodable': true},
    {'word': 'dig', 'image': '⛏️', 'meaning': 'Excavate', 'decodable': true},
    {'word': 'fig', 'image': '🌳', 'meaning': 'Mediterranean fruit', 'decodable': true},
    {'word': 'gig', 'image': '🎸', 'meaning': 'Show', 'decodable': true},
    {'word': 'jig', 'image': '🎻', 'meaning': 'Irish dance', 'decodable': false},
    {'word': 'pig', 'image': '🐽', 'meaning': 'Oink animal', 'decodable': true},
    {'word': 'rig', 'image': '🛢️', 'meaning': 'Oil equipment', 'decodable': false},
    {'word': 'wig', 'image': '👱‍♀️', 'meaning': 'False hair', 'decodable': true},
    {'word': 'bun', 'image': '🍞', 'meaning': 'Bread roll', 'decodable': true},
    {'word': 'fun', 'image': '🎉', 'meaning': 'Enjoyment', 'decodable': true},
    {'word': 'gun', 'image': '🔫', 'meaning': 'Weapon', 'decodable': true},
    {'word': 'nun', 'image': '⛪', 'meaning': 'Religious woman', 'decodable': true},
    {'word': 'pun', 'image': '😄', 'meaning': 'Word joke', 'decodable': false},
    {'word': 'run', 'image': '🏃', 'meaning': 'Move fast', 'decodable': true},
    {'word': 'sun', 'image': '☀️', 'meaning': 'Day star', 'decodable': true},
    {'word': 'cut', 'image': '✂️', 'meaning': 'Slice', 'decodable': true},
    {'word': 'gut', 'image': '🫁', 'meaning': 'Belly', 'decodable': true},
    {'word': 'hut', 'image': '🛖', 'meaning': 'Small house', 'decodable': true},
    {'word': 'jut', 'image': '📐', 'meaning': 'Stick out', 'decodable': false},
    {'word': 'nut', 'image': '🥜', 'meaning': 'Tree seed', 'decodable': true},
    {'word': 'put', 'image': '📦', 'meaning': 'Place', 'decodable': true},
    {'word': 'rut', 'image': '🔄', 'meaning': 'Groove', 'decodable': false},
    {'word': 'cuff', 'image': '👔', 'meaning': 'Wrist band', 'decodable': false},
    {'word': 'huff', 'image': '😤', 'meaning': 'Puff angrily', 'decodable': true},
    {'word': 'puff', 'image': '💨', 'meaning': 'Short blow', 'decodable': true},
    {'word': 'buff', 'image': '💪', 'meaning': 'Polish', 'decodable': false},
    {'word': 'bluff', 'image': '🃏', 'meaning': 'Pretend', 'decodable': false},
    {'word': 'fluff', 'image': '☁️', 'meaning': 'Soft stuff', 'decodable': true},
    {'word': 'gruff', 'image': '😠', 'meaning': 'Rough voice', 'decodable': false},
    {'word': 'muff', 'image': '🧤', 'meaning': 'Hand warmer', 'decodable': false},
    {'word': 'stuff', 'image': '📦', 'meaning': 'Things', 'decodable': false},
    {'word': 'tuff', 'image': '🪨', 'meaning': 'Rock type', 'decodable': false},
    {'word': 'tofu', 'image': '🧊', 'meaning': 'Soy food', 'decodable': false},
  ];

  // =====================================================
  // PHASE 4 CVC WORDS (adds: J Z W X Y Qu V)
  // =====================================================
  static const List<Map<String, dynamic>> phase4CVCWords = [
    {'word': 'jam', 'image': '🍓', 'meaning': 'Fruit spread', 'decodable': true},
    {'word': 'jet', 'image': '✈️', 'meaning': 'Fast plane', 'decodable': true},
    {'word': 'job', 'image': '💼', 'meaning': 'Work', 'decodable': false},
    {'word': 'jog', 'image': '🏃', 'meaning': 'Slow run', 'decodable': true},
    {'word': 'jug', 'image': '🏺', 'meaning': 'Container', 'decodable': true},
    {'word': 'jump', 'image': '⬆️', 'meaning': 'Leap', 'decodable': false},
    {'word': 'just', 'image': '⚖️', 'meaning': 'Fair', 'decodable': false},
    {'word': 'zip', 'image': '⚡', 'meaning': 'Fast', 'decodable': true},
    {'word': 'zap', 'image': '⚡', 'meaning': 'Quick hit', 'decodable': true},
    {'word': 'zoo', 'image': '🦁', 'meaning': 'Animal park', 'decodable': true},
    {'word': 'buzz', 'image': '🐝', 'meaning': 'Fly sound', 'decodable': false},
    {'word': 'fizz', 'image': '🥤', 'meaning': 'Bubble sound', 'decodable': false},
    {'word': 'jazz', 'image': '🎷', 'meaning': 'Music style', 'decodable': false},
    {'word': 'fizz', 'image': '🍾', 'meaning': 'Effervescent', 'decodable': false},
    {'word': 'whiz', 'image': '🚀', 'meaning': 'Fast person', 'decodable': false},
    {'word': 'wet', 'image': '💧', 'meaning': 'Not dry', 'decodable': true},
    {'word': 'win', 'image': '🏆', 'meaning': 'Victory', 'decodable': true},
    {'word': 'web', 'image': '🕸️', 'meaning': 'Silk thread', 'decodable': true},
    {'word': 'wag', 'image': '🐕', 'meaning': 'Tail move', 'decodable': true},
    {'word': 'wig', 'image': '👩‍🦱', 'meaning': 'Hair piece', 'decodable': true},
    {'word': 'wax', 'image': '🕯️', 'meaning': 'Candle material', 'decodable': true},
    {'word': 'won', 'image': '🎖️', 'meaning': 'Past tense win', 'decodable': true},
    {'word': 'few', 'image': '🔢', 'meaning': 'Small number', 'decodable': true},
    {'word': 'new', 'image': '✨', 'meaning': 'Not old', 'decodable': true},
    {'word': 'dew', 'image': '💧', 'meaning': 'Morning water', 'decodable': true},
    {'word': 'saw', 'image': '🔨', 'meaning': 'Cutting tool', 'decodable': false},
    {'word': 'raw', 'image': '🥩', 'meaning': 'Not cooked', 'decodable': true},
    {'word': 'jaw', 'image': '😬', 'meaning': 'Mouth bone', 'decodable': true},
    {'word': 'law', 'image': '⚖️', 'meaning': 'Rule', 'decodable': true},
    {'word': 'paw', 'image': '🐾', 'meaning': 'Animal foot', 'decodable': true},
    {'word': 'box', 'image': '📦', 'meaning': 'Container', 'decodable': true},
    {'word': 'fox', 'image': '🦊', 'meaning': 'Cunning animal', 'decodable': true},
    {'word': 'six', 'image': '6️⃣', 'meaning': 'Number', 'decodable': true},
    {'word': 'mix', 'image': '🥣', 'meaning': 'Combine', 'decodable': true},
    {'word': 'fix', 'image': '🔧', 'meaning': 'Repair', 'decodable': true},
    {'word': 'wax', 'image': '🕯️', 'meaning': 'Beeswax', 'decodable': true},
    {'word': 'tax', 'image': '💸', 'meaning': 'Payment', 'decodable': false},
    {'word': 'yes', 'image': '✅', 'meaning': 'Agreement', 'decodable': true},
    {'word': 'yak', 'image': '🦬', 'meaning': 'Mountain animal', 'decodable': true},
    {'word': 'yap', 'image': '🐕', 'meaning': 'Bark', 'decodable': true},
    {'word': 'yum', 'image': '😋', 'meaning': 'Tasty', 'decodable': true},
    {'word': 'yet', 'image': '⏰', 'meaning': 'Still', 'decodable': false},
    {'word': 'you', 'image': '👆', 'meaning': 'Person', 'decodable': false},
    {'word': 'yell', 'image': '📢', 'meaning': 'Shout', 'decodable': false},
    {'word': 'quest', 'image': '🗺️', 'meaning': 'Journey', 'decodable': false},
    {'word': 'queen', 'image': '👸', 'meaning': 'Royal woman', 'decodable': true},
    {'word': 'quick', 'image': '⚡', 'meaning': 'Fast', 'decodable': false},
    {'word': 'quit', 'image': '✋', 'meaning': 'Stop', 'decodable': true},
    {'word': 'quiz', 'image': '🧠', 'meaning': 'Test', 'decodable': true},
    {'word': 'quack', 'image': '🦆', 'meaning': 'Duck sound', 'decodable': false},
    {'word': 'quilt', 'image': '🛏️', 'meaning': 'Blanket', 'decodable': false},
    {'word': 'van', 'image': '🚐', 'meaning': 'Vehicle', 'decodable': true},
    {'word': 'vet', 'image': '👨‍⚕️', 'meaning': 'Animal doctor', 'decodable': true},
    {'word': 'vase', 'image': '🏺', 'meaning': 'Flower holder', 'decodable': true},
    {'word': 'vest', 'image': '👔', 'meaning': 'Clothing', 'decodable': false},
    {'word': 'very', 'image': '✨', 'meaning': 'Extremely', 'decodable': false},
    {'word': 'vote', 'image': '🗳️', 'meaning': 'Choose', 'decodable': false},
    {'word': 'vivid', 'image': '🌈', 'meaning': 'Bright', 'decodable': false},
  ];

  // =====================================================
  // PHASE 5 WORDS (Long Vowels + Digraphs)
  // =====================================================
  static const List<Map<String, dynamic>> phase5Words = [
    {'word': 'rain', 'image': '🌧️', 'meaning': 'Water from sky', 'decodable': true},
    {'word': 'train', 'image': '🚂', 'meaning': 'Rail vehicle', 'decodable': true},
    {'word': 'pain', 'image': '🤕', 'meaning': 'Hurt', 'decodable': true},
    {'word': 'main', 'image': '🔑', 'meaning': 'Primary', 'decodable': true},
    {'word': 'chain', 'image': '⛓️', 'meaning': 'Linked metal', 'decodable': true},
    {'word': 'brain', 'image': '🧠', 'meaning': 'Mind organ', 'decodable': true},
    {'word': 'stain', 'image': '☕', 'meaning': 'Mark', 'decodable': true},
    {'word': 'Spain', 'image': '🇪🇸', 'meaning': 'Country', 'decodable': false},
    {'word': 'tree', 'image': '🌳', 'meaning': 'Plant', 'decodable': true},
    {'word': 'bee', 'image': '🐝', 'meaning': 'Insect', 'decodable': true},
    {'word': 'see', 'image': '👁️', 'meaning': 'Look', 'decodable': true},
    {'word': 'sea', 'image': '🌊', 'meaning': 'Ocean', 'decodable': true},
    {'word': 'key', 'image': '🔑', 'meaning': 'Unlock tool', 'decodable': true},
    {'word': 'knee', 'image': '🦵', 'meaning': 'Leg joint', 'decodable': true},
    {'word': 'green', 'image': '💚', 'meaning': 'Color', 'decodable': true},
    {'word': 'speed', 'image': '🏎️', 'meaning': 'Go fast', 'decodable': true},
    {'word': 'sleep', 'image': '😴', 'meaning': 'Rest', 'decodable': true},
    {'word': 'cheese', 'image': '🧀', 'meaning': 'Dairy food', 'decodable': true},
    {'word': 'night', 'image': '🌙', 'meaning': 'Evening', 'decodable': true},
    {'word': 'light', 'image': '💡', 'meaning': 'Illumination', 'decodable': true},
    {'word': 'fight', 'image': '🥊', 'meaning': 'Battle', 'decodable': true},
    {'word': 'right', 'image': '✅', 'meaning': 'Correct', 'decodable': true},
    {'word': 'might', 'image': '💪', 'meaning': 'Possible', 'decodable': false},
    {'word': 'sigh', 'image': '😮‍💨', 'meaning': 'Deep breath', 'decodable': true},
    {'word': 'high', 'image': '⬆️', 'meaning': 'Tall', 'decodable': true},
    {'word': 'thigh', 'image': '🦵', 'meaning': 'Leg part', 'decodable': true},
    {'word': 'flight', 'image': '✈️', 'meaning': 'Air travel', 'decodable': true},
    {'word': 'knight', 'image': '🏰', 'meaning': 'Arthurian hero', 'decodable': false},
    {'word': 'boat', 'image': '⛵', 'meaning': 'Water craft', 'decodable': true},
    {'word': 'coat', 'image': '🧥', 'meaning': 'Outer wear', 'decodable': true},
    {'word': 'goat', 'image': '🐐', 'meaning': 'Farm animal', 'decodable': true},
    {'word': 'road', 'image': '🛣️', 'meaning': 'Path', 'decodable': true},
    {'word': 'soap', 'image': '🧼', 'meaning': 'Cleaner', 'decodable': true},
    {'word': 'toad', 'image': '🐸', 'meaning': 'Amphibian', 'decodable': true},
    {'word': 'load', 'image': '📦', 'meaning': 'Carry', 'decodable': true},
    {'word': 'float', 'image': '🛟', 'meaning': 'Stay on surface', 'decodable': true},
    {'word': 'moon', 'image': '🌙', 'meaning': 'Night satellite', 'decodable': true},
    {'word': 'soon', 'image': '⏰', 'meaning': 'Shortly', 'decodable': true},
    {'word': 'food', 'image': '🍽️', 'meaning': 'Eatables', 'decodable': true},
    {'word': 'cool', 'image': '😎', 'meaning': 'Great', 'decodable': true},
    {'word': 'tool', 'image': '🔧', 'meaning': 'Equipment', 'decodable': true},
    {'word': 'school', 'image': '🏫', 'meaning': 'Place to learn', 'decodable': true},
    {'word': 'spoon', 'image': '🥄', 'meaning': 'Eating utensil', 'decodable': true},
    {'word': 'shoe', 'image': '👟', 'meaning': 'Footwear', 'decodable': true},
    {'word': 'ship', 'image': '🚢', 'meaning': 'Boat', 'decodable': true},
    {'word': 'shop', 'image': '🏪', 'meaning': 'Store', 'decodable': true},
    {'word': 'fish', 'image': '🐟', 'meaning': 'Swim creature', 'decodable': true},
    {'word': 'dish', 'image': '🍽️', 'meaning': 'Plate', 'decodable': true},
    {'word': 'wash', 'image': '🧼', 'meaning': 'Clean', 'decodable': true},
    {'word': 'shut', 'image': '🚪', 'meaning': 'Close', 'decodable': true},
    {'word': 'cash', 'image': '💵', 'meaning': 'Money', 'decodable': true},
    {'word': 'trash', 'image': '🗑️', 'meaning': 'Garbage', 'decodable': true},
    {'word': 'splash', 'image': '💦', 'meaning': 'Spray water', 'decodable': true},
    {'word': 'chip', 'image': '🍟', 'meaning': 'Potato snack', 'decodable': true},
    {'word': 'chop', 'image': '🥩', 'meaning': 'Cut', 'decodable': true},
    {'word': 'chin', 'image': '👴', 'meaning': 'Face part', 'decodable': true},
    {'word': 'chat', 'image': '💬', 'meaning': 'Talk', 'decodable': true},
    {'word': 'rich', 'image': '💰', 'meaning': 'Wealthy', 'decodable': true},
    {'word': 'much', 'image': '➕', 'meaning': 'A lot', 'decodable': true},
    {'word': 'such', 'image': '📌', 'meaning': 'Like', 'decodable': true},
    {'word': 'lunch', 'image': '🥪', 'meaning': 'Midday meal', 'decodable': true},
    {'word': 'bench', 'image': '🪑', 'meaning': 'Long seat', 'decodable': true},
    {'word': 'thin', 'image': '📏', 'meaning': 'Not fat', 'decodable': true},
    {'word': 'thick', 'image': '📚', 'meaning': 'Not thin', 'decodable': true},
    {'word': 'this', 'image': '👆', 'meaning': 'Current', 'decodable': true},
    {'word': 'that', 'image': '👉', 'meaning': 'Over there', 'decodable': true},
    {'word': 'then', 'image': '⏭️', 'meaning': 'Next', 'decodable': true},
    {'word': 'them', 'image': '👥', 'meaning': 'Those people', 'decodable': true},
    {'word': 'bath', 'image': '🛁', 'meaning': 'Wash', 'decodable': true},
    {'word': 'path', 'image': '🛤️', 'meaning': 'Walkway', 'decodable': true},
    {'word': 'moth', 'image': '🦋', 'meaning': 'Night butterfly', 'decodable': true},
    {'word': 'sing', 'image': '🎤', 'meaning': 'Make music', 'decodable': true},
    {'word': 'song', 'image': '🎵', 'meaning': 'Tune', 'decodable': true},
    {'word': 'ring', 'image': '💍', 'meaning': 'Jewelry', 'decodable': true},
    {'word': 'wing', 'image': '🦅', 'meaning': 'Flight part', 'decodable': true},
    {'word': 'king', 'image': '👑', 'meaning': 'Royal man', 'decodable': true},
    {'word': 'long', 'image': '📏', 'meaning': 'Not short', 'decodable': true},
    {'word': 'bring', 'image': '🎁', 'meaning': 'Carry here', 'decodable': true},
    {'word': 'spring', 'image': '🌸', 'meaning': 'Season', 'decodable': true},
    {'word': 'string', 'image': '🧵', 'meaning': 'Thread', 'decodable': true},
    {'word': 'thing', 'image': '🎁', 'meaning': 'Object', 'decodable': true},
    {'word': 'think', 'image': '🤔', 'meaning': 'Consider', 'decodable': true},
    {'word': 'thank', 'image': '🙏', 'meaning': 'Gratitude', 'decodable': true},
    {'word': 'sink', 'image': '🚰', 'meaning': 'Go down', 'decodable': true},
    {'word': 'pink', 'image': '🌸', 'meaning': 'Color', 'decodable': true},
    {'word': 'wink', 'image': '😉', 'meaning': 'Eye gesture', 'decodable': true},
    {'word': 'link', 'image': '🔗', 'meaning': 'Connection', 'decodable': true},
  ];

  // =====================================================
  // ALL CVC WORDS COMBINED (by phase)
  // =====================================================
  static List<Map<String, dynamic>> getCVCWordsForPhase(int phase) {
    switch (phase) {
      case 1:
        return phase1CVCWords;
      case 2:
        return [...phase1CVCWords, ...phase2CVCWords];
      case 3:
        return [...phase1CVCWords, ...phase2CVCWords, ...phase3CVCWords];
      case 4:
        return [...phase1CVCWords, ...phase2CVCWords, ...phase3CVCWords, ...phase4CVCWords];
      case 5:
        return [
          ...phase1CVCWords, ...phase2CVCWords, 
          ...phase3CVCWords, ...phase4CVCWords,
          ...phase5Words
        ];
      default:
        return [
          ...phase1CVCWords, ...phase2CVCWords, 
          ...phase3CVCWords, ...phase4CVCWords,
          ...phase5Words
        ];
    }
  }

  static int getTotalWordsForPhase(int phase) {
    return getCVCWordsForPhase(phase).length;
  }

  // Statistics
  static int get phase1WordCount => phase1CVCWords.length;
  static int get phase2WordCount => phase2CVCWords.length;
  static int get phase3WordCount => phase3CVCWords.length;
  static int get phase4WordCount => phase4CVCWords.length;
  static int get phase5WordCount => phase5Words.length;
  
  static int get totalCVCWords => 
    phase1WordCount + phase2WordCount + phase3WordCount + 
    phase4WordCount + phase5WordCount;

  // =====================================================
  // Regional Accent Differences
  // =====================================================
  static const Map<String, Map<String, String>> regionalDifferences = {
    's': {
      'au': 'sss (softer, dental)',
      'nz': 'sss (similar to AU)',
      'us': 'sss (more sibilant)',
    },
    'r': {
      'au': 'R is silent when not followed by vowel',
      'nz': 'R is silent when not followed by vowel',
      'us': 'Full R sound always pronounced',
    },
    'a': {
      'au': 'a as in "cat"',
      'nz': 'a as in "cat" (slightly more nasal)',
      'us': 'a as in "cat"',
    },
    'i': {
      'au': 'i as in "pin"',
      'nz': 'i as in "pin" (slightly clipped)',
      'us': 'i as in "pin"',
    },
    't': {
      'au': 't as in "top" (flapped T)',
      'nz': 't as in "top"',
      'us': 't as in "top" (harder T)',
    },
    'd': {
      'au': 'd as in "dog" (softer)',
      'nz': 'd as in "dog"',
      'us': 'd as in "dog" (harder)',
    },
  };

  // =====================================================
  // Word Builder Helper Methods
  // =====================================================
  
  /// Get words that can be built with specific letters
  static List<Map<String, dynamic>> getWordsWithLetters(List<String> letters) {
    final allWords = [...phase1CVCWords, ...phase2CVCWords, ...phase3CVCWords, 
                      ...phase4CVCWords, ...phase5Words];
    
    return allWords.where((wordData) {
      final word = wordData['word'] as String;
      // Check if word can be made with given letters
      final wordLetters = word.toLowerCase().split('');
      final availableLetters = letters.map((l) => l.toLowerCase()).toList();
      
      for (final letter in wordLetters) {
        if (!availableLetters.contains(letter)) {
          return false;
        }
        availableLetters.remove(letter);
      }
      return true;
    }).toList();
  }

  /// Get random decodable CVC words for practice
  static List<Map<String, dynamic>> getRandomCVCWords(int count, {int? phase}) {
    final words = phase != null ? getCVCWordsForPhase(phase) : getCVCWordsForPhase(5);
    final decodable = words.where((w) => w['decodable'] == true).toList();
    decodable.shuffle();
    return decodable.take(count).toList();
  }

  /// Get words for word builder game (3-letter CVC only)
  static List<Map<String, dynamic>> getWordBuilderWords(int phase) {
    final words = getCVCWordsForPhase(phase);
    return words.where((w) {
      final word = w['word'] as String;
      return word.length == 3 && w['decodable'] == true;
    }).toList();
  }
}
