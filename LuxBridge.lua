-- Desktop Mate Bridge Script
-- Path: DesktopMate/Lua/LuxBridge.lua

local LuxBridge = {}

-- Configuration - match the Python sender path
local BRIDGE_FILE = "C:\\\\\Users\\\\HighE\\\\DesktopMateLux\\\\alerts.json"
local lastHash = ""
local checkInterval = 1.0  -- Check every second
local timer = 0

-- Alert types and their responses
local ALERT_RESPONSES = {
    grade_a = {
        animation = "happy",
        expression = "excited",
        text = "🚀 Grade A Found!"
    },
    checkpoint = {
        animation = "nod",
        expression = "smile",
        text = "🎯 Checkpoint Passed!"
    },
    survivor = {
        animation = "dance",
        expression = "celebrate",
        text = "🏆 Survivor!"
    },
    heartbeat = {
        animation = "wave",
        expression = "neutral",
        text = "🦞 Online"
    }
}

-- Read file (Windows path)
function LuxBridge.readAlertFile()
    local file = io.open(BRIDGE_FILE, "r")
    if not file then
        return nil, "File not found"
    end
    
    local content = file:read("*all")
    file:close()
    
    if content == "" or #content < 5 then
        return nil, "Empty file"
    end
    
    return content, nil
end

-- Simple JSON parsing (doesn't require external library)
function LuxBridge.parseAlert(content)
    if not content then return nil end
    
    local alert = {}
    -- Extract key-value pairs
    for key, value in content:gmatch('"([^"]+)":"([^"]+)"') do
        alert[key] = value
    end
    for key, value in content:gmatch('"([^"]+)":(%d+)') do
        alert[key] = tonumber(value)
    end
    
    -- Get timestamp (special handling)
    local timestamp = content:match('"timestamp":"([^"]+)"')
    if timestamp then
        alert.timestamp = timestamp
    end
    
    return alert
end

-- Check if this is a new alert
function LuxBridge.isNewAlert(alert)
    if not alert or not alert.timestamp then return false end
    
    local currentHash = tostring(alert.timestamp) .. tostring(alert.type)
    if currentHash == lastHash then
        return false  -- Already processed
    end
    
    lastHash = currentHash
    return true
end

-- Process and react to alert
function LuxBridge.processAlert(alert)
    if not alert or not alert.type then return end
    
    print("[LuxBridge] New alert: " .. (alert.display_text or alert.type))
    
    local response = ALERT_RESPONSES[alert.type]
    if not response then
        response = ALERT_RESPONSES.heartbeat
    end
    
    -- Play animation (placeholder for actual DesktopMate API)
    print("[LuxBridge] Animation: " .. response.animation)
    print("[LuxBridge] Text: " .. (alert.display_text or response.text))
    
    -- TODO: Replace with actual DesktopMate API calls
    -- DesktopMate.PlayAnimation(response.animation)
    -- DesktopMate.SetExpression(response.expression)
    -- DesktopMate.ShowFloatingText(alert.display_text or response.text, 5.0)
    
    -- Clear the alert file
    local file = io.open(BRIDGE_FILE, "w")
    if file then
        file:write("")
        file:close()
        print("[LuxBridge] Alert cleared")
    end
end

-- Main update function (called by DesktopMate game loop)
function LuxBridge.update(dt)
    timer = timer + dt
    if timer < checkInterval then
        return  -- Wait for next check
    end
    timer = 0
    
    local content, err = LuxBridge.readAlertFile()
    if not content then
        return  -- No file or empty
    end
    
    local alert = LuxBridge.parseAlert(content)
    if LuxBridge.isNewAlert(alert) then
        LuxBridge.processAlert(alert)
    end
end

-- Initialize
function LuxBridge.init()
    print("=")
    print("[LuxBridge] Bridge initialized!")
    print("[LuxBridge] Watching: " .. BRIDGE_FILE)
    print("=")
    
    -- Test by reading current state
    local content = LuxBridge.readAlertFile()
    if content then
        print("[LuxBridge] Bridge file exists and is readable")
    else
        print("[LuxBridge] Creating bridge file...")
        local file = io.open(BRIDGE_FILE, "w")
        if file then
            file:write("")
            file:close()
        end
    end
end

-- Export module
_G.LuxBridge = LuxBridge

-- Auto-initialize if called directly
LuxBridge.init()

-- Return module
return LuxBridge

local lastCheckTime = 0
local lastAlertHash = ""

-- Animation mappings for different alert types
local ANIMATIONS = {
    grade_a = {
        "happy_jump",
        "excited_clap",
        "victory_pose",
        dance = true
    },
    checkpoint = {
        "nod",
        "thumbs_up",
        "smile"
    },
    survivor = {
        "dance",
        "celebrate",
        "wave"
    },
    error = {
        "confused",
        "head_tilt"
    },
    heartbeat = {
        "wave",
        "idle_bounce"
    }
}

-- Read alert file
function LuxBridge.checkForAlerts()
    local file = io.open(BRIDGE_FILE, "r")
    if not file then
        return nil
    end
    
    local content = file:read("*all")
    file:close()
    
    if content == "" then
        return nil
    end
    
    local success, alert = pcall(json.decode, content)
    if not success then
        print("[LuxBridge] Failed to parse alert JSON")
        return nil
    end
    
    -- Check if this is a new alert
    local alertHash = tostring(alert.timestamp) .. tostring(alert.type)
    if alertHash == lastAlertHash then
        return nil -- Already processed
    end
    
    lastAlertHash = alertHash
    return alert
end

-- Trigger avatar animation
function LuxBridge.triggerAnimation(animType)
    local anims = ANIMATIONS[animType] or ANIMATIONS.heartbeat
    
    -- Select random animation from category
    local anim = anims[math.random(#anims)]
    
    -- This is pseudo-code - replace with actual Desktop Mate API calls
    -- DesktopMate.PlayAnimation(anim)
    -- DesktopMate.SetExpression("happy")
    
    print("[LuxBridge] Playing animation: " .. anim)
    
    -- Return to idle after animation
    -- DesktopMate.Schedule("ReturnToIdle", 3.0)
end

-- Display floating text
function LuxBridge.showFloatingText(text, duration)
    -- DesktopMate.ShowFloatingText(text, duration)
    print("[LuxBridge] Floating text: " .. text)
end

-- Main update loop (called by Desktop Mate)
function LuxBridge.update()
    local alert = LuxBridge.checkForAlerts()
    
    if alert then
        print("[LuxBridge] New alert received!")
        print("  Type: " .. alert.type)
        print("  Message: " .. alert.message)
        
        -- Trigger appropriate response
        LuxBridge.triggerAnimation(alert.type)
        LuxBridge.showFloatingText(alert.display_text, 5.0)
        
        -- Mark as processed (clear file)
        local file = io.open(BRIDGE_FILE, "w")
        if file then
            file:write("")
            file:close()
        end
    end
end

-- Initialize
function LuxBridge.init()
    print("[LuxBridge] Initialized!")
    print("[LuxBridge] Watching: " .. BRIDGE_FILE)
    
    -- Create directory if needed
    local dir = os.getenv("USERPROFILE") .. "/DesktopMateLux"
    os.execute('mkdir "' .. dir .. '" 2>nul')
end

return LuxBridge
