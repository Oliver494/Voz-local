$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$Runtime = Join-Path $ProjectRoot '.runtime'
$Uv = Join-Path $Runtime 'bin\uv.exe'
try {
    if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -eq 'ARM64') {
        throw 'This launcher requires Windows x64 / Este iniciador requiere Windows x64.'
    }
    if (-not (Test-Path -LiteralPath $Uv)) {
        Write-Host 'Preparing installer / Preparando instalador...'
        New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
        $env:UV_INSTALL_DIR = Join-Path $Runtime 'bin'
        $env:UV_NO_MODIFY_PATH = '1'
        $Download = Join-Path $Runtime 'uv-install.ps1'
        Invoke-WebRequest -UseBasicParsing -Uri 'https://astral.sh/uv/install.ps1' -OutFile $Download
        & $Download
        if (-not (Test-Path -LiteralPath $Uv)) { throw 'Could not install uv / No se pudo instalar uv.' }
    }
    if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
        Write-Host 'FFmpeg is missing. Installing with WinGet / Instalando FFmpeg...'
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            throw 'Install Microsoft App Installer (WinGet), then run this file again: https://learn.microsoft.com/windows/package-manager/winget/'
        }
        # Leave license and elevation prompts to the person running the installer.
        & winget install --id Gyan.FFmpeg --exact --source winget
        if ($LASTEXITCODE -ne 0) { throw 'FFmpeg installation failed or was cancelled / Instalacion cancelada o fallida.' }
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + $env:Path
        if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
            throw 'Close this window and run the .bat again to refresh PATH / Cierra esta ventana y abre el .bat otra vez.'
        }
    }
    $VcRuntime = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64' -ErrorAction SilentlyContinue
    if (-not $VcRuntime -or $VcRuntime.Installed -ne 1) {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            throw 'Install Microsoft App Installer (WinGet) for the Visual C++ runtime, then run again.'
        }
        Write-Host 'Installing Microsoft Visual C++ runtime for PyTorch / Preparando bibliotecas de Windows...'
        & winget install --id 'Microsoft.VCRedist.2015+.x64' --exact --source winget
        if ($LASTEXITCODE -ne 0) { throw 'Visual C++ runtime installation failed or needs a restart / Revisa la instalacion o reinicia Windows.' }
    }
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $Runtime 'python'
    $env:UV_PYTHON_PREFERENCE = 'only-managed'
    Write-Host 'Checking Python 3.12; it will be downloaded if missing / Preparando Python 3.12...'
    & $Uv python install 3.12
    if ($LASTEXITCODE -ne 0) { throw 'Python download failed / No se pudo descargar Python.' }
    & $Uv run --no-project --python 3.12 (Join-Path $PSScriptRoot 'setup.py') --uv $Uv
    exit $LASTEXITCODE
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
