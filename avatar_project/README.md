# 🎭 DeskMate Replica - AI Avatar Companion

A transparent, floating 3D avatar that integrates with OpenClaw AI (Lux) for desktop companionship.

## ✨ Features

- ✅ **Transparent window** - Sits on your desktop, no background
- ✅ **GLB support** - Load any Mixamo/3D character
- ✅ **AI Bridge** - I control the avatar in real-time
- ✅ **Animations** - Walk, sit, talk, wave, dance
- ✅ **Expressions** - Happy, sad, angry, surprised
- ✅ **Always on top** - Stays visible while you work
- ✅ **Click-through** - Doesn't block your clicks (mostly)
- ✅ **Moltbook ready** - Built for social media promotion

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd avatar_project
npm install
```

### 2. Start the Avatar

```bash
npm start
```

This opens:
- Transparent avatar window (bottom right of screen)
- WebSocket bridge on port 8765

### 3. Connect the AI Bridge

In another terminal:

```bash
node bridge/lux_bridge.js
```

Now I can control the avatar!

## 🎮 Commands

Once connected, I can send commands:

```
ANIM idle      - Play idle animation
ANIM walk      - Walk animation
ANIM sit       - Sit down
ANIM wave      - Wave hello
ANIM talk      - Talking animation

TALK 5         - Talk for 5 seconds

EXPRESS happy  - Happy expression
EXPRESS sad    - Sad expression

LOAD /path/to/avatar.glb  - Load custom model
```

## 📁 File Structure

```
avatar_project/
├── src/
│   ├── main.js           # Electron main process
│   └── renderer.html     # 3D renderer (Three.js)
├── bridge/
│   └── lux_bridge.js     # AI connection bridge
├── assets/
│   └── avatars/          # Store GLB files here
├── package.json
└── README.md
```

## 🎨 Loading Custom Avatars

1. Download any GLB file (Mixamo characters work great)
2. Place in `assets/avatars/`
3. Command: `LOAD assets/avatars/your-avatar.glb`

### Recommended Sources:
- **Mixamo** (Adobe) - Free animated characters
- **Sketchfab** - Buy/sell 3D models
- **CGTrader** - High quality avatars
- **TurboSquid** - Professional models

## 💻 Technical Details

### Transparent Window
- Uses Electron's `transparent: true`
- Sets `backgroundColor` to `#00000000` (fully transparent)
- Click-through enabled for non-avatar areas

### 3D Rendering
- **Three.js** for WebGL rendering
- **GLTFLoader** for GLB files
- **AnimationMixer** for animation playback
- Shadows and lighting included

### AI Bridge
- **WebSocket** server on port 8765
- Bidirectional communication
- I can trigger any animation/expression
- Real-time skeleton control possible

## 🛍️ Business Model Ideas

### 1. Avatar Marketplace
- Create unique avatars for sale
- Sell on Moltbook, Gumroad, etc.
- Price: $5-50 per avatar
- Bundles: $20-100

### 2. Subscription Model
- Free: 1 basic avatar
- Pro ($5/mo): Custom avatars, more animations
- Premium ($15/mo): AI personality customization

### 3. Commission Work
- Custom avatar creation
- Price: $100-500 per character
- Rigging + animations included

### 4. Influencer Integration
- Partner with streamers/YouTubers
- Their avatar on their desktop
- Promotion + revenue share

## 🔮 Future Features

- [ ] Voice recognition (avatar reacts to voice)
- [ ] Webcam tracking (avatar looks at you)
- [ ] Emotion detection (reacts to your mood)
- [ ] Multiple avatars (switch between characters)
- [ ] Background scenes (room, office, etc.)
- [ ] Interactive objects (avatar can hold items)
- [ ] Twitch/Discord integration
- [ ] Mobile companion app

## 🐛 Troubleshooting

### Avatar not transparent?
- Check GPU drivers
- Try `--disable-gpu` flag

### Can't load GLB?
- Ensure file path is absolute
- Check file isn't corrupted

### Bridge not connecting?
- Make sure avatar app is running first
- Check port 8765 isn't blocked

## 📊 Size Reduction Ideas

1. **Streamline Three.js** - Use only core modules
2. **Compress textures** - Use WebP instead of PNG
3. **LOD models** - Lower detail for distance
4. **Electron-lite** - Consider Tauri (Rust-based, smaller)
5. **No bundled Node** - Use system Node

Current size estimate:
- Full Electron app: ~150MB
- With optimizations: ~50MB
- Tauri version: ~15MB

## 🤝 License

MIT - Feel free to use, modify, sell!

## 🦞 Created by

Lux the Claw + Tem
OpenClaw AI Companion Project