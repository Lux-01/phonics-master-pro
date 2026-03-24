# OpenClaw Windows Installer - Bug Report & Fixes

**Analysis Date:** 2026-03-11  
**Script Version:** 1.0  
**Status:** 🔴 NEEDS FIXES BEFORE DEPLOYMENT

---

## 🔴 CRITICAL BUGS (Must Fix)

### Bug #1: WSL Path Conversion Bug
**Location:** Lines 156-158, 192-194, 223-225, etc.

**Problem:**
```powershell
$tempScript = "$env:TEMP\ubuntu_setup.sh"
wsl -d Ubuntu-22.04 -u root cp "$tempScript" /tmp/setup.sh
```

`$env:TEMP` = `C:\Users\Name\AppData\Local\Temp\ubuntu_setup.sh` (Windows path)

When passed to `wsl cp`, bash sees backslashes as escape characters and fails.

**Fix:** Convert Windows path to WSL path:
```powershell
# Option A: Use wslpath
$wslPath = wsl wslpath -u "$tempScript"
wsl -d Ubuntu-22.04 -u root cp "$wslPath" /tmp/setup.sh

# Option B: Use forward slashes
$tempScriptUnix = $tempScript.Replace('\', '/')
wsl -d Ubuntu-22.04 -u root cp "$tempScriptUnix" /tmp/setup.sh

# Option C: Mount C: drive location
$wslPath = "/mnt/c" + $tempScript.Substring(2).Replace('\', '/')
```

**Impact:** Script fails when copying setup files to WSL

---

### Bug #2: Interactive WSL Install Hangs Script  
**Location:** Line 109

**Problem:**
```powershell
wsl --install -d Ubuntu-22.04
```

This command is **interactive**. It will:
1. Wait for user to press Enter to continue
2. Prompt to create username
3. Prompt to create password
4. Prompt to confirm password

If run unattended (from script), it **hangs forever**.

**Fix:** Skip the interactive install and use quiet mode OR check for first-run:
```powershell
# Option A: Use --no-launch flag (if available)
wsl --install -d Ubuntu-22.04 --no-launch

# Option B: Check if Ubuntu already installed, if not, warn user
$distros = wsl --list --quiet 2>$null
if ($distros -notmatch "Ubuntu") {
    Write-Host "CRITICAL: Ubuntu must be installed first."
    Write-Host "Please run manually: wsl --install -d Ubuntu-22.04"
    Write-Host "Then AFTER creating username/password, run this script again with -SkipWSL"
    exit 1
}
```

**Impact:** Script appears to freeze, user doesn't know why

---

## 🟡 MEDIUM BUGS (Should Fix)

### Bug #3: Nested Heredoc Escaping
**Location:** Lines 251-272 (inside OpenClaw config)

**Problem:**
```powershell
$openclawScript = @'
...
cat > config.json << 'EOF'
...
EOF
'@
```

PowerShell heredoc (`@' '@`) containing bash heredoc (`<< 'EOF'`) with the same delimiter can cause escaping issues.

**Fix:** Use different delimiters or avoid nested heredocs:
```powershell
# Use different markers
$openclawScript = @'
cat > config.json << 'CONFIG_EOF'
...
CONFIG_EOF
'@

# Or use echo with proper escaping
$openclawScript = @'
echo '{
  "gateway": {
    "host": "localhost",
    "port": 3000
  }
}' > config.json
'@
```

**Impact:** Config file might be malformed

---

### Bug #4: No Pre-flight Checks
**Problem:** Script doesn't check prerequisites before starting.

**Checks Missing:**
- Windows version (needs 2004+)
- Sufficient disk space
- Sufficient RAM
- Internet connectivity

**Fix:** Add checks:
```powershell
# Check Windows version
$osVersion = [System.Environment]::OSVersion.Version
if ($osVersion -lt [System.Version]"10.0.19041") {
    Write-Error "Requires Windows 10 version 2004 or later"
    exit 1
}

# Check disk space
$drive = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='$($env:SystemDrive)'"
$freeSpaceGB = [math]::Round($drive.FreeSpace / 1GB, 2)
if ($freeSpaceGB -lt 10) {
    Write-Error "Requires at least 10GB free space. Found: $freeSpaceGB GB"
    exit 1
}

# Check RAM
$ramGB = [math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 0)
if ($ramGB -lt 8) {
    Write-Warning "8GB+ RAM recommended. Found: $ramGB GB"
}
```

---

## 🟢 MINOR ISSUES (Nice to have)

### Issue #5: No Resume Capability
If install fails halfway, user must restart from the beginning.

**Suggestion:** Save state file and resume.

### Issue #6: No Progress Indicator for Downloads
Large downloads (4GB model) show no progress.

**Suggestion:** Add progress bars.

### Issue #7: Fixed Model Name
Hardcoded to `kimi-k2.5`

**Suggestion:** Make configurable.

---

## ✅ VERIFIED GOOD

- ✅ Administrator check works
- ✅ Batch launcher properly calls PowerShell
- ✅ Bash syntax in setup scripts is valid
- ✅ Error handling present (though could be better)
- ✅ Logging to temp file works
- ✅ Function structure is good
- ✅ Color output for readability

---

## 📋 RECOMMENDED FIXES

### Priority 1 (Critical):
1. Fix path conversion for WSL (Bug #1)
2. Handle interactive Ubuntu install (Bug #2)

### Priority 2 (Important):
3. Add pre-flight checks
4. Fix nested heredoc (Bug #3)
5. Add progress indicators

### Priority 3 (Nice to have):
6. Add resume capability
7. Make model configurable
8. Add more detailed logging

---

## 🔧 FIXED VERSION

See `openclaw-windows-installer-FIXED.ps1` for corrected version.

---

## 🎯 DEPLOYMENT RECOMMENDATION

**DO NOT deploy** until:
- ✅ Bug #1 and #2 are fixed
- ✅ Tested on clean Windows 10/11 VM

**Then:**
1. Test on Windows 10 (version 2004+)
2. Test on Windows 11
3. Test with fresh user account
4. Verify all paths with spaces work
5. Test without admin (should fail gracefully)

---

**Reporter:** ALOE Reflection System  
**Generated:** 2026-03-11
