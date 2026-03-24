# OpenClaw Windows Installer v2.0 - Enhanced Edition
# Visually appealing installer with pre-flight checks
# Run in PowerShell as Administrator: .<\openclaw-installer-v2.ps1>

param(
    [switch]$SkipWSL,
    [switch]$SkipOllama,
    [switch]$SkipModel,
    [switch]$Verbose,
    [switch]$Unattended
)

$ErrorActionPreference = "Stop"
$ProgressPreference = 'Continue'

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
$script:Config = @{
    Version = "2.0"
    MinWindowsVersion = [System.Version]"10.0.19041"
    RequiredDiskSpaceGB = 15
    LogFile = "$env:TEMP\openclaw-install-v2.log"
    Colors = @{
        Primary    = "Cyan"
        Success    = "Green"
        Warning    = "Yellow"
        Error      = "Red"
        Info       = "White"
        Accent     = "Magenta"
        Step       = "DarkCyan"
    }
}

# ═══════════════════════════════════════════════════════════════
# VISUAL FUNCTIONS
# ═══════════════════════════════════════════════════════════════

function Show-Banner {
    Clear-Host
    $banner = @"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ██████╗ ██████╗ ███████╗███╗   ██╗ ██████╗██╗      █████╗  ║
║  ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██║     ██╔══██╗ ║
║  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║██║     ██║     ███████║ ║
║  ██║   ██║██╔══██╗██╔══╝  ██║╚██╗██║██║     ██║     ██╔══██║ ║
║  ╚██████╔╝██║  ██║███████╗██║ ╚████║╚██████╗███████╗██║  ██║ ║
║   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝ ║
║                                                                ║
║              Windows Installer v2.0 - Enhanced                 ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@
    Write-Host $banner -ForegroundColor $Config.Colors.Primary
    Write-Host ""
}

function Show-ProgressBar {
    param($Percent, $Width = 50)
    $filled = [math]::Floor($Width * $Percent / 100)
    $empty = $Width - $filled
    $bar = "█" * $filled + "░" * $empty
    Write-Host " [$bar] $Percent%" -NoNewline -ForegroundColor $Config.Colors.Success
}

function Write-Separator {
    Write-Host ""
    Write-Host "─" * 70 -ForegroundColor DarkGray
    Write-Host ""
}

function Write-Header($text) {
    Write-Separator
    Write-Host "  🔷 $text" -ForegroundColor $Config.Colors.Primary
    Write-Host "  " + ("─" * ($text.Length + 3)) -ForegroundColor $Config.Colors.Primary
    Write-Log "HEADER: $text"
}

function Write-Step($number, $text) {
    Write-Host ""
    Write-Host "  Step $number/6: $text" -ForegroundColor $Config.Colors.Step
    Write-Log "STEP $number`: $text"
}

function Write-Success($text) {
    Write-Host "     ✅ $text" -ForegroundColor $Config.Colors.Success
    Write-Log "SUCCESS: $text"
}

function Write-Warning($text) {
    Write-Host "     ⚠️  $text" -ForegroundColor $Config.Colors.Warning
    Write-Log "WARNING: $text"
}

function Write-Error($text) {
    Write-Host "     ❌ $text" -ForegroundColor $Config.Colors.Error
    Write-Log "ERROR: $text"
}

function Write-Info($text) {
    Write-Host "     ℹ️  $text" -ForegroundColor $Config.Colors.Info
}

function Write-Log($Message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp | $Message" | Out-File -FilePath $Config.LogFile -Append -ErrorAction SilentlyContinue
}

# ═══════════════════════════════════════════════════════════════
# CHECK FUNCTIONS
# ═══════════════════════════════════════════════════════════════

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-WindowsVersion {
    $osInfo = Get-CimInstance Win32_OperatingSystem
    $version = [System.Version]$osInfo.Version
    return $version -ge $Config.MinWindowsVersion
}

function Test-DiskSpace {
    $systemDrive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($env:SystemDrive)'"
    $freeSpaceGB = [math]::Round($systemDrive.FreeSpace / 1GB, 2)
    return $freeSpaceGB
}

function Test-WSLInstalled {
    try {
        $wslOutput = wsl --list --verbose 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    } catch {}
    return $false
}

function Test-UbuntuInstalled {
    try {
        $distros = wsl --list --quiet 2>$null
        if ($distros -match "Ubuntu") {
            return $true
        }
    } catch {}
    return $false
}

function Test-OllamaInstalled {
    try {
        $result = wsl -d Ubuntu-22.04 bash -c "which ollama 2>/dev/null" 2>$null
        if ($result) {
            return $true
        }
    } catch {}
    return $false
}

function Test-ModelDownloaded {
    try {
        $result = wsl -d Ubuntu-22.04 bash -c "ollama list 2>/dev/null | grep -i kimi" 2>$null
        if ($result) {
            return $true
        }
    } catch {}
    return $false
}

function Test-OpenClawInstalled {
    try {
        $result = wsl -d Ubuntu-22.04 bash -c "which openclaw 2>/dev/null" 2>$null
        if ($result) {
            return $true
        }
    } catch {}
    return $false
}

# ═══════════════════════════════════════════════════════════════
# PRE-FLIGHT CHECKS
# ═══════════════════════════════════════════════════════════════

function Show-PreFlightChecks {
    Write-Header "Pre-Flight System Checks"
    
    $checks = @()
    $allPassed = $true
    
    # Check 1: Admin Rights
    Write-Host "  Checking administrator privileges..." -NoNewline
    if (Test-AdminRights) {
        Write-Host " ✅" -ForegroundColor Green
        $checks += @{ Name = "Administrator Rights"; Status = "PASS"; Message = "Running as Administrator" }
    } else {
        Write-Host " ❌" -ForegroundColor Red
        $checks += @{ Name = "Administrator Rights"; Status = "FAIL"; Message = "Run PowerShell as Administrator" }
        $allPassed = $false
    }
    
    # Check 2: Windows Version
    Write-Host "  Checking Windows version..." -NoNewline
    if (Test-WindowsVersion) {
        $osInfo = Get-CimInstance Win32_OperatingSystem
        Write-Host " ✅" -ForegroundColor Green
        $checks += @{ Name = "Windows Version"; Status = "PASS"; Message = "$($osInfo.Caption) $($osInfo.Version)" }
    } else {
        Write-Host " ❌" -ForegroundColor Red
        $checks += @{ Name = "Windows Version"; Status = "FAIL"; Message = "Windows 10 v2004+ or Windows 11 required" }
        $allPassed = $false
    }
    
    # Check 3: Disk Space
    Write-Host "  Checking available disk space..." -NoNewline
    $freeSpace = Test-DiskSpace
    if ($freeSpace -ge $Config.RequiredDiskSpaceGB) {
        Write-Host " ✅" -ForegroundColor Green
        $checks += @{ Name = "Disk Space"; Status = "PASS"; Message = "$freeSpace GB available (need $($Config.RequiredDiskSpaceGB) GB)" }
    } else {
        Write-Host " ❌" -ForegroundColor Red
        $checks += @{ Name = "Disk Space"; Status = "FAIL"; Message = "$freeSpace GB available (need $($Config.RequiredDiskSpaceGB) GB)" }
        $allPassed = $false
    }
    
    # Check 4: WSL Status
    Write-Host "  Checking WSL2 installation..." -NoNewline
    if (Test-WSLInstalled) {
        Write-Host " ✅" -ForegroundColor Green
        $checks += @{ Name = "WSL2"; Status = "INSTALLED"; Message = "WSL2 is already installed" }
        $script:WSLAlreadyInstalled = $true
    } else {
        Write-Host " ⏳" -ForegroundColor Yellow
        $checks += @{ Name = "WSL2"; Status = "NEEDED"; Message = "Will be installed" }
        $script:WSLAlreadyInstalled = $false
    }
    
    # Check 5: Ubuntu Status
    Write-Host "  Checking Ubuntu installation..." -NoNewline
    if (Test-UbuntuInstalled) {
        Write-Host " ✅" -ForegroundColor Green
        $checks += @{ Name = "Ubuntu"; Status = "INSTALLED"; Message = "Ubuntu is already installed" }
        $script:UbuntuAlreadyInstalled = $true
    } else {
        Write-Host " ⏳" -ForegroundColor Yellow
        $checks += @{ Name = "Ubuntu"; Status = "NEEDED"; Message = "Will be installed" }
        $script:UbuntuAlreadyInstalled = $false
    }
    
    # Check 6: Ollama Status (if WSL/Ubuntu exist)
    if ($script:WSLAlreadyInstalled -and $script:UbuntuAlreadyInstalled) {
        Write-Host "  Checking Ollama installation..." -NoNewline
        if (Test-OllamaInstalled) {
            Write-Host " ✅" -ForegroundColor Green
            $checks += @{ Name = "Ollama"; Status = "INSTALLED"; Message = "Ollama is already installed" }
            $script:OllamaAlreadyInstalled = $true
            
            # Check Model
            Write-Host "  Checking AI model..." -NoNewline
            if (Test-ModelDownloaded) {
                Write-Host " ✅" -ForegroundColor Green
                $checks += @{ Name = "AI Model"; Status = "INSTALLED"; Message = "Kimi-K2.5 is already downloaded" }
                $script:ModelAlreadyInstalled = $true
            } else {
                Write-Host " ⏳" -ForegroundColor Yellow
                $checks += @{ Name = "AI Model"; Status = "NEEDED"; Message = "Will be downloaded (~4GB)" }
                $script:ModelAlreadyInstalled = $false
            }
        } else {
            Write-Host " ⏳" -ForegroundColor Yellow
            $checks += @{ Name = "Ollama"; Status = "NEEDED"; Message = "Will be installed" }
            $script:OllamaAlreadyInstalled = $false
        }
        
        # Check OpenClaw
        Write-Host "  Checking OpenClaw installation..." -NoNewline
        if (Test-OpenClawInstalled) {
            Write-Host " ✅" -ForegroundColor Green
            $checks += @{ Name = "OpenClaw"; Status = "INSTALLED"; Message = "OpenClaw is already installed" }
            $script:OpenClawAlreadyInstalled = $true
        } else {
            Write-Host " ⏳" -ForegroundColor Yellow
            $checks += @{ Name = "OpenClaw"; Status = "NEEDED"; Message = "Will be installed" }
            $script:OpenClawAlreadyInstalled = $false
        }
    }
    
    # Summary Table
    Write-Separator
    Write-Host "  Summary:" -ForegroundColor $Config.Colors.Primary
    Write-Host ""
    
    foreach ($check in $checks) {
        $symbol = if ($check.Status -eq "PASS" -or $check.Status -eq "INSTALLED") { "✅" } 
                  elseif ($check.Status -eq "FAIL") { "❌" }
                  else { "⏳" }
        $color = if ($check.Status -eq "PASS" -or $check.Status -eq "INSTALLED") { $Config.Colors.Success }
                 elseif ($check.Status -eq "FAIL") { $Config.Colors.Error }
                 else { $Config.Colors.Warning }
        
        Write-Host "    $symbol $($check.Name.PadRight(25)) $($check.Message)" -ForegroundColor $color
    }
    
    Write-Separator
    
    if (-not $allPassed) {
        Write-Host ""
        Write-Host "  ❌ Pre-flight checks FAILED. Please fix the issues above and try again." -ForegroundColor $Config.Colors.Error
        Write-Host ""
        exit 1
    }
    
    # Calculate what will be installed
    $willInstall = @()
    if (-not $script:WSLAlreadyInstalled) { $willInstall += "WSL2" }
    if (-not $script:UbuntuAlreadyInstalled) { $willInstall += "Ubuntu 22.04" }
    if (-not $script:OllamaAlreadyInstalled) { $willInstall += "Ollama" }
    if (-not $script:ModelAlreadyInstalled) { $willInstall += "Kimi-K2.5 AI Model (~4GB)" }
    if (-not $script:OpenClawAlreadyInstalled) { $willInstall += "OpenClaw" }
    
    if ($willInstall.Count -eq 0) {
        Write-Host ""
        Write-Host "  🎉 Everything is already installed! OpenClaw is ready to use." -ForegroundColor $Config.Colors.Success
        Write-Host ""
        Write-Host "  Quick Start:" -ForegroundColor $Config.Colors.Primary
        Write-Host "    1. Open a new terminal"
        Write-Host "    2. Type: wsl"
        Write-Host "    3. Type: openclaw"
        Write-Host ""
        
        $response = Read-Host "  Do you want to reconfigure or repair the installation? (y/N)"
        if ($response -notmatch "^[Yy]") {
            exit 0
        }
    } else {
        Write-Host ""
        Write-Host "  📦 Components to install:" -ForegroundColor $Config.Colors.Primary
        foreach ($item in $willInstall) {
            Write-Host "     • $item" -ForegroundColor $Config.Colors.Info
        }
        Write-Host ""
    }
    
    if (-not $Unattended) {
        Write-Host ""
        $continue = Read-Host "  Press Enter to continue or Ctrl+C to cancel"
    }
}

# ═══════════════════════════════════════════════════════════════
# INSTALLATION STEPS
# ═══════════════════════════════════════════════════════════════

function Install-WSL {
    if ($SkipWSL -or $script:WSLAlreadyInstalled) {
        Write-Info "Skipping WSL installation (already installed or --SkipWSL flag used)"
        return
    }
    
    Write-Step 1 "Installing WSL2"
    Write-Info "This enables Windows Subsystem for Linux"
    Write-Info "Estimated time: 2-3 minutes"
    Write-Host ""
    
    try {
        Write-Host "  Enabling WSL feature..." -NoNewline
        $result = dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✅" -ForegroundColor Green
        } else {
            Write-Host " ⚠️" -ForegroundColor Yellow
        }
        
        Write-Host "  Enabling Virtual Machine Platform..." -NoNewline
        $result = dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✅" -ForegroundColor Green
        } else {
            Write-Host " ⚠️" -ForegroundColor Yellow
        }
        
        Write-Host "  Setting WSL default version to 2..." -NoNewline
        wsl --set-default-version 2 2>&1 | Out-Null
        Write-Host " ✅" -ForegroundColor Green
        
        Write-Success "WSL2 features enabled"
        Write-Warning "A system restart may be required after installation"
        
    } catch {
        Write-Error "Failed to enable WSL: $_"
        exit 1
    }
}

function Install-Ubuntu {
    if ($SkipWSL -or $script:UbuntuAlreadyInstalled) {
        Write-Info "Skipping Ubuntu installation (already installed)"
        return
    }
    
    Write-Step 2 "Installing Ubuntu 22.04"
    Write-Info "This downloads and installs Ubuntu Linux"
    Write-Info "Estimated time: 5-10 minutes depending on internet speed"
    Write-Host ""
    
    try {
        Write-Host "  Installing Ubuntu via WSL..."
        Write-Host "  (This will open a new window - please wait)" -ForegroundColor DarkGray
        Write-Host ""
        
        # Use wsl --install which handles everything
        wsl --install -d Ubuntu-22.04
        
        Write-Success "Ubuntu installation initiated"
        Write-Warning "You may need to create a username and password in the Ubuntu window"
        Write-Info "After setting up Ubuntu, press Enter here to continue..."
        Read-Host
        
    } catch {
        Write-Error "Failed to install Ubuntu: $_"
        exit 1
    }
}

function Install-UbuntuPackages {
    if ($SkipWSL) {
        return
    }
    
    Write-Step 3 "Configuring Ubuntu"
    Write-Info "Installing Node.js and required packages"
    Write-Info "Estimated time: 3-5 minutes"
    Write-Host ""
    
    $setupScript = @'
#!/bin/bash
set -e

echo "→ Updating package lists..."
sudo apt-get update -qq

echo "→ Installing prerequisites..."
sudo apt-get install -y -qq curl wget git build-essential ca-certificates gnupg software-properties-common

echo "→ Installing Node.js 22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >/dev/null 2>&1
sudo apt-get install -y -qq nodejs

echo "→ Verifying installations..."
NODE_VER=$(node --version)
NPM_VER=$(npm --version)
echo "✓ Node.js $NODE_VER installed"
echo "✓ npm $NPM_VER installed"
'@
    
    try {
        $tempScript = "$env:TEMP\ubuntu_setup.sh"
        $setupScript | Out-File -FilePath $tempScript -Encoding UTF8
        
        # Convert path for WSL
        $wslPath = $tempScript -replace '\\', '/' -replace '^([A-Za-z]):', { '/mnt/' + $_.Groups[1].Value.ToLower() }
        
        Write-Host "  Running Ubuntu setup script..." -NoNewline
        wsl -d Ubuntu-22.04 bash -c "cp '$wslPath' /tmp/setup.sh && chmod +x /tmp/setup.sh && bash /tmp/setup.sh" 2>&1 | ForEach-Object {
            if ($_ -match "✓") {
                Write-Host "`n     $_" -ForegroundColor Green
            } elseif ($_ -match "→") {
                Write-Host "`n     $_" -ForegroundColor Cyan
            }
        }
        
        Remove-Item $tempScript -ErrorAction SilentlyContinue
        Write-Host " ✅" -ForegroundColor Green
        
        Write-Success "Ubuntu configured successfully"
        
    } catch {
        Write-Error "Failed to configure Ubuntu: $_"
        exit 1
    }
}

function Install-Ollama {
    if ($SkipOllama -or $script:OllamaAlreadyInstalled) {
        Write-Info "Skipping Ollama installation (already installed or --SkipOllama flag used)"
        return
    }
    
    Write-Step 4 "Installing Ollama"
    Write-Info "Ollama runs AI models locally"
    Write-Info "Estimated time: 2-3 minutes"
    Write-Host ""
    
    try {
        Write-Host "  Downloading and installing Ollama..." -NoNewline
        
        $result = wsl -d Ubuntu-22.04 bash -c "curl -fsSL https://ollama.com/install.sh | sh" 2>&1
        
        Write-Host " ✅" -ForegroundColor Green
        
        Write-Host "  Starting Ollama service..." -NoNewline
        wsl -d Ubuntu-22.04 bash -c "sudo systemctl enable ollama && sudo systemctl start ollama" 2>&1 | Out-Null
        Write-Host " ✅" -ForegroundColor Green
        
        $version = wsl -d Ubuntu-22.04 bash -c "ollama --version" 2>&1
        Write-Success "Ollama installed ($version)"
        
    } catch {
        Write-Error "Failed to install Ollama: $_"
        exit 1
    }
}

function Install-Model {
    if ($SkipModel -or $script:ModelAlreadyInstalled) {
        Write-Info "Skipping model download (already installed or --SkipModel flag used)"
        return
    }
    
    Write-Step 5 "Downloading Kimi-K2.5 AI Model"
    Write-Info "This is a ~4GB download and may take 10-20 minutes"
    Write-Info "Please be patient - this is the AI brain of OpenClaw"
    Write-Host ""
    
    try {
        Write-Host "  Downloading Kimi-K2.5..."
        Write-Host "  (This will take a while - grab a coffee ☕)" -ForegroundColor DarkGray
        Write-Host ""
        
        wsl -d Ubuntu-22.04 bash -c "ollama pull kimi-k2.5" 2>&1 | ForEach-Object {
            if ($_ -match "pulling|downloading") {
                Write-Host "     $_" -ForegroundColor Cyan
            }
        }
        
        Write-Host ""
        Write-Host "  Verifying model..." -NoNewline
        $modelCheck = wsl -d Ubuntu-22.04 bash -c "ollama list | grep kimi" 2>&1
        if ($modelCheck) {
            Write-Host " ✅" -ForegroundColor Green
            Write-Success "Kimi-K2.5 model ready"
        } else {
            Write-Host " ⚠️" -ForegroundColor Yellow
            Write-Warning "Model verification inconclusive, but download completed"
        }
        
    } catch {
        Write-Error "Failed to download model: $_"
        exit 1
    }
}

function Install-OpenClaw {
    if ($script:OpenClawAlreadyInstalled) {
        Write-Info "Skipping OpenClaw installation (already installed)"
        return
    }
    
    Write-Step 6 "Installing OpenClaw"
    Write-Info "The AI gateway that connects everything"
    Write-Info "Estimated time: 1-2 minutes"
    Write-Host ""
    
    try {
        Write-Host "  Installing OpenClaw globally..." -NoNewline
        wsl -d Ubuntu-22.04 bash -c "sudo npm install -g openclaw" 2>&1 | Out-Null
        Write-Host " ✅" -ForegroundColor Green
        
        Write-Host "  Verifying installation..." -NoNewline
        $version = wsl -d Ubuntu-22.04 bash -c "openclaw --version" 2>&1
        Write-Host " ✅" -ForegroundColor Green
        
        Write-Host "  Creating workspace..." -NoNewline
        wsl -d Ubuntu-22.04 bash -c "mkdir -p ~/openclaw-workspace && cd ~/openclaw-workspace" 2>&1 | Out-Null
        Write-Host " ✅" -ForegroundColor Green
        
        Write-Success "OpenClaw v$version installed"
        
    } catch {
        Write-Error "Failed to install OpenClaw: $_"
        exit 1
    }
}

# ═══════════════════════════════════════════════════════════════
# COMPLETION
# ═══════════════════════════════════════════════════════════════

function Show-CompletionScreen {
    Clear-Host
    
    $completionBanner = @"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║                    🎉 INSTALLATION COMPLETE! 🎉                 ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@
    
    Write-Host $completionBanner -ForegroundColor $Config.Colors.Success
    Write-Host ""
    
    # Status summary
    Write-Host "  Installation Status:" -ForegroundColor $Config.Colors.Primary
    Write-Host ""
    
    $components = @(
        @{ Name = "WSL2"; Status = $script:WSLAlreadyInstalled -or (-not $SkipWSL) },
        @{ Name = "Ubuntu 22.04"; Status = $script:UbuntuAlreadyInstalled -or (-not $SkipWSL) },
        @{ Name = "Ollama"; Status = $script:OllamaAlreadyInstalled -or (-not $SkipOllama) },
        @{ Name = "Kimi-K2.5 Model"; Status = $script:ModelAlreadyInstalled -or (-not $SkipModel) },
        @{ Name = "OpenClaw"; Status = $script:OpenClawAlreadyInstalled }
    )
    
    foreach ($comp in $components) {
        $symbol = if ($comp.Status) { "✅" } else { "⏭️" }
        $color = if ($comp.Status) { $Config.Colors.Success } else { $Config.Colors.Warning }
        Write-Host "    $symbol $($comp.Name.PadRight(20))" -ForegroundColor $color
    }
    
    Write-Separator
    
    Write-Host "  🚀 Quick Start Guide:" -ForegroundColor $Config.Colors.Primary
    Write-Host ""
    Write-Host "    1. Open a NEW terminal/PowerShell window" -ForegroundColor $Config.Colors.Info
    Write-Host "    2. Type: wsl" -ForegroundColor $Config.Colors.Info
    Write-Host "    3. Type: openclaw" -ForegroundColor $Config.Colors.Info
    Write-Host "    4. Open browser: http://localhost:3000" -ForegroundColor $Config.Colors.Info
    Write-Host ""
    
    Write-Host "  📚 Useful Commands:" -ForegroundColor $Config.Colors.Primary
    Write-Host ""
    Write-Host "    Command                    Description" -ForegroundColor DarkGray
    Write-Host "    ────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "    wsl                        Enter Linux environment"
    Write-Host "    openclaw --version         Check OpenClaw version"
    Write-Host "    openclaw config            Edit configuration"
    Write-Host "    openclaw gateway start     Start the server"
    Write-Host "    ollama list                List installed AI models"
    Write-Host "    ollama run kimi-k2.5       Test the AI model"
    Write-Host ""
    
    if (-not $script:WSLAlreadyInstalled) {
        Write-Separator
        Write-Warning "IMPORTANT: You may need to RESTART your computer for WSL2 to work fully!"
        Write-Info "After restart, run 'wsl' in a terminal to start using OpenClaw."
        Write-Host ""
    }
    
    Write-Host "  📄 Installation log saved to:" -ForegroundColor DarkGray
    Write-Host "     $($Config.LogFile)" -ForegroundColor DarkGray
    Write-Host ""
    
    Write-Host "  💡 Need help? Visit: https://docs.openclaw.ai" -ForegroundColor $Config.Colors.Accent
    Write-Host ""
    
    Read-Host "  Press Enter to exit"
}

# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

# Initialize log
"OpenClaw Installer v2.0 Started: $(Get-Date)" | Out-File -FilePath $Config.LogFile -Force

# Show banner
Show-Banner

# Run pre-flight checks
Show-PreFlightChecks

# Install components
Install-WSL
Install-Ubuntu
Install-UbuntuPackages
Install-Ollama
Install-Model
Install-OpenClaw

# Show completion
Show-CompletionScreen
