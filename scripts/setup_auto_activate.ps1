$ProfilePath = $PROFILE

if (-not (Test-Path $ProfilePath)) {
    New-Item -Path $ProfilePath -Type File -Force | Out-Null
    Write-Host "Created new PowerShell profile at $ProfilePath"
}

$FunctionDefinition = @'

function Set-VirtualEnv {
    if (Test-Path .venv\Scripts\Activate.ps1) {
        if ($env:VIRTUAL_ENV -ne (Resolve-Path .venv).Path) {
            Write-Host "Activating venv..." -ForegroundColor Green
            . .venv\Scripts\Activate.ps1
        }
    }
}

# Hook into cd (Set-Location)
function Set-Location {
    param(
        [Parameter(Position=0, ValueFromPipeline=$true)]
        [string]$Path,
        [switch]$PassThru
    )
    process {
        Microsoft.PowerShell.Management\Set-Location @PSBoundParameters
        Set-VirtualEnv
    }
}

# Run once on startup
Set-VirtualEnv
'@

if (Get-Content $ProfilePath | Select-String "Set-VirtualEnv") {
    Write-Host "Auto-activation already configured in profile." -ForegroundColor Yellow
} else {
    Add-Content -Path $ProfilePath -Value "`n$FunctionDefinition"
    Write-Host "Added auto-activation hook to $ProfilePath" -ForegroundColor Green
    Write-Host "Please restart your terminal or run: . `$PROFILE" -ForegroundColor Cyan
}
