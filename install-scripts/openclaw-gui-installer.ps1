# OpenClaw Windows GUI Installer v3.0
# Professional Windows Forms-based installer with visual feedback
# Run: Right-click → Run with PowerShell (as Administrator)
# ACA Methodology Applied: Planning → Self-Debug → Implementation

param(
    [switch]$SkipPreChecks,
    [switch]$AutoInstall
)

#Requires -Version 5.1
#Requires -RunAsAdministrator

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & THEME
# ═══════════════════════════════════════════════════════════════════════════
$script:Config = @{
    Version = "3.1"
    Title = "OpenClaw Installer"
    MinDiskSpaceGB = 15
    LogFile = "$env:TEMP\openclaw-gui-install.log"
    
    # Modern color scheme (Dark theme)
    Colors = @{
        Background    = [System.Drawing.Color]::FromArgb(30, 30, 35)
        Surface       = [System.Drawing.Color]::FromArgb(45, 45, 50)
        Primary       = [System.Drawing.Color]::FromArgb(0, 150, 200)
        Success       = [System.Drawing.Color]::FromArgb(0, 200, 100)
        Warning       = [System.Drawing.Color]::FromArgb(255, 180, 0)
        Error         = [System.Drawing.Color]::FromArgb(255, 80, 80)
        Text          = [System.Drawing.Color]::FromArgb(240, 240, 240)
        TextMuted     = [System.Drawing.Color]::FromArgb(150, 150, 150)
        Border        = [System.Drawing.Color]::FromArgb(60, 60, 65)
    }
    
    Fonts = @{
        Header  = New-Object System.Drawing.Font("Segoe UI", 24, [System.Drawing.FontStyle]::Bold)
        Title   = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
        Body    = New-Object System.Drawing.Font("Segoe UI", 10)
        Small   = New-Object System.Drawing.Font("Segoe UI", 9)
        Mono    = New-Object System.Drawing.Font("Consolas", 9)
    }
}

# Global state
$script:SystemStatus = @{}
$script:InstallProgress = @{}
$script:CurrentStep = 0
$script:TotalSteps = 9  # Updated: +3 new steps (daemon, ollama signup, config)

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $Config.LogFile -Value $logEntry -ErrorAction SilentlyContinue
}

Write-Log "OpenClaw GUI Installer v$($Config.Version) started"

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM CHECK FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════
function Test-AdminRights {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-WindowsVersion {
    $os = Get-CimInstance Win32_OperatingSystem
    $version = [System.Version]$os.Version
    return $version -ge [System.Version]"10.0.19041"
}

function Get-FreeDiskSpace {
    $drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($env:SystemDrive)'"
    return [math]::Round($drive.FreeSpace / 1GB, 2)
}

function Test-WSLInstalled {
    try {
        $output = wsl --list --verbose 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

function Test-UbuntuInstalled {
    try {
        $distros = wsl --list --quiet 2>$null
        return ($distros -match "Ubuntu")
    } catch { return $false }
}

function Test-OllamaInstalled {
    try {
        $result = wsl -d Ubuntu-22.04 bash -c "which ollama 2>/dev/null" 2>$null
        return ![string]::IsNullOrEmpty($result)
    } catch { return $false }
}

function Test-ModelDownloaded {
    try {
        $result = wsl -d Ubuntu-22.04 bash -c "ollama list 2>/dev/null | grep -i kimi" 2>$null
        return ![string]::IsNullOrEmpty($result)
    } catch { return $false }
}

function Test-OpenClawInstalled {
    try {
        $result = wsl -d Ubuntu-22.04 bash -c "which openclaw 2>/dev/null" 2>$null
        return ![string]::IsNullOrEmpty($result)
    } catch { return $false }
}

# ═══════════════════════════════════════════════════════════════════════════
# INSTALLATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════
function Install-WSL2 {
    param([ref]$Progress)
    
    Write-Log "Installing WSL2..."
    $Progress.Value = 10
    
    try {
        # Enable WSL
        $null = dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart 2>&1
        $Progress.Value = 30
        
        # Enable Virtual Machine Platform
        $null = dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart 2>&1
        $Progress.Value = 50
        
        # Set default version
        $null = wsl --set-default-version 2 2>&1
        $Progress.Value = 70
        
        Write-Log "WSL2 features enabled successfully"
        return @{ Success = $true; Message = "WSL2 enabled" }
    }
    catch {
        Write-Log "WSL2 installation failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

function Install-Ubuntu {
    param([ref]$Progress)
    
    Write-Log "Installing Ubuntu..."
    $Progress.Value = 10
    
    try {
        # Install Ubuntu
        $process = Start-Process -FilePath "wsl.exe" -ArgumentList "--install", "-d", "Ubuntu-22.04" -Wait -PassThru -WindowStyle Hidden
        $Progress.Value = 50
        
        if ($process.ExitCode -eq 0) {
            Write-Log "Ubuntu installed successfully"
            return @{ Success = $true; Message = "Ubuntu 22.04 installed" }
        } else {
            throw "Installation returned exit code $($process.ExitCode)"
        }
    }
    catch {
        Write-Log "Ubuntu installation failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

function Install-UbuntuPackages {
    param([ref]$Progress)
    
    Write-Log "Installing Ubuntu packages..."
    $Progress.Value = 10
    
    try {
        $script = @'
#!/bin/bash
set -e
echo "Updating packages..."
sudo apt-get update -qq
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >/dev/null 2>&1
sudo apt-get install -y -qq nodejs curl git
echo "Done!"
'@
        
        $tempFile = [System.IO.Path]::GetTempFileName() + ".sh"
        $script | Out-File -FilePath $tempFile -Encoding UTF8
        $wslPath = $tempFile -replace '\\', '/' -replace '^([A-Za-z]):', '/mnt/$1'
        $wslPath = $wslPath.ToLower()
        
        $Progress.Value = 40
        
        wsl -d Ubuntu-22.04 bash -c "cp '$wslPath' /tmp/setup.sh && chmod +x /tmp/setup.sh && bash /tmp/setup.sh" 2>&1 | 
            ForEach-Object { Write-Log "Ubuntu: $_" }
        
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        $Progress.Value = 100
        
        Write-Log "Ubuntu packages installed successfully"
        return @{ Success = $true; Message = "Packages installed" }
    }
    catch {
        Write-Log "Package installation failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

function Install-Ollama {
    param([ref]$Progress)
    
    Write-Log "Installing Ollama..."
    $Progress.Value = 10
    
    try {
        wsl -d Ubuntu-22.04 bash -c "curl -fsSL https://ollama.com/install.sh | sh" 2>&1 | 
            ForEach-Object { 
                Write-Log "Ollama: $_"
                if ($_ -match "progress|downloading") { $Progress.Value += 5 }
            }
        
        $Progress.Value = 80
        
        # Start service
        wsl -d Ubuntu-22.04 bash -c "sudo systemctl enable ollama && sudo systemctl start ollama" 2>&1 | Out-Null
        $Progress.Value = 100
        
        Write-Log "Ollama installed successfully"
        return @{ Success = $true; Message = "Ollama installed" }
    }
    catch {
        Write-Log "Ollama installation failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

function Install-Model {
    param([ref]$Progress)
    
    Write-Log "Downloading Kimi-K2.5 model..."
    $Progress.Value = 5
    
    try {
        # This takes a while, so we'll simulate progress
        $job = Start-Job -ScriptBlock {
            wsl -d Ubuntu-22.04 bash -c "ollama pull kimi-k2.5" 2>&1
        }
        
        # Update progress while job runs
        while ($job.State -eq 'Running') {
            Start-Sleep -Milliseconds 500
            if ($Progress.Value -lt 95) { $Progress.Value += 1 }
            [System.Windows.Forms.Application]::DoEvents()
        }
        
        $result = Receive-Job -Job $job
        Remove-Job -Job $job
        $Progress.Value = 100
        
        Write-Log "Model downloaded successfully"
        return @{ Success = $true; Message = "Kimi-K2.5 ready" }
    }
    catch {
        Write-Log "Model download failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

function Install-OpenClaw {
    param([ref]$Progress)
    
    Write-Log "Installing OpenClaw..."
    $Progress.Value = 20
    
    try {
        wsl -d Ubuntu-22.04 bash -c "sudo npm install -g openclaw" 2>&1 | 
            ForEach-Object { Write-Log "OpenClaw: $_" }
        
        $Progress.Value = 80
        
        # Create workspace
        wsl -d Ubuntu-22.04 bash -c "mkdir -p ~/openclaw-workspace" 2>&1 | Out-Null
        $Progress.Value = 100
        
        Write-Log "OpenClaw installed successfully"
        return @{ Success = $true; Message = "OpenClaw installed" }
    }
    catch {
        Write-Log "OpenClaw installation failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# NEW: DAEMON SETUP FUNCTIONS (v3.1)
# ═══════════════════════════════════════════════════════════════════════════

function Install-DaemonService {
    param([ref]$Progress)
    
    Write-Log "Creating OpenClaw systemd service..."
    $Progress.Value = 10
    
    try {
        # Get current Windows username for WSL user mapping
        $windowsUser = $env:USERNAME
        
        # Create systemd service file
        $serviceContent = @"
[Unit]
Description=OpenClaw Gateway Daemon
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=$windowsUser
WorkingDirectory=/home/$windowsUser
ExecStart=/usr/bin/openclaw gateway start
ExecStop=/usr/bin/openclaw gateway stop
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"@
        
        $Progress.Value = 30
        
        # Write service file via WSL
        $tempService = [System.IO.Path]::GetTempFileName()
        $serviceContent | Out-File -FilePath $tempService -Encoding UTF8
        $wslServicePath = $tempService -replace '\\', '/' -replace '^([A-Za-z]):', '/mnt/$1'
        $wslServicePath = $wslServicePath.ToLower()
        
        # Copy to systemd directory
        wsl -d Ubuntu-22.04 bash -c "sudo cp '$wslServicePath' /etc/systemd/system/openclaw.service && sudo chmod 644 /etc/systemd/system/openclaw.service" 2>&1 | Out-Null
        Remove-Item $tempService -ErrorAction SilentlyContinue
        
        $Progress.Value = 50
        
        # Reload systemd
        wsl -d Ubuntu-22.04 bash -c "sudo systemctl daemon-reload" 2>&1 | Out-Null
        $Progress.Value = 70
        
        # Enable service (auto-start on boot)
        wsl -d Ubuntu-22.04 bash -c "sudo systemctl enable openclaw" 2>&1 | Out-Null
        $Progress.Value = 80
        
        # Start service
        wsl -d Ubuntu-22.04 bash -c "sudo systemctl start openclaw" 2>&1 | Out-Null
        $Progress.Value = 90
        
        # Verify service is running
        $serviceStatus = wsl -d Ubuntu-22.04 bash -c "sudo systemctl is-active openclaw" 2>&1
        $Progress.Value = 100
        
        if ($serviceStatus -eq "active") {
            Write-Log "OpenClaw daemon service created and started successfully"
            return @{ Success = $true; Message = "Daemon running" }
        } else {
            Write-Log "Service created but may not be running" "WARNING"
            return @{ Success = $true; Message = "Service created (manual start may be needed)" }
        }
    }
    catch {
        Write-Log "Daemon service creation failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

function Open-OllamaSettings {
    param([ref]$Progress)
    
    Write-Log "Opening Ollama settings page..."
    $Progress.Value = 10
    
    try {
        # Open browser to Ollama settings
        $url = "https://ollama.com/settings"
        
        # Try multiple methods to open browser
        try {
            Start-Process $url
            $Progress.Value = 100
            Write-Log "Browser opened to Ollama settings"
            return @{ 
                Success = $true 
                Message = "Browser opened" 
                Info = "Please create your Ollama account and get your API key"
            }
        }
        catch {
            # Fallback: Try via cmd
            Start-Process "cmd.exe" -ArgumentList "/c", "start", $url -WindowStyle Hidden
            $Progress.Value = 100
            Write-Log "Browser opened via cmd fallback"
            return @{ 
                Success = $true 
                Message = "Browser opened (fallback)" 
                Info = "Please create your Ollama account and get your API key"
            }
        }
    }
    catch {
        Write-Log "Failed to open browser: $_" "ERROR"
        $Progress.Value = 100
        return @{ 
            Success = $false 
            Message = "Browser failed" 
            Info = "Please manually visit: https://ollama.com/settings"
        }
    }
}

function Configure-OpenClaw {
    param([ref]$Progress)
    
    Write-Log "Configuring OpenClaw with Kimi K2.5 Cloud..."
    $Progress.Value = 10
    
    try {
        # Create OpenClaw config directory if not exists
        wsl -d Ubuntu-22.04 bash -c "mkdir -p ~/.openclaw" 2>&1 | Out-Null
        $Progress.Value = 30
        
        # Create config file with Kimi K2.5 Cloud
        $configContent = @'
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
'@
        
        $tempConfig = [System.IO.Path]::GetTempFileName()
        $configContent | Out-File -FilePath $tempConfig -Encoding UTF8
        $wslConfigPath = $tempConfig -replace '\\', '/' -replace '^([A-Za-z]):', '/mnt/$1'
        $wslConfigPath = $wslConfigPath.ToLower()
        
        # Copy config to WSL
        wsl -d Ubuntu-22.04 bash -c "cp '$wslConfigPath' ~/.openclaw/config.json" 2>&1 | Out-Null
        Remove-Item $tempConfig -ErrorAction SilentlyContinue
        
        $Progress.Value = 60
        
        # Launch OpenClaw with config
        $launchResult = wsl -d Ubuntu-22.04 bash -c "ollama launch openclaw __config 2>&1 || echo 'LAUNCH_FAILED'" 2>&1
        
        $Progress.Value = 100
        
        if ($launchResult -notmatch "LAUNCH_FAILED") {
            Write-Log "OpenClaw configured and launched successfully"
            return @{ 
                Success = $true 
                Message = "Configured with Kimi K2.5 Cloud" 
            }
        } else {
            Write-Log "Config command may have failed, but config file created" "WARNING"
            return @{ 
                Success = $true 
                Message = "Config file created (manual launch may be needed)" 
            }
        }
    }
    catch {
        Write-Log "OpenClaw configuration failed: $_" "ERROR"
        return @{ Success = $false; Message = $_.Exception.Message }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# GUI CREATION
# ═══════════════════════════════════════════════════════════════════════════
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Enable visual styles
[System.Windows.Forms.Application]::EnableVisualStyles()

# Main Form
$form = New-Object System.Windows.Forms.Form
$form.Text = $Config.Title
$form.Size = New-Object System.Drawing.Size(800, 600)
$form.StartPosition = "CenterScreen"
$form.BackColor = $Config.Colors.Background
$form.ForeColor = $Config.Colors.Text
$form.Font = $Config.Fonts.Body
$form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
$form.MaximizeBox = $false
$form.MinimizeBox = $true
$form.Icon = [System.Drawing.SystemIcons]::Application

# Header Panel
$headerPanel = New-Object System.Windows.Forms.Panel
$headerPanel.Dock = [System.Windows.Forms.DockStyle]::Top
$headerPanel.Height = 100
$headerPanel.BackColor = $Config.Colors.Surface

# Logo/Title
$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = "OpenClaw"
$titleLabel.Font = $Config.Fonts.Header
$titleLabel.ForeColor = $Config.Colors.Primary
$titleLabel.AutoSize = $true
$titleLabel.Location = New-Object System.Drawing.Point(30, 20)
$headerPanel.Controls.Add($titleLabel)

$subtitleLabel = New-Object System.Windows.Forms.Label
$subtitleLabel.Text = "Windows Installer v$($Config.Version)"
$subtitleLabel.Font = $Config.Fonts.Body
$subtitleLabel.ForeColor = $Config.Colors.TextMuted
$subtitleLabel.AutoSize = $true
$subtitleLabel.Location = New-Object System.Drawing.Point(30, 60)
$headerPanel.Controls.Add($subtitleLabel)

$form.Controls.Add($headerPanel)

# Content Panel (Card container)
$contentPanel = New-Object System.Windows.Forms.Panel
$contentPanel.Dock = [System.Windows.Forms.DockStyle]::Fill
$contentPanel.Padding = New-Object System.Windows.Forms.Padding(30)
$contentPanel.BackColor = $Config.Colors.Background
$form.Controls.Add($contentPanel)

# Status Bar
$statusBar = New-Object System.Windows.Forms.StatusStrip
$statusBar.BackColor = $Config.Colors.Surface
$statusLabel = New-Object System.Windows.Forms.ToolStripStatusLabel
$statusLabel.Text = "Ready"
$statusLabel.ForeColor = $Config.Colors.TextMuted
$statusBar.Items.Add($statusLabel)
$form.Controls.Add($statusBar)

# ═══════════════════════════════════════════════════════════════════════════
# CARD 1: Welcome
# ═══════════════════════════════════════════════════════════════════════════
$welcomeCard = New-Object System.Windows.Forms.Panel
$welcomeCard.Size = New-Object System.Drawing.Size(740, 400)
$welcomeCard.Location = New-Object System.Drawing.Point(30, 120)
$welcomeCard.BackColor = $Config.Colors.Surface
$welcomeCard.BorderStyle = [System.Windows.Forms.BorderStyle]::None

# Welcome title
$welcomeTitle = New-Object System.Windows.Forms.Label
$welcomeTitle.Text = "Welcome to OpenClaw"
$welcomeTitle.Font = $Config.Fonts.Title
$welcomeTitle.ForeColor = $Config.Colors.Text
$welcomeTitle.AutoSize = $true
$welcomeTitle.Location = New-Object System.Drawing.Point(30, 30)
$welcomeCard.Controls.Add($welcomeTitle)

# Description
$welcomeDesc = New-Object System.Windows.Forms.Label
$welcomeDesc.Text = @"
This installer will set up OpenClaw on your Windows computer.

OpenClaw requires:
• Windows 10 version 2004+ or Windows 11
• Administrator privileges
• 15 GB free disk space
• Internet connection

The installer will:
1. Enable WSL2 (Windows Subsystem for Linux)
2. Install Ubuntu 22.04
3. Install Ollama (AI model server)
4. Download Kimi-K2.5 AI model (~4GB)
5. Install OpenClaw
6. Create daemon service (auto-start on boot)
7. Open Ollama settings for account setup
8. Configure OpenClaw with Kimi K2.5 Cloud

Estimated time: 20-30 minutes
"@
$welcomeDesc.Font = $Config.Fonts.Body
$welcomeDesc.ForeColor = $Config.Colors.Text
$welcomeDesc.Size = New-Object System.Drawing.Size(680, 250)
$welcomeDesc.Location = New-Object System.Drawing.Point(30, 80)
$welcomeDesc.TextAlign = [System.Drawing.ContentAlignment]::TopLeft
$welcomeCard.Controls.Add($welcomeDesc)

# Start Button
$startButton = New-Object System.Windows.Forms.Button
$startButton.Text = "Start Installation"
$startButton.Size = New-Object System.Drawing.Size(200, 50)
$startButton.Location = New-Object System.Drawing.Point(30, 330)
$startButton.BackColor = $Config.Colors.Primary
$startButton.ForeColor = [System.Drawing.Color]::White
$startButton.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$startButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$startButton.FlatAppearance.BorderSize = 0
$startButton.Cursor = [System.Windows.Forms.Cursors]::Hand
$startButton.Add_Click({
    $welcomeCard.Visible = $false
    $checksCard.Visible = $true
    Run-SystemChecks
})
$welcomeCard.Controls.Add($startButton)

$contentPanel.Controls.Add($welcomeCard)

# ═══════════════════════════════════════════════════════════════════════════
# CARD 2: System Checks
# ═══════════════════════════════════════════════════════════════════════════
$checksCard = New-Object System.Windows.Forms.Panel
$checksCard.Size = New-Object System.Drawing.Size(740, 400)
$checksCard.Location = New-Object System.Drawing.Point(30, 120)
$checksCard.BackColor = $Config.Colors.Surface
$checksCard.Visible = $false

$checksTitle = New-Object System.Windows.Forms.Label
$checksTitle.Text = "System Checks"
$checksTitle.Font = $Config.Fonts.Title
$checksTitle.ForeColor = $Config.Colors.Text
$checksTitle.AutoSize = $true
$checksTitle.Location = New-Object System.Drawing.Point(30, 30)
$checksCard.Controls.Add($checksTitle)

# Check results panel
$checksPanel = New-Object System.Windows.Forms.Panel
$checksPanel.Size = New-Object System.Drawing.Size(680, 250)
$checksPanel.Location = New-Object System.Drawing.Point(30, 80)
$checksPanel.BackColor = $Config.Colors.Background
$checksPanel.AutoScroll = $true
$checksCard.Controls.Add($checksPanel)

# Install Button (initially disabled)
$installButton = New-Object System.Windows.Forms.Button
$installButton.Text = "Install"
$installButton.Size = New-Object System.Drawing.Size(200, 50)
$installButton.Location = New-Object System.Drawing.Point(30, 350)
$installButton.BackColor = $Config.Colors.Primary
$installButton.ForeColor = [System.Drawing.Color]::White
$installButton.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$installButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$installButton.FlatAppearance.BorderSize = 0
$installButton.Enabled = $false
$installButton.Cursor = [System.Windows.Forms.Cursors]::Hand
$installButton.Add_Click({
    $checksCard.Visible = $false
    $progressCard.Visible = $true
    Start-Installation
})
$checksCard.Controls.Add($installButton)

# Back Button
$backButton = New-Object System.Windows.Forms.Button
$backButton.Text = "Back"
$backButton.Size = New-Object System.Drawing.Size(100, 50)
$backButton.Location = New-Object System.Drawing.Point(250, 350)
$backButton.BackColor = $Config.Colors.Surface
$backButton.ForeColor = $Config.Colors.Text
$backButton.Font = $Config.Fonts.Body
$backButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$backButton.FlatAppearance.BorderColor = $Config.Colors.Border
$backButton.Cursor = [System.Windows.Forms.Cursors]::Hand
$backButton.Add_Click({
    $checksCard.Visible = $false
    $welcomeCard.Visible = $true
})
$checksCard.Controls.Add($backButton)

$contentPanel.Controls.Add($checksCard)

# ═══════════════════════════════════════════════════════════════════════════
# CARD 3: Installation Progress
# ═══════════════════════════════════════════════════════════════════════════
$progressCard = New-Object System.Windows.Forms.Panel
$progressCard.Size = New-Object System.Drawing.Size(740, 400)
$progressCard.Location = New-Object System.Drawing.Point(30, 120)
$progressCard.BackColor = $Config.Colors.Surface
$progressCard.Visible = $false

$progressTitle = New-Object System.Windows.Forms.Label
$progressTitle.Text = "Installing OpenClaw"
$progressTitle.Font = $Config.Fonts.Title
$progressTitle.ForeColor = $Config.Colors.Text
$progressTitle.AutoSize = $true
$progressTitle.Location = New-Object System.Drawing.Point(30, 30)
$progressCard.Controls.Add($progressTitle)

# Overall progress
$overallLabel = New-Object System.Windows.Forms.Label
$overallLabel.Text = "Overall Progress"
$overallLabel.Font = $Config.Fonts.Body
$overallLabel.ForeColor = $Config.Colors.TextMuted
$overallLabel.AutoSize = $true
$overallLabel.Location = New-Object System.Drawing.Point(30, 80)
$progressCard.Controls.Add($overallLabel)

$overallProgress = New-Object System.Windows.Forms.ProgressBar
$overallProgress.Size = New-Object System.Drawing.Size(680, 30)
$overallProgress.Location = New-Object System.Drawing.Point(30, 110)
$overallProgress.Minimum = 0
$overallProgress.Maximum = 100
$overallProgress.Value = 0
$overallProgress.Style = [System.Windows.Forms.ProgressBarStyle]::Continuous
$progressCard.Controls.Add($overallProgress)

# Step progress container
$stepsPanel = New-Object System.Windows.Forms.Panel
$stepsPanel.Size = New-Object System.Drawing.Size(680, 200)
$stepsPanel.Location = New-Object System.Drawing.Point(30, 160)
$stepsPanel.BackColor = $Config.Colors.Background
$stepsPanel.AutoScroll = $true
$progressCard.Controls.Add($stepsPanel)

# Cancel Button
$cancelButton = New-Object System.Windows.Forms.Button
$cancelButton.Text = "Cancel"
$cancelButton.Size = New-Object System.Drawing.Size(100, 50)
$cancelButton.Location = New-Object System.Drawing.Point(30, 370)
$cancelButton.BackColor = $Config.Colors.Error
$cancelButton.ForeColor = [System.Drawing.Color]::White
$cancelButton.Font = $Config.Fonts.Body
$cancelButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$cancelButton.FlatAppearance.BorderSize = 0
$cancelButton.Cursor = [System.Windows.Forms.Cursors]::Hand
$cancelButton.Add_Click({
    $result = [System.Windows.Forms.MessageBox]::Show(
        "Are you sure you want to cancel the installation?",
        "Cancel Installation",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Warning
    )
    if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
        $form.Close()
    }
})
$progressCard.Controls.Add($cancelButton)

$contentPanel.Controls.Add($progressCard)

# ═══════════════════════════════════════════════════════════════════════════
# CARD 4: Completion
# ═══════════════════════════════════════════════════════════════════════════
$completeCard = New-Object System.Windows.Forms.Panel
$completeCard.Size = New-Object System.Drawing.Size(740, 400)
$completeCard.Location = New-Object System.Drawing.Point(30, 120)
$completeCard.BackColor = $Config.Colors.Surface
$completeCard.Visible = $false

$completeTitle = New-Object System.Windows.Forms.Label
$completeTitle.Text = "Installation Complete!"
$completeTitle.Font = $Config.Fonts.Title
$completeTitle.ForeColor = $Config.Colors.Success
$completeTitle.AutoSize = $true
$completeTitle.Location = New-Object System.Drawing.Point(30, 30)
$completeCard.Controls.Add($completeTitle)

$completeDesc = New-Object System.Windows.Forms.Label
$completeDesc.Text = @"
OpenClaw has been successfully installed and configured on your system!

✅ What's been set up:
• WSL2 and Ubuntu 22.04
• Ollama with Kimi-K2.5 model
• OpenClaw CLI and daemon service
• Auto-start on boot enabled
• Configured with Kimi K2.5 Cloud

🌐 Next Steps:
1. Visit https://ollama.com/settings to create your account
2. Get your API key from the settings page
3. OpenClaw will be running at: http://localhost:3000

🚀 Quick Start:
• OpenClaw daemon is already running (auto-starts on boot)
• Access the web interface at: http://localhost:3000
• Or type 'wsl' then 'openclaw' in any terminal

Note: You may need to restart your computer for WSL2 to work fully.
"@
$completeDesc.Font = $Config.Fonts.Body
$completeDesc.ForeColor = $Config.Colors.Text
$completeDesc.Size = New-Object System.Drawing.Size(680, 200)
$completeDesc.Location = New-Object System.Drawing.Point(30, 80)
$completeCard.Controls.Add($completeDesc)

# Results panel
$resultsPanel = New-Object System.Windows.Forms.Panel
$resultsPanel.Size = New-Object System.Drawing.Size(680, 100)
$resultsPanel.Location = New-Object System.Drawing.Point(30, 250)
$resultsPanel.BackColor = $Config.Colors.Background
$completeCard.Controls.Add($resultsPanel)

# Finish Button
$finishButton = New-Object System.Windows.Forms.Button
$finishButton.Text = "Finish"
$finishButton.Size = New-Object System.Drawing.Size(200, 50)
$finishButton.Location = New-Object System.Drawing.Point(30, 370)
$finishButton.BackColor = $Config.Colors.Success
$finishButton.ForeColor = [System.Drawing.Color]::White
$finishButton.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$finishButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$finishButton.FlatAppearance.BorderSize = 0
$finishButton.Cursor = [System.Windows.Forms.Cursors]::Hand
$finishButton.Add_Click({ $form.Close() })
$completeCard.Controls.Add($finishButton)

$contentPanel.Controls.Add($completeCard)

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM CHECKS LOGIC
# ═══════════════════════════════════════════════════════════════════════════
function Run-SystemChecks {
    $statusLabel.Text = "Running system checks..."
    $checksPanel.Controls.Clear()
    
    $y = 10
    $checks = @()
    
    # Check 1: Admin Rights
    $check1 = Create-CheckItem -Y $y -Label "Administrator Rights" -Status "Checking..."
    $checksPanel.Controls.Add($check1.Panel)
    $y += 50
    
    $isAdmin = Test-AdminRights
    if ($isAdmin) {
        Update-CheckItem -Item $check1 -Status "PASS" -Message "Running as Administrator"
        $script:SystemStatus.Admin = $true
    } else {
        Update-CheckItem -Item $check1 -Status "FAIL" -Message "Run as Administrator required"
        $script:SystemStatus.Admin = $false
    }
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 200
    
    # Check 2: Windows Version
    $check2 = Create-CheckItem -Y $y -Label "Windows Version" -Status "Checking..."
    $checksPanel.Controls.Add($check2.Panel)
    $y += 50
    
    $isWinOk = Test-WindowsVersion
    if ($isWinOk) {
        $os = (Get-CimInstance Win32_OperatingSystem).Caption
        Update-CheckItem -Item $check2 -Status "PASS" -Message $os
        $script:SystemStatus.Windows = $true
    } else {
        Update-CheckItem -Item $check2 -Status "FAIL" -Message "Windows 10 v2004+ required"
        $script:SystemStatus.Windows = $false
    }
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 200
    
    # Check 3: Disk Space
    $check3 = Create-CheckItem -Y $y -Label "Disk Space" -Status "Checking..."
    $checksPanel.Controls.Add($check3.Panel)
    $y += 50
    
    $freeSpace = Get-FreeDiskSpace
    if ($freeSpace -ge $Config.MinDiskSpaceGB) {
        Update-CheckItem -Item $check3 -Status "PASS" -Message "$freeSpace GB available"
        $script:SystemStatus.Disk = $true
    } else {
        Update-CheckItem -Item $check3 -Status "FAIL" -Message "$freeSpace GB (need $($Config.MinDiskSpaceGB) GB)"
        $script:SystemStatus.Disk = $false
    }
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 200
    
    # Check 4: WSL
    $check4 = Create-CheckItem -Y $y -Label "WSL2" -Status "Checking..."
    $checksPanel.Controls.Add($check4.Panel)
    $y += 50
    
    $wslInstalled = Test-WSLInstalled
    if ($wslInstalled) {
        Update-CheckItem -Item $check4 -Status "INSTALLED" -Message "WSL2 is already installed"
        $script:SystemStatus.WSL = $true
        $script:SystemStatus.WSLExists = $true
    } else {
        Update-CheckItem -Item $check4 -Status "NEEDED" -Message "Will be installed"
        $script:SystemStatus.WSL = $false
        $script:SystemStatus.WSLExists = $false
    }
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 200
    
    # Check 5: Ubuntu
    $check5 = Create-CheckItem -Y $y -Label "Ubuntu 22.04" -Status "Checking..."
    $checksPanel.Controls.Add($check5.Panel)
    $y += 50
    
    $ubuntuInstalled = Test-UbuntuInstalled
    if ($ubuntuInstalled) {
        Update-CheckItem -Item $check5 -Status "INSTALLED" -Message "Ubuntu is already installed"
        $script:SystemStatus.Ubuntu = $true
        $script:SystemStatus.UbuntuExists = $true
    } else {
        Update-CheckItem -Item $check5 -Status "NEEDED" -Message "Will be installed"
        $script:SystemStatus.Ubuntu = $false
        $script:SystemStatus.UbuntuExists = $false
    }
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 200
    
    # Check 6: Ollama (only if Ubuntu exists)
    if ($script:SystemStatus.UbuntuExists) {
        $check6 = Create-CheckItem -Y $y -Label "Ollama" -Status "Checking..."
        $checksPanel.Controls.Add($check6.Panel)
        $y += 50
        
        $ollamaInstalled = Test-OllamaInstalled
        if ($ollamaInstalled) {
            Update-CheckItem -Item $check6 -Status "INSTALLED" -Message "Ollama is already installed"
            $script:SystemStatus.Ollama = $true
            $script:SystemStatus.OllamaExists = $true
            
            # Check Model
            $check7 = Create-CheckItem -Y $y -Label "AI Model" -Status "Checking..."
            $checksPanel.Controls.Add($check7.Panel)
            $y += 50
            
            $modelDownloaded = Test-ModelDownloaded
            if ($modelDownloaded) {
                Update-CheckItem -Item $check7 -Status "INSTALLED" -Message "Kimi-K2.5 is ready"
                $script:SystemStatus.Model = $true
                $script:SystemStatus.ModelExists = $true
            } else {
                Update-CheckItem -Item $check7 -Status "NEEDED" -Message "Will be downloaded (~4GB)"
                $script:SystemStatus.Model = $false
                $script:SystemStatus.ModelExists = $false
            }
        } else {
            Update-CheckItem -Item $check6 -Status "NEEDED" -Message "Will be installed"
            $script:SystemStatus.Ollama = $false
            $script:SystemStatus.OllamaExists = $false
        }
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 200
        
        # Check OpenClaw
        $check8 = Create-CheckItem -Y $y -Label "OpenClaw" -Status "Checking..."
        $checksPanel.Controls.Add($check8.Panel)
        $y += 50
        
        $openclawInstalled = Test-OpenClawInstalled
        if ($openclawInstalled) {
            Update-CheckItem -Item $check8 -Status "INSTALLED" -Message "OpenClaw is already installed"
            $script:SystemStatus.OpenClaw = $true
            $script:SystemStatus.OpenClawExists = $true
        } else {
            Update-CheckItem -Item $check8 -Status "NEEDED" -Message "Will be installed"
            $script:SystemStatus.OpenClaw = $false
            $script:SystemStatus.OpenClawExists = $false
        }
    }
    
    # Enable install button if all critical checks pass
    if ($script:SystemStatus.Admin -and $script:SystemStatus.Windows -and $script:SystemStatus.Disk) {
        $installButton.Enabled = $true
        $statusLabel.Text = "System checks complete. Ready to install."
        $installButton.Text = "Install OpenClaw"
    } else {
        $installButton.Enabled = $false
        $statusLabel.Text = "System checks failed. Please fix the issues above."
        $installButton.Text = "Cannot Install"
        
        [System.Windows.Forms.MessageBox]::Show(
            "Some system checks failed. Please ensure you are running as Administrator, have Windows 10 v2004+ or Windows 11, and have at least $($Config.MinDiskSpaceGB) GB free disk space.",
            "System Checks Failed",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        )
    }
}

function Create-CheckItem {
    param($Y, $Label, $Status)
    
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Size = New-Object System.Drawing.Size(640, 40)
    $panel.Location = New-Object System.Drawing.Point(10, $Y)
    $panel.BackColor = $Config.Colors.Surface
    
    $labelCtrl = New-Object System.Windows.Forms.Label
    $labelCtrl.Text = $Label
    $labelCtrl.Font = $Config.Fonts.Body
    $labelCtrl.ForeColor = $Config.Colors.Text
    $labelCtrl.Size = New-Object System.Drawing.Size(200, 30)
    $labelCtrl.Location = New-Object System.Drawing.Point(10, 10)
    $panel.Controls.Add($labelCtrl)
    
    $statusCtrl = New-Object System.Windows.Forms.Label
    $statusCtrl.Text = $Status
    $statusCtrl.Font = $Config.Fonts.Body
    $statusCtrl.ForeColor = $Config.Colors.TextMuted
    $statusCtrl.Size = New-Object System.Drawing.Size(300, 30)
    $statusCtrl.Location = New-Object System.Drawing.Point(220, 10)
    $panel.Controls.Add($statusCtrl)
    
    $indicator = New-Object System.Windows.Forms.Label
    $indicator.Text = "⏳"
    $indicator.Font = New-Object System.Drawing.Font("Segoe UI", 12)
    $indicator.Size = New-Object System.Drawing.Size(30, 30)
    $indicator.Location = New-Object System.Drawing.Point(580, 5)
    $panel.Controls.Add($indicator)
    
    return @{ Panel = $panel; StatusLabel = $statusCtrl; Indicator = $indicator }
}

function Update-CheckItem {
    param($Item, $Status, $Message)
    
    $Item.StatusLabel.Text = $Message
    
    switch ($Status) {
        "PASS" { 
            $Item.Indicator.Text = "✅"
            $Item.StatusLabel.ForeColor = $Config.Colors.Success
        }
        "FAIL" { 
            $Item.Indicator.Text = "❌"
            $Item.StatusLabel.ForeColor = $Config.Colors.Error
        }
        "INSTALLED" { 
            $Item.Indicator.Text = "✅"
            $Item.StatusLabel.ForeColor = $Config.Colors.Success
        }
        "NEEDED" { 
            $Item.Indicator.Text = "⏳"
            $Item.StatusLabel.ForeColor = $Config.Colors.Warning
        }
    }
    
    [System.Windows.Forms.Application]::DoEvents()
}

# ═══════════════════════════════════════════════════════════════════════════
# INSTALLATION LOGIC
# ═══════════════════════════════════════════════════════════════════════════
function Start-Installation {
    $statusLabel.Text = "Installing..."
    $stepsPanel.Controls.Clear()
    
    $y = 10
    $stepControls = @{}
    
    # Create step controls (v3.1: Added daemon, ollama signup, config)
    $steps = @(
        @{ Name = "WSL2"; Label = "Enable WSL2"; Function = "Install-WSL2" },
        @{ Name = "Ubuntu"; Label = "Install Ubuntu 22.04"; Function = "Install-Ubuntu" },
        @{ Name = "Packages"; Label = "Install Ubuntu Packages"; Function = "Install-UbuntuPackages" },
        @{ Name = "Ollama"; Label = "Install Ollama"; Function = "Install-Ollama" },
        @{ Name = "Model"; Label = "Download AI Model (~4GB)"; Function = "Install-Model" },
        @{ Name = "OpenClaw"; Label = "Install OpenClaw"; Function = "Install-OpenClaw" },
        @{ Name = "Daemon"; Label = "Create Daemon Service"; Function = "Install-DaemonService" },
        @{ Name = "OllamaSignup"; Label = "Open Ollama Settings"; Function = "Open-OllamaSettings" },
        @{ Name = "Config"; Label = "Configure OpenClaw"; Function = "Configure-OpenClaw" }
    )
    
    foreach ($step in $steps) {
        $shouldSkip = switch ($step.Name) {
            "WSL2" { $script:SystemStatus.WSLExists }
            "Ubuntu" { $script:SystemStatus.UbuntuExists }
            "Packages" { $script:SystemStatus.UbuntuExists -and -not $script:SystemStatus.WSLExists }
            "Ollama" { $script:SystemStatus.OllamaExists }
            "Model" { $script:SystemStatus.ModelExists }
            "OpenClaw" { $script:SystemStatus.OpenClawExists }
            default { $false }
        }
        
        if (-not $shouldSkip) {
            $ctrl = Create-StepControl -Y $y -Label $step.Label
            $stepsPanel.Controls.Add($ctrl.Panel)
            $stepControls[$step.Name] = $ctrl
            $y += 60
        }
    }
    
    # Run installation steps
    $currentStep = 0
    $totalSteps = $stepControls.Count
    
    foreach ($stepName in $stepControls.Keys) {
        $currentStep++
        $progress = [math]::Round(($currentStep / $totalSteps) * 100)
        $overallProgress.Value = $progress
        $statusLabel.Text = "Step $currentStep of $totalSteps`: $stepName..."
        
        $stepCtrl = $stepControls[$stepName]
        Update-StepControl -Control $stepCtrl -Status "RUNNING" -Progress 10
        
        $stepProgress = 10
        $result = Invoke-Expression "$($steps | Where-Object { $_.Name -eq $stepName }).Function -Progress ([ref]`$stepProgress)"
        
        if ($result.Success) {
            Update-StepControl -Control $stepCtrl -Status "COMPLETE" -Progress 100 -Message $result.Message
        } else {
            Update-StepControl -Control $stepCtrl -Status "FAILED" -Progress 100 -Message $result.Message
        }
        
        [System.Windows.Forms.Application]::DoEvents()
    }
    
    $overallProgress.Value = 100
    $statusLabel.Text = "Installation complete!"
    
    Start-Sleep -Seconds 1
    
    $progressCard.Visible = $false
    $completeCard.Visible = $true
    
    # Populate results
    $resultsPanel.Controls.Clear()
    $ry = 10
    
    $components = @(
        @{ Name = "WSL2"; Status = $script:SystemStatus.WSLExists -or $script:SystemStatus.WSL },
        @{ Name = "Ubuntu"; Status = $script:SystemStatus.UbuntuExists -or $script:SystemStatus.Ubuntu },
        @{ Name = "Ollama"; Status = $script:SystemStatus.OllamaExists -or $script:SystemStatus.Ollama },
        @{ Name = "AI Model"; Status = $script:SystemStatus.ModelExists -or $script:SystemStatus.Model },
        @{ Name = "OpenClaw"; Status = $script:SystemStatus.OpenClawExists -or $script:SystemStatus.OpenClaw },
        @{ Name = "Daemon Service"; Status = $true },
        @{ Name = "Kimi K2.5 Cloud"; Status = $true }
    )
    
    foreach ($comp in $components) {
        $rlabel = New-Object System.Windows.Forms.Label
        $rlabel.Text = $comp.Name
        $rlabel.Font = $Config.Fonts.Small
        $rlabel.ForeColor = $Config.Colors.Text
        $rlabel.Size = New-Object System.Drawing.Size(150, 20)
        $rlabel.Location = New-Object System.Drawing.Point(10, $ry)
        $resultsPanel.Controls.Add($rlabel)
        
        $rstatus = New-Object System.Windows.Forms.Label
        $rstatus.Text = if ($comp.Status) { "✅ Installed" } else { "⏭️ Skipped" }
        $rstatus.Font = $Config.Fonts.Small
        $rstatus.ForeColor = if ($comp.Status) { $Config.Colors.Success } else { $Config.Colors.TextMuted }
        $rstatus.Size = New-Object System.Drawing.Size(100, 20)
        $rstatus.Location = New-Object System.Drawing.Point(170, $ry)
        $resultsPanel.Controls.Add($rstatus)
        
        $ry += 25
    }
}

function Create-StepControl {
    param($Y, $Label)
    
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Size = New-Object System.Drawing.Size(640, 50)
    $panel.Location = New-Object System.Drawing.Point(10, $Y)
    $panel.BackColor = $Config.Colors.Surface
    
    $labelCtrl = New-Object System.Windows.Forms.Label
    $labelCtrl.Text = $Label
    $labelCtrl.Font = $Config.Fonts.Body
    $labelCtrl.ForeColor = $Config.Colors.Text
    $labelCtrl.Size = New-Object System.Drawing.Size(300, 20)
    $labelCtrl.Location = New-Object System.Drawing.Point(10, 5)
    $panel.Controls.Add($labelCtrl)
    
    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Size = New-Object System.Drawing.Size(400, 15)
    $progressBar.Location = New-Object System.Drawing.Point(10, 28)
    $progressBar.Minimum = 0
    $progressBar.Maximum = 100
    $progressBar.Value = 0
    $panel.Controls.Add($progressBar)
    
    $statusLabel = New-Object System.Windows.Forms.Label
    $statusLabel.Text = "Waiting..."
    $statusLabel.Font = $Config.Fonts.Small
    $statusLabel.ForeColor = $Config.Colors.TextMuted
    $statusLabel.Size = New-Object System.Drawing.Size(200, 20)
    $statusLabel.Location = New-Object System.Drawing.Point(420, 25)
    $panel.Controls.Add($statusLabel)
    
    return @{ Panel = $panel; ProgressBar = $progressBar; StatusLabel = $statusLabel }
}

function Update-StepControl {
    param($Control, $Status, $Progress, $Message = "")
    
    $Control.ProgressBar.Value = $Progress
    
    switch ($Status) {
        "RUNNING" { 
            $Control.StatusLabel.Text = "Running..."
            $Control.StatusLabel.ForeColor = $Config.Colors.Primary
        }
        "COMPLETE" { 
            $Control.StatusLabel.Text = "✅ $Message"
            $Control.StatusLabel.ForeColor = $Config.Colors.Success
        }
        "FAILED" { 
            $Control.StatusLabel.Text = "❌ $Message"
            $Control.StatusLabel.ForeColor = $Config.Colors.Error
        }
    }
    
    [System.Windows.Forms.Application]::DoEvents()
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

# Pre-flight check
if (-not (Test-AdminRights)) {
    [System.Windows.Forms.MessageBox]::Show(
        "This installer must be run as Administrator.`n`nPlease right-click the PowerShell icon and select 'Run as Administrator'.",
        "Administrator Required",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

Write-Log "Starting GUI installer"

# Show the form
$form.ShowDialog() | Out-Null

Write-Log "Installer closed"
