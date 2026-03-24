# 🎯 Size Reduction Plan

Current estimated size: ~150MB
Target size: ~30-50MB

## Optimization Strategies

### 1. Use Tauri Instead of Electron ⭐ RECOMMENDED
**Size: 15-30MB**
- Rust-based, much smaller runtime
- WebView (uses system browser)
- All features we need
- Better performance

**Migration:**
```bash
# Install Tauri CLI
cargo install tauri-cli

# New Tauri project
cargo tauri init

# Move src/ to Tauri structure
# Keep Three.js renderer
# Reuse bridge code
```

### 2. Node-Integrated Electron
**Size: ~80MB**
- Don't bundle Node.js
- Use system Node.js
- Only pack app code

**In package.json:**
```json
"build": {
  "nodeGypRebuild": false,
  "npmRebuild": false,
  "files": [
    "src/**/*",
    "!node_modules/**/*",
    "../node_modules/ws/**/*",
    "../node_modules/express/**/*"
  ]
}
```

### 3. Lite Version - Web-Based
**Size: HTML file < 1MB**
- Run in browser
- Use nativefier or similar
- User runs bridge separately
- Slightly less integrated

**For quick sharing:**
```html
<!-- Single HTML file -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"></script>
<!-- All code inline -->
```

### 4. Modular Three.js
**Size: ~5MB savings**
- Only import used modules
- Tree-shake unused features
- Custom Three.js build

**Instead of:**
```javascript
import * as THREE from 'three';
```

**Use:**
```javascript
import { Scene, Camera, WebGLRenderer } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
```

### 5. Optimize GLB Files
**Size: Variable**
- Compress textures (WebP)
- Reduce polygon count
- Remove unused animations
- Draco compression

**Tool:** gltf-pipeline
```bash
npm install -g gltf-pipeline
gltf-pipeline -i model.glb -o model-compressed.glb --draco.compressionLevel 10
```

## Recommended: Hybrid Approach

1. **Lite version** (1MB HTML) - For quick demos
2. **Tauri version** (20MB) - Recommended for users
3. **Electron version** (150MB) - For development

## File Breakdown

| Component | Electron | Tauri | Lite |
|-----------|----------|-------|------|
| Runtime | 120MB | 5MB | 0MB |
| Chromium | Included | System | System |
| Node.js | Included | Rust | System |
| App code | 15MB | 15MB | 1MB |
| Dependencies | 10MB | 5MB | 0MB |
| **Total** | **~150MB** | **~25MB** | **1MB** |

## Decision Matrix

| Feature | Electron | Tauri | Lite |
|---------|----------|-------|------|
| Transparent window | ✅ | ✅ | ⚠️ |
| Always on top | ✅ | ✅ | ⚠️ |
| System integration | ✅ | ✅ | ❌ |
| Easy install | ⚠️ | ✅ | ✅ |
| Auto-updates | ✅ | ✅ | ❌ |
| Size | 150MB | 25MB | 1MB |

**Recommendation:** Build Tauri version for distribution!

## Quick Wins (Tonight)

1. ✅ Create HTML-only version for demos
2. ⏳ Research Tauri migration
3. ⏳ Set up build pipeline

**Which path do you want to take?**