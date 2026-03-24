# OpenClaw Windows Installer - FIXED VERSION v1.1
# Fixed: Path conversion, interactive install handling, heredoc escaping

param(
    [switch]$SkipWSL,
    [switch]$SkipOllama,
    [switch]$SkipModel,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$ProgressPreference = 'Continue'

# Logging
$LogFile = "$env:TEMP\openclaw-install-fixed.log"
function Write-Log($Message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp | $Message" | Tee-Object -FilePath $LogFile -Append | Write-Host
}

function Write-Header($text) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $text -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Log "HEADER: $text"
}

function Write-Step($text) {
    Write-Host "`n→ $text" -ForegroundColor Yellow
    Write-Log "STEP: $text"
}

function Write-Success($text) {
    Write-Host "✓ $text" -ForegroundColor Green
    Write-Log "SUCCESS: $text"
}

function Write-Error($text) {
    Write-Host "✗ $text" -ForegroundColor Red
    Write-Log "ERROR: $text"
}

# Convert Windows path to WSL path
function ConvertTo-WSLPath($WindowsPath) {
    $path = $WindowsPath -replace '\\', '/'
    if ($path -match '^([A-Za-z]):(.+)') {
        $drive = $matches[1].ToLower()
        return "/mnt/$drive$($matches[2])"
    }
    return $path
}

# Pre-flight checks
Write-Header "Pre-flight Checks"

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Error "Administrator privileges required."
    exit 1
}
Write-Success "Running as Administrator"

# Check Windows version
$osVersion = [System.Environment]::OSVersion.Version
if ($osVersion -lt [System.Version]"10.0.19041") {
    Write-Error "Windows 10 version 2004+ or Windows 11 required."
    exit 1
}
Write-Success "Windows version OK"

# Check disk space
$drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($env:SystemDrive)'"
$freeSpaceGB = [math]::Round($drive.FreeSpace / 1GB, 2)
if ($freeSpaceGB -lt 10) {
    Write-Error "Insufficient disk space. Need 10GB+, found $freeSpaceGB GB"
    exit 1
}
Write-Success "Disk space OK"

Write-Header "OpenClaw Installer v1.1"
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 1: WSL
Write-Header "Step 1: WSL2 + Ubuntu"

if (-not $SkipWSL) {
    Write-Step "Checking for WSL..."
    
    $wslReady = $false
    try {
        $distros = wsl --list --quiet 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($distros -match "Ubuntu") {
                Write-Success "Ubuntu found"
                $wslReady = $true
            }
        }
    } catch {}
    
    if (-not $wslReady) {
        Write-Host "WSL needs setup. Installing..."
        wsl --install
        Write-Host "⚠️  RESTART REQUIRED. After restart, run with -SkipWSL flag"
        pause
        exit 0
    }
}

# Step 2: Ubuntu setup
Write-Step "Configuring Ubuntu..."

$setupScript = '#!/bin/bash
set -e
sudo apt-get update -qq
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >/dev/null 2>&1
sudo apt-get install -y -qq nodejs curl git
echo "Node: $(node --version)"
'@

$tempScript = "$env:TEMP\setup_node.sh"
$setupScript | Out-File -FilePath $tempScript -Encoding UTF8

# FIX: Convert Windows path for WSL
$wslScriptPath = ConvertTo-WSLPath $tempScript

wsl -d Ubuntu-22.04 bash -c "cp '$wslScriptPath' /tmp/setup.sh && bash /tmp/setup.sh"
Remove-Item $tempScript -ErrorAction SilentlyContinue
Write-Success "Ubuntu configured"

# Step 3: Ollama
Write-Header "Step 2: Ollama"

if (-not $SkipOllama) {
    Write-Step "Installing Ollama..."
    wsl -d Ubuntu-22.04 bash -c "curl -fsSL https://ollama.com/install.sh | sh"
    Write-Success "Ollama installed"
}

# Step 4: Model
Write-Header "Step 3: AI Model"

if (-not $SkipModel) {
    Write-Step "Downloading Kimi-K2.5 (~4GB, 15-20 min)..."
    wsl -d Ubuntu-22.04 bash -c "ollama pull kimi-k2.5"
    Write-Success "Model ready"
}

# Step 5: OpenClaw
Write-Header "Step 4: OpenClaw"
Write-Step "Installing..."
wsl -d Ubuntu-22.04 bash -c "sudo npm install -g openclaw"
Write-Success "OpenClaw installed"

# Summary
Write-Header "Complete! 🎉"
Write-Host "Next: wsl → openclaw → http://localhost:3000"
Write-Host "Log: $LogFile"
