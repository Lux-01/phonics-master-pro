# OpenClaw GUI Installer v3.1 - ACA Implementation Report

**Date:** March 16, 2026  
**Methodology:** Autonomous Code Architect (ACA)  
**Version:** 3.1 (Added daemon setup + Ollama config)

---

## 🎯 ACA Methodology Applied

### Phase 1: Planning (7-Step Workflow)

#### Step 1: Requirements Analysis
**New Requirements:**
1. **Automatic daemon setup** - Create systemd service for auto-start
2. **Ollama signup prompt** - Open browser to https://ollama.com/settings
3. **Auto-configure OpenClaw** - Run `ollama launch openclaw __config` with Kimi K2.5 Cloud

**Success Criteria:**
- Daemon starts automatically on boot
- User sees browser open to Ollama settings
- OpenClaw configured and ready to use

#### Step 2: Architecture Design
```
Updated Installation Flow:
├── Existing Steps 1-6 (WSL, Ubuntu, Packages, Ollama, Model, OpenClaw)
├── NEW Step 7: Create Systemd Service
│   ├── Create /etc/systemd/system/openclaw.service
│   ├── Enable service (systemctl enable)
│   ├── Start service (systemctl start)
│   └── Verify service is running
├── NEW Step 8: Open Ollama Settings
│   ├── Launch browser to https://ollama.com/settings
│   └── Show message: "Create account and get API key"
└── NEW Step 9: Configure OpenClaw
    ├── Create config file with Kimi K2.5 Cloud
    ├── Run: ollama launch openclaw __config
    └── Verify configuration
```

#### Step 3: Data Flow
```
1. OpenClaw installation completes
   ↓
2. Create systemd service file
   ↓
3. Reload systemd daemon
   ↓
4. Enable service (auto-start on boot)
   ↓
5. Start service now
   ↓
6. Verify service status
   ↓
7. Open browser to ollama.com/settings
   ↓
8. Create OpenClaw config file
   ↓
9. Launch OpenClaw with config
   ↓
10. Show final completion with status
```

#### Step 4: Edge Cases
| Edge Case | Handling |
|-----------|----------|
| Systemd not available | Skip service creation, show manual instructions |
| Service already exists | Stop, update, restart |
| Browser launch fails | Show URL in message box for manual copy |
| Config command fails | Log error, show manual config steps |
| Service fails to start | Show error log, manual start instructions |

#### Step 5: Tool Constraints
- **Systemd:** Requires root privileges (already have as admin)
- **Browser:** `Start-Process` from PowerShell, fallback to `cmd.exe /c start`
- **Config:** WSL bash commands to create files and run commands

#### Step 6: Error Handling Strategy
```powershell
try {
    # Create service file
} catch {
    Log error
    Show warning: "Service creation failed. Manual setup required."
    Continue to next step
}
```

#### Step 7: Testing Plan
- Happy path: Fresh install → All steps complete
- Edge cases: Service exists, browser blocked, config fails

---

## 🔍 Phase 2: Self-Debug

**Issues Identified Before Coding:**

1. **Systemd not in WSL** → Check if available, fallback to manual
2. **Browser doesn't open** → Use `cmd.exe /c start` from WSL as fallback
3. **Config command syntax** → Verify exact command: `ollama launch openclaw __config`
4. **Service permissions** → Ensure service runs as correct user
5. **Model name format** → Verify: `kimi-k2.5:cloud`

---

## 💻 Phase 3: Implementation

### New Functions Added:

#### 1. Install-DaemonService
Creates systemd service for auto-start:
```powershell
function Install-DaemonService {
    # Creates /etc/systemd/system/openclaw.service
    # Enables auto-start: systemctl enable openclaw
    # Starts service: systemctl start openclaw
    # Verifies: systemctl is-active openclaw
}
```

**Service File:**
```ini
[Unit]
Description=OpenClaw Gateway Daemon
After=network.target ollama.service

[Service]
Type=simple
User={username}
ExecStart=/usr/bin/openclaw gateway start
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 2. Open-OllamaSettings
Opens browser to Ollama settings:
```powershell
function Open-OllamaSettings {
    # Opens: https://ollama.com/settings
    # Fallback: Show URL in message box
}
```

#### 3. Configure-OpenClaw
Configures OpenClaw with Kimi K2.5 Cloud:
```powershell
function Configure-OpenClaw {
    # Creates ~/.openclaw/config.json
    # Sets model: "kimi-k2.5:cloud"
    # Runs: ollama launch openclaw __config
}
```

**Config File:**
```json
{
  "model": "kimi-k2.5:cloud",
  "gateway": {
    "enabled": true,
    "port": 3000,
    "host": "localhost"
  },
  "logging": {
    "level": "info",
    "file": "~/.openclaw/openclaw.log"
  }
}
```

---

## 📊 Changes Summary

| Aspect | v3.0 | v3.1 |
|--------|------|------|
| Total Steps | 6 | 9 |
| Daemon Setup | ❌ Manual | ✅ Automatic |
| Ollama Signup | ❌ Manual | ✅ Auto-opens browser |
| Config | ❌ Manual | ✅ Auto-configured |
| Auto-start | ❌ No | ✅ Systemd service |

---

## 🚀 Usage

**Run the installer:**
```powershell
# As Administrator
powershell -ExecutionPolicy Bypass -File openclaw-gui-installer.ps1
```

**What happens automatically:**
1. ✅ Installs all components (WSL, Ubuntu, Ollama, OpenClaw)
2. ✅ Creates systemd service for auto-start
3. ✅ Opens browser to https://ollama.com/settings
4. ✅ Configures OpenClaw with Kimi K2.5 Cloud
5. ✅ Starts the daemon

**User only needs to:**
- Create Ollama account at the opened page
- Get API key from settings
- Visit http://localhost:3000 to use OpenClaw

---

## ✅ ACA Checklist

| ACA Step | Status |
|----------|--------|
| 1. Requirements Analysis | ✅ Complete |
| 2. Architecture Design | ✅ Complete |
| 3. Data Flow Planning | ✅ Complete |
| 4. Edge Case Identification | ✅ Complete (5 cases) |
| 5. Tool Constraints Analysis | ✅ Complete |
| 6. Error Handling Strategy | ✅ Complete |
| 7. Testing Plan | ✅ Complete |
| Self-Debug | ✅ Complete (5 issues) |
| Code Generation | ✅ Complete (3 new functions) |
| Versioning | ✅ Complete (v3.1) |

---

**Built with ACA Methodology** ⚡
*Plan → Debug → Code → Test → Version*
