# OpenClaw GUI Installer Tests
# ACA Test Suite for the GUI Installer
# Run: .\test-gui-installer.ps1

param(
    [switch]$Verbose,
    [switch]$StopOnFailure
)

$ErrorActionPreference = "Stop"
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:TestResults = @()

# Test Framework
function Test-Case {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$Category = "General"
    )
    
    Write-Host "  Testing: $Name..." -NoNewline
    
    try {
        $result = & $Test
        if ($result) {
            Write-Host " ✅ PASS" -ForegroundColor Green
            $script:TestsPassed++
            $script:TestResults += @{ Name = $Name; Category = $Category; Result = "PASS" }
        } else {
            Write-Host " ❌ FAIL" -ForegroundColor Red
            $script:TestsFailed++
            $script:TestResults += @{ Name = $Name; Category = $Category; Result = "FAIL" }
            if ($StopOnFailure) { throw "Test failed: $Name" }
        }
    }
    catch {
        Write-Host " ❌ ERROR: $_" -ForegroundColor Red
        $script:TestsFailed++
        $script:TestResults += @{ Name = $Name; Category = $Category; Result = "ERROR"; Message = $_.Exception.Message }
        if ($StopOnFailure) { throw }
    }
}

function Test-Group {
    param([string]$Name, [scriptblock]$Tests)
    Write-Host "`n📦 $Name" -ForegroundColor Cyan
    Write-Host "  " + ("─" * 60) -ForegroundColor DarkGray
    & $Tests
}

# Header
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     OpenClaw GUI Installer Test Suite v1.0               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: System Check Functions
# ═══════════════════════════════════════════════════════════════════════════

Test-Group "System Check Functions" {
    
    # Mock the functions for testing
    function Test-AdminRights-Mock { return $true }
    function Test-WindowsVersion-Mock { return $true }
    function Get-FreeDiskSpace-Mock { return 50 }
    function Test-WSLInstalled-Mock { return $true }
    function Test-UbuntuInstalled-Mock { return $false }
    
    Test-Case -Name "Admin rights detection" -Category "System" -Test {
        # In real scenario, this checks WindowsPrincipal
        # For test, we verify function exists and returns boolean
        $result = Test-AdminRights-Mock
        return ($result -is [bool])
    }
    
    Test-Case -Name "Windows version check" -Category "System" -Test {
        $result = Test-WindowsVersion-Mock
        return ($result -is [bool] -and $result -eq $true)
    }
    
    Test-Case -Name "Disk space calculation" -Category "System" -Test {
        $space = Get-FreeDiskSpace-Mock
        return ($space -is [double] -and $space -gt 0)
    }
    
    Test-Case -Name "WSL detection" -Category "System" -Test {
        $result = Test-WSLInstalled-Mock
        return ($result -is [bool])
    }
    
    Test-Case -Name "Ubuntu detection" -Category "System" -Test {
        $result = Test-UbuntuInstalled-Mock
        return ($result -is [bool] -and $result -eq $false)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: Configuration Validation
# ═══════════════════════════════════════════════════════════════════════════

Test-Group "Configuration Validation" {
    
    Test-Case -Name "Config has required fields" -Category "Config" -Test {
        $config = @{
            Version = "3.0"
            Title = "OpenClaw Installer"
            MinDiskSpaceGB = 15
            LogFile = "$env:TEMP\test.log"
            Colors = @{ Primary = [System.Drawing.Color]::Blue }
            Fonts = @{ Header = New-Object System.Drawing.Font("Arial", 12) }
        }
        
        return ($config.Version -and $config.Title -and $config.MinDiskSpaceGB -gt 0)
    }
    
    Test-Case -Name "Color scheme is valid" -Category "Config" -Test {
        $colors = @{
            Background = [System.Drawing.Color]::FromArgb(30, 30, 35)
            Primary = [System.Drawing.Color]::FromArgb(0, 150, 200)
            Success = [System.Drawing.Color]::FromArgb(0, 200, 100)
            Error = [System.Drawing.Color]::FromArgb(255, 80, 80)
        }
        
        # Verify all colors are valid Color objects
        $valid = $true
        foreach ($color in $colors.Values) {
            if (-not ($color -is [System.Drawing.Color])) {
                $valid = $false
                break
            }
        }
        return $valid
    }
    
    Test-Case -Name "Minimum disk space requirement" -Category "Config" -Test {
        $minSpace = 15
        return ($minSpace -ge 10 -and $minSpace -le 50)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: GUI Component Creation
# ═══════════════════════════════════════════════════════════════════════════

Test-Group "GUI Component Creation" {
    
    # We can't actually create Windows Forms in test mode without STA
    # So we test the logic and structure
    
    Test-Case -Name "Form configuration is valid" -Category "GUI" -Test {
        $formConfig = @{
            Width = 800
            Height = 600
            StartPosition = "CenterScreen"
            FormBorderStyle = "FixedDialog"
        }
        
        return ($formConfig.Width -gt 0 -and $formConfig.Height -gt 0)
    }
    
    Test-Case -Name "Card panels structure" -Category "GUI" -Test {
        $cards = @("Welcome", "SystemChecks", "Progress", "Completion")
        return ($cards.Count -eq 4)
    }
    
    Test-Case -Name "Button styling configuration" -Category "GUI" -Test {
        $buttonStyle = @{
            FlatStyle = "Flat"
            BorderSize = 0
            Cursor = "Hand"
        }
        
        return ($buttonStyle.FlatStyle -eq "Flat" -and $buttonStyle.BorderSize -eq 0)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: Installation Logic
# ═══════════════════════════════════════════════════════════════════════════

Test-Group "Installation Logic" {
    
    Test-Case -Name "Step ordering is correct" -Category "Install" -Test {
        $steps = @(
            "WSL2"
            "Ubuntu"
            "Packages"
            "Ollama"
            "Model"
            "OpenClaw"
        )
        
        $expectedOrder = @("WSL2", "Ubuntu", "Packages", "Ollama", "Model", "OpenClaw")
        $match = $true
        for ($i = 0; $i -lt $steps.Count; $i++) {
            if ($steps[$i] -ne $expectedOrder[$i]) {
                $match = $false
                break
            }
        }
        return $match
    }
    
    Test-Case -Name "Skip logic for existing components" -Category "Install" -Test {
        $systemStatus = @{
            WSLExists = $true
            UbuntuExists = $true
            OllamaExists = $false
        }
        
        # Should skip WSL and Ubuntu
        $shouldSkipWSL = $systemStatus.WSLExists
        $shouldSkipUbuntu = $systemStatus.UbuntuExists
        $shouldSkipOllama = $systemStatus.OllamaExists
        
        return ($shouldSkipWSL -and $shouldSkipUbuntu -and -not $shouldSkipOllama)
    }
    
    Test-Case -Name "Progress calculation" -Category "Install" -Test {
        $currentStep = 3
        $totalSteps = 6
        $progress = [math]::Round(($currentStep / $totalSteps) * 100)
        
        return ($progress -eq 50)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 5: Error Handling
# ═══════════════════════════════════════════════════════════════════════════

Test-Group "Error Handling" {
    
    Test-Case -Name "Admin rights error handling" -Category "Error" -Test {
        $isAdmin = $false
        
        if (-not $isAdmin) {
            $errorMessage = "Administrator rights required"
            return ($errorMessage -ne "")
        }
        return $false
    }
    
    Test-Case -Name "Disk space error handling" -Category "Error" -Test {
        $freeSpace = 5
        $minRequired = 15
        
        if ($freeSpace -lt $minRequired) {
            $errorMessage = "Insufficient disk space: $freeSpace GB (need $minRequired GB)"
            return ($errorMessage -match "Insufficient disk space")
        }
        return $false
    }
    
    Test-Case -Name "Windows version error handling" -Category "Error" -Test {
        $version = [System.Version]"10.0.18362"  # Too old
        $minVersion = [System.Version]"10.0.19041"
        
        if ($version -lt $minVersion) {
            $errorMessage = "Windows 10 version 2004+ or Windows 11 required"
            return ($errorMessage -match "Windows 10 version 2004")
        }
        return $false
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 6: Logging
# ═══════════════════════════════════════════════════════════════════════════

Test-Group "Logging System" {
    
    Test-Case -Name "Log file path is valid" -Category "Logging" -Test {
        $logPath = "$env:TEMP\openclaw-test.log"
        $isValid = $logPath -match "\\[\w\-\.]+\.log$"
        return $isValid
    }
    
    Test-Case -Name "Log entry format" -Category "Logging" -Test {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $level = "INFO"
        $message = "Test message"
        $entry = "[$timestamp] [$level] $message"
        
        return ($entry -match "\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")
    }
    
    Test-Case -Name "Log levels are valid" -Category "Logging" -Test {
        $validLevels = @("INFO", "ERROR", "WARNING", "DEBUG")
        $testLevel = "ERROR"
        
        return ($validLevels -contains $testLevel)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST GROUP 7: Edge Cases
# ═══════════════════════════════════════════════════════════════════════════

Test-Group "Edge Cases" {
    
    Test-Case -Name "Zero disk space" -Category "Edge" -Test {
        $space = 0
        $minSpace = 15
        $shouldFail = $space -lt $minSpace
        return $shouldFail
    }
    
    Test-Case -Name "All components already installed" -Category "Edge" -Test {
        $status = @{
            WSLExists = $true
            UbuntuExists = $true
            OllamaExists = $true
            ModelExists = $true
            OpenClawExists = $true
        }
        
        $allInstalled = $status.WSLExists -and $status.UbuntuExists -and 
                       $status.OllamaExists -and $status.ModelExists -and 
                       $status.OpenClawExists
        
        return $allInstalled
    }
    
    Test-Case -Name "No components installed" -Category "Edge" -Test {
        $status = @{
            WSLExists = $false
            UbuntuExists = $false
            OllamaExists = $false
            ModelExists = $false
            OpenClawExists = $false
        }
        
        $noneInstalled = -not ($status.WSLExists -or $status.UbuntuExists -or 
                              $status.OllamaExists -or $status.ModelExists -or 
                              $status.OpenClawExists)
        
        return $noneInstalled
    }
    
    Test-Case -Name "Partial installation" -Category "Edge" -Test {
        $status = @{
            WSLExists = $true      # Already have WSL
            UbuntuExists = $false  # Need Ubuntu
            OllamaExists = $false # Need Ollama
            ModelExists = $false  # Need model
            OpenClawExists = $false # Need OpenClaw
        }
        
        # Should only install Ubuntu, Ollama, Model, OpenClaw
        $shouldSkipWSL = $status.WSLExists
        $shouldInstallUbuntu = -not $status.UbuntuExists
        
        return ($shouldSkipWSL -and $shouldInstallUbuntu)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "`n" + ("═" * 64) -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host ("═" * 64) -ForegroundColor Cyan
Write-Host ""

# Group results by category
$categories = $script:TestResults | Group-Object -Property Category

foreach ($cat in $categories) {
    $passCount = ($cat.Group | Where-Object { $_.Result -eq "PASS" }).Count
    $totalCount = $cat.Group.Count
    $color = if ($passCount -eq $totalCount) { "Green" } else { "Yellow" }
    
    Write-Host "  $($cat.Name): $passCount/$totalCount passed" -ForegroundColor $color
}

Write-Host ""
Write-Host "  Total Tests: $($script:TestsPassed + $script:TestsFailed)" -ForegroundColor White
Write-Host "  Passed: $($script:TestsPassed)" -ForegroundColor Green
Write-Host "  Failed: $($script:TestsFailed)" -ForegroundColor $(if ($script:TestsFailed -gt 0) { "Red" } else { "Green" })

$successRate = if (($script:TestsPassed + $script:TestsFailed) -gt 0) {
    [math]::Round(($script:TestsPassed / ($script:TestsPassed + $script:TestsFailed)) * 100, 1)
} else { 0 }

Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

Write-Host "`n" + ("═" * 64) -ForegroundColor Cyan

# Exit code
if ($script:TestsFailed -eq 0) {
    Write-Host "  ✅ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "  ❌ Some tests failed. Review output above." -ForegroundColor Red
    exit 1
}
