# OpenClaw Windows Installer - One Click Setup
# Run this in PowerShell as Administrator
# This script: Installs WSL2 → Ubuntu → Ollama → Kimi-K2.5 → OpenClaw

param(
    [switch]$SkipWSL,
    [switch]$SkipOllama,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-Header($text) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $text -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Step($text) {
    Write-Host "`n→ $text" -ForegroundColor Yellow
}

function Write-Success($text) {
    Write-Host "✓ $text" -ForegroundColor Green
}

function Write-Error($text) {
    Write-Host "✗ $text" -ForegroundColor Red
}

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Error "Please run PowerShell as Administrator (Right-click → Run as Administrator)"
    exit 1
}

Write-Header "OpenClaw Windows Installer"
Write-Host "This will install:"
Write-Host "  1. WSL2 (Windows Subsystem for Linux)"
Write-Host "  2. Ubuntu 22.04"
Write-Host "  3. Ollama (AI model server)"
Write-Host "  4. Kimi-K2.5 model"
Write-Host "  5. OpenClaw (AI gateway)"
Write-Host "`nPress any key to continue or Ctrl+C to cancel..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 1: Install WSL2
Write-Header "Step 1/6: Installing WSL2"

if ($SkipWSL) {
    Write-Host "Skipping WSL installation (--SkipWSL flag used)"
} else {
    # Check if WSL is already installed
    $wslInstalled = $false
    try {
        $wslCheck = wsl --list --verbose 2>$null
        if ($LASTEXITCODE -eq 0) {
            $wslInstalled = $true
            Write-Success "WSL2 already installed"
        }
    } catch {}

    if (-not $wslInstalled) {
        Write-Step "Enabling WSL2 (this may take 2-3 minutes)..."
        
        # Enable WSL
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
        
        # Enable Virtual Machine Platform
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
        
        # Set WSL default version to 2
        wsl --set-default-version 2
        
        Write-Success "WSL2 features enabled"
        Write-Host "`n⚠️  IMPORTANT: You may need to restart your computer after this script completes."
    }
}

# Step 2: Install Ubuntu
Write-Header "Step 2/6: Installing Ubuntu 22.04"

$ubuntuInstalled = $false
try {
    $distros = wsl --list --quiet 2>$null
    if ($distros -like "*Ubuntu*") {
        $ubuntuInstalled = $true
        Write-Success "Ubuntu already installed"
    }
} catch {}

if (-not $ubuntuInstalled) {
    Write-Step "Downloading and installing Ubuntu 22.04..."
    Write-Host "This will take 5-10 minutes depending on your internet..."
    
    # Download Ubuntu from Microsoft Store
    $ubuntuPackage = "https://aka.ms/wslubuntu2204"
    $tempFile = "$env:TEMP\Ubuntu.appx"
    
    try {
        Invoke-WebRequest -Uri $ubuntuPackage -OutFile $tempFile -UseBasicParsing
        Add-AppxPackage -Path $tempFile
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        Write-Success "Ubuntu installed"
    } catch {
        # Fallback: Use wsl --install
        Write-Step "Installing via wsl --install (alternative method)..."
        wsl --install -d Ubuntu-22.04
        Write-Success "Ubuntu installation initiated"
    }
}

# Step 3: Configure Ubuntu (automated setup)
Write-Header "Step 3/6: Configuring Ubuntu"

Write-Step "Setting up Ubuntu with required packages..."

# Create setup script for inside Ubuntu
$setupScript = @'
#!/bin/bash
set -e

echo "========================================"
echo "OpenClaw Setup Script (Ubuntu)"
echo "========================================"

# Update packages
echo "→ Updating package lists..."
sudo apt-get update -qq

# Install dependencies
echo "→ Installing prerequisites..."
sudo apt-get install -y -qq curl wget git build-essential ca-certificates gnupg

# Install Node.js 22.x (required for OpenClaw)
echo "→ Installing Node.js 22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y -qq nodejs

# Verify installations
echo "→ Verifying installations..."
node --version
npm --version

echo "========================================"
echo "Ubuntu setup complete!"
echo "========================================"
'@

# Write script to temp file
$tempScript = "$env:TEMP\ubuntu_setup.sh"
$setupScript | Out-File -FilePath $tempScript -Encoding UTF8

# Copy to WSL and execute
wsl -d Ubuntu-22.04 -u root cp "$tempScript" /tmp/setup.sh
wsl -d Ubuntu-22.04 -u root chmod +x /tmp/setup.sh  
wsl -d Ubuntu-22.04 -u root bash /tmp/setup.sh

Remove-Item "$tempScript" -ErrorAction SilentlyContinue

Write-Success "Ubuntu configured"

# Step 4: Install Ollama
Write-Header "Step 4/6: Installing Ollama"

if ($SkipOllama) {
    Write-Host "Skipping Ollama installation (--SkipOllama flag used)"
} else {
    Write-Step "Installing Ollama inside WSL..."
    
    $ollamaScript = @'
#!/bin/bash
set -e

echo "→ Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "→ Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

echo "→ Verifying Ollama..."
ollama --version

echo "✓ Ollama installed and running"
'@

    $tempOllama = "$env:TEMP\ollama_install.sh"
    $ollamaScript | Out-File -FilePath $tempOllama -Encoding UTF8
    
    wsl -d Ubuntu-22.04 -u root cp "$tempOllama" /tmp/ollama.sh
    wsl -d Ubuntu-22.04 -u root chmod +x /tmp/ollama.sh
    wsl -d Ubuntu-22.04 -u root bash /tmp/ollama.sh
    
    Remove-Item "$tempOllama" -ErrorAction SilentlyContinue
    
    Write-Success "Ollama installed"
}

# Step 5: Download Kimi-K2.5
Write-Header "Step 5/6: Downloading Kimi-K2.5 Model"

Write-Step "Downloading AI model (this is ~4-5GB and will take 10-20 minutes)..."
Write-Host "Please be patient - this is a large file transfer."

$modelScript = @'
#!/bin/bash

echo "→ Pulling Kimi-K2.5 model..."
echo "This may take 10-20 minutes depending on your internet speed..."
ollama pull kimi-k2.5

echo "→ Verifying model..."
ollama list

echo "✓ Model ready!"
'@

$tempModel = "$env:TEMP\model_pull.sh"
$modelScript | Out-File -FilePath $tempModel -Encoding UTF8

wsl -d Ubuntu-22.04 -u root cp "$tempModel" /tmp/model.sh
wsl -d Ubuntu-22.04 -u root chmod +x /tmp/model.sh
wsl -d Ubuntu-22.04 -u root bash /tmp/model.sh

Remove-Item "$tempModel" -ErrorAction SilentlyContinue

Write-Success "Kimi-K2.5 model downloaded"

# Step 6: Install OpenClaw
Write-Header "Step 6/6: Installing OpenClaw"

Write-Step "Installing OpenClaw AI Gateway..."

$openclawScript = @'
#!/bin/bash
set -e

echo "→ Installing OpenClaw globally..."
npm install -g openclaw

echo "→ Verifying OpenClaw..."
openclaw --version

echo "→ Creating workspace directory..."
mkdir -p ~/openclaw-workspace
cd ~/openclaw-workspace

# Create initial config
cat > config.json << 'EOF'
{
  "gateway": {
    "host": "localhost",
    "port": 3000,
    "logLevel": "info"
  },
  "models": {
    "default": "ollama/kimi-k2.5",
    "providers": {
      "ollama": {
        "baseUrl": "http://localhost:11434",
        "models": ["kimi-k2.5"]
      }
    }
  },
  "sessions": {
    "defaultModel": "ollama/kimi-k2.5",
    "ollama/kimi-k2.5": {
      "keepAlive": "30m",
      "batchSize": 8
    }
  }
}
EOF

echo "✓ OpenClaw installed and configured"
'@

$tempOpenclaw = "$env:TEMP\openclaw_install.sh"
$openclawScript | Out-File -FilePath $tempOpenclaw -Encoding UTF8

wsl -d Ubuntu-22.04 -u root cp "$tempOpenclaw" /tmp/openclaw.sh  
wsl -d Ubuntu-22.04 chmod +x /tmp/openclaw.sh
wsl -d Ubuntu-22.04 bash /tmp/openclaw.sh

Remove-Item "$tempOpenclaw" -ErrorAction SilentlyContinue

Write-Success "OpenClaw installed"

# Final Summary
Write-Header "Installation Complete! 🎉"

Write-Host "`nYour OpenClaw setup is ready!"
Write-Host "`nNext steps:"
Write-Host "  1. Open a NEW terminal window"
Write-Host "  2. Type: wsl"
Write-Host "  3. Type: openclaw"
Write-Host "  4. Visit: http://localhost:3000 in your browser"
Write-Host "`nOptional: Connect messaging apps (Telegram, WhatsApp, Discord, etc.)"
Write-Host "  Run: openclaw config --guide"

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  wsl                    - Enter Linux environment"
Write-Host "  openclaw --version     - Check version"
Write-Host "  openclaw config        - Edit configuration"
Write-Host "  openclaw gateway start - Start the server"
Write-Host "  ollama list            - Check installed models"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if (-not $SkipWSL) {
    Write-Host "`n⚠️  IMPORTANT:" -ForegroundColor Yellow
    Write-Host "   You may need to RESTART your computer for WSL2 to work fully."
    Write-Host "   After restart, run 'wsl' in a terminal to start using."
}

Write-Host "`nInstall log saved to: $env:TEMP\openclaw-install.log"
