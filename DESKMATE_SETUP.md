# Desktop Mate Bridge Setup

Connects OpenClaw crypto alerts to your Desktop Mate avatar!

## 📁 Files Created

1. `LuxBridge.lua` - Desktop Mate script (goes in Windows)
2. `luxbridge_sender.py` - OpenClaw bridge (WSL2)
3. `C:\Users\HighE\DesktopMateLux\alerts.json` - Bridge file

## 🎮 Desktop Mate Setup (Windows)

### Step 1: Find Desktop Mate Lua Folder

Desktop Mate loads Lua scripts from one of these locations:

Option A: DesktopMate app data
```
C:\Users\HighE\AppData\Roaming\DesktopMate\_USER\Mods\Lua
```

Option B: DesktopMate install folder
```
C:\Program Files (x86)\Steam\steamapps\common\DesktopMate\Mods\Lua
```

Option C: Custom location (check Desktop Mate settings)

### Step 2: Create Lua File

Create file: `LuxBridge.lua` in the Lua folder

```lua
-- Lux Bridge for Desktop Mate
-- Watches C:\Users\HighE\DesktopMateLux\alerts.json

local LuxBridge = {}
local BRIDGE_FILE = "C:\\Users\\HighE\\DesktopMateLux\\alerts.json"
local lastModified = 0

-- Animation mappings
local ANIMATIONS = {
    grade_a = {"happy", "excited", "victory"},
    checkpoint = {"nod", "smile"},
    survivor = {"dance", "celebrate"},
    heartbeat = {"idle", "wave"}
}

function LuxBridge.check()
    local file = io.open(BRIDGE_FILE, "r")
    if not file then return end
    
    local content = file:read("*all")
    file:close()
    
    if content == "" or #content < 10 then return end
    
    -- Parse simple JSON
    local alert = {}
    for k, v in content:gmatch('"([^"]+)":"([^"]+)"') do
        alert[k] = v
    end
    
    if alert.type then
        print("[Lux] Alert: " .. alert.display_text)
        
        -- Trigger animation
        local anims = ANIMATIONS[alert.type] or {"idle"}
        local anim = anims[math.random(#anims)]
        
        -- Replace this with actual Desktop Mate API call
        -- DesktopMate.PlayAnimation(anim)
        -- DesktopMate.ShowFloatingText(alert.display_text, 5.0)
        
        -- Clear the alert
        local f = io.open(BRIDGE_FILE, "w")
        if f then f:write(""); f:close() end
    end
end

-- Call this in Desktop Mate's update loop
function update()
    LuxBridge.check()
end

return LuxBridge
```

### Step 3: Test Integration

1. Load Desktop Mate
2. The script should auto-load from the Lua folder
3. Try the test from WSL:
   ```bash
   cd /home/skux/.openclaw/workspace
   python3 luxbridge_sender.py
   ```
4. Your avatar should react!

## 🚀 Alert Types

Your avatar can react to:

| Alert Type | Animation | Sent To Desktop Mate |
|------------|-----------|---------------------|
| `grade_a` | Happy/excited | When new Grade A token found |
| `checkpoint` | Nod/thumbs up | When token survives 6h/12h/24h |
| `survivor` | Dance/celebrate | 24h+ Grade A survivor |
| `heartbeat` | Wave | Every 30min status ping |

## 🔧 Quick Test

```bash
# From WSL
python3 -c "
from luxbridge_sender import LuxBridge
b = LuxBridge()
b.grade_a_alert({
    'ca': 'test123',
    'name': 'TestCoin',
    'grade': 'A+',
    'mcap': 100000,
    'liq': 50000,
    'holders': 1000
})
"
```

## 💡 Next Steps

1. Figure out Desktop Mate's actual Lua API (check docs)
2. Replace placeholder animation calls with real ones
3. Add floating text display
4. Customize reactions per alert type

## 🔍 Finding Desktop Mate's Script Folder

In Desktop Mate:
1. Go to Settings/Options
2. Look for "Scripts" or "Mods"
3. Check where it loads Lua from

OR check these common paths:
- `%APPDATA%\DesktopMate\_USER\Mods\Lua`
- `%LOCALAPPDATA%\DesktopMate\Lua`
- `Documents\DesktopMate\Scripts`

## 🆘 Troubleshooting

**Alert file exists but avatar doesn't react:**
- Desktop Mate Lua isn't loading the script
- Check the correct Lua folder
- Try reloading Desktop Mate or pressing F5 to reload scripts

**File permissions:**
- Make alerts.json readable by Desktop Mate
- Windows might block cross-app file access

**Animations not playing:**
- Replace `DesktopMate.PlayAnimation` with actual API
- Check Desktop Mate documentation for Lua API
