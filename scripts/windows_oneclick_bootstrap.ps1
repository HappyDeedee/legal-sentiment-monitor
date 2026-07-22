[CmdletBinding()]
param(
    [ValidateSet("Detached", "Foreground")]
    [string]$Mode = "Detached",
    [switch]$PreflightOnly
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$PinnedUvVersion = "0.11.30"
$RuntimeDirectory = Join-Path $ProjectRoot ".runtime\uv"
$ProjectUv = Join-Path $RuntimeDirectory "uv.exe"
$UvInstallerUrl = "https://astral.sh/uv/$PinnedUvVersion/install.ps1"

function Test-UvCommand {
    param([Parameter(Mandatory = $true)][string]$Candidate)

    try {
        & $Candidate --version *> $null
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        $syncHelp = (& $Candidate sync --help 2>$null) -join "`n"
        $runHelp = (& $Candidate run --help 2>$null) -join "`n"
        return $LASTEXITCODE -eq 0 -and $syncHelp.Contains("--locked") -and $runHelp.Contains("--no-sync")
    }
    catch {
        return $false
    }
}

function Get-InstallTimeoutSeconds {
    $raw = [string]$env:MONITOR_UV_INSTALL_TIMEOUT_SECONDS
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return 120
    }
    $parsed = 0
    if (-not [int]::TryParse($raw, [ref]$parsed) -or $parsed -lt 30 -or $parsed -gt 900) {
        throw "MONITOR_UV_INSTALL_TIMEOUT_SECONDS must be an integer from 30 to 900."
    }
    return $parsed
}

function Test-NoProxyHost {
    param([Parameter(Mandatory = $true)][string]$HostName)

    $raw = [string]$env:NO_PROXY
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $false
    }
    foreach ($entry in ($raw -split ",")) {
        $token = $entry.Trim()
        if ([string]::IsNullOrWhiteSpace($token)) {
            continue
        }
        if ($token -eq "*") {
            return $true
        }
        $token = $token.TrimStart("*").TrimStart(".")
        if ($token -match "://") {
            $parsedUri = $null
            if ([Uri]::TryCreate($token, [UriKind]::Absolute, [ref]$parsedUri)) {
                $token = $parsedUri.Host
            }
        }
        if ($token -match ":\d+$") {
            $token = $token.Substring(0, $token.LastIndexOf(":"))
        }
        if ($HostName -ieq $token -or $HostName.EndsWith("." + $token, [StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Get-InstallerProxy {
    if (Test-NoProxyHost "astral.sh") {
        return $null
    }
    foreach ($name in @("HTTPS_PROXY", "ALL_PROXY", "HTTP_PROXY")) {
        $raw = [string][Environment]::GetEnvironmentVariable($name, "Process")
        if ([string]::IsNullOrWhiteSpace($raw)) {
            continue
        }
        if ($raw -notmatch "^[a-zA-Z][a-zA-Z0-9+.-]*://") {
            $raw = "http://$raw"
        }
        $proxyUri = $null
        if (-not [Uri]::TryCreate($raw, [UriKind]::Absolute, [ref]$proxyUri)) {
            throw "The configured installer proxy is not a valid URI."
        }
        if ($proxyUri.Scheme -notin @("http", "https")) {
            throw "PowerShell 5.1 requires an HTTP or HTTPS installer proxy."
        }
        $credential = $null
        if (-not [string]::IsNullOrWhiteSpace($proxyUri.UserInfo)) {
            $separator = $proxyUri.UserInfo.IndexOf(":")
            if ($separator -ge 0) {
                $username = [Uri]::UnescapeDataString($proxyUri.UserInfo.Substring(0, $separator))
                $password = [Uri]::UnescapeDataString($proxyUri.UserInfo.Substring($separator + 1))
            }
            else {
                $username = [Uri]::UnescapeDataString($proxyUri.UserInfo)
                $password = ""
            }
            $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
            $credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $username, $securePassword
            $proxyBuilder = New-Object -TypeName System.UriBuilder -ArgumentList $proxyUri
            $proxyBuilder.UserName = ""
            $proxyBuilder.Password = ""
            $proxyUri = $proxyBuilder.Uri
        }
        return [pscustomobject]@{
            Uri = $proxyUri
            Credential = $credential
        }
    }
    return $null
}

function Add-ExecutableDirectoryToProcessPath {
    param([Parameter(Mandatory = $true)][string]$Executable)

    $executableDirectory = Split-Path -Parent $Executable
    if ([string]::IsNullOrWhiteSpace($executableDirectory)) {
        return
    }
    $remaining = @(([string]$env:Path -split ";") | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_) -and $_ -ine $executableDirectory
    })
    $env:Path = (@($executableDirectory) + $remaining) -join ";"
}

function Stop-OwnedProcessTree {
    param([Parameter(Mandatory = $true)]$Process)

    if ($Process.HasExited) {
        return
    }
    $taskkill = Join-Path $env:SystemRoot "System32\taskkill.exe"
    if (Test-Path -LiteralPath $taskkill -PathType Leaf) {
        & $taskkill /PID ([string]$Process.Id) /T /F *> $null
    }
    if (-not $Process.WaitForExit(10000)) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    }
}

function Install-ProjectUv {
    New-Item -ItemType Directory -Force -Path $RuntimeDirectory | Out-Null
    $installerPath = Join-Path ([IO.Path]::GetTempPath()) ("mediacrawler-uv-installer-" + [guid]::NewGuid().ToString("N") + ".ps1")
    $previousInstallDirectory = [Environment]::GetEnvironmentVariable("UV_UNMANAGED_INSTALL", "Process")
    $previousNoModifyPath = [Environment]::GetEnvironmentVariable("UV_NO_MODIFY_PATH", "Process")
    try {
        Write-Host "No compatible uv found. Installing project-local uv $PinnedUvVersion ..."
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        try {
            $downloadParameters = @{
                UseBasicParsing = $true
                Uri = $UvInstallerUrl
                OutFile = $installerPath
                TimeoutSec = (Get-InstallTimeoutSeconds)
            }
            $installerProxy = Get-InstallerProxy
            if ($null -ne $installerProxy) {
                $downloadParameters.Proxy = $installerProxy.Uri
                if ($null -ne $installerProxy.Credential) {
                    $downloadParameters.ProxyCredential = $installerProxy.Credential
                }
            }
            Invoke-WebRequest @downloadParameters
        }
        catch {
            throw "uv download failed. Check the network or proxy, then run the launcher again."
        }
        if (-not (Test-Path -LiteralPath $installerPath) -or (Get-Item -LiteralPath $installerPath).Length -eq 0) {
            throw "The downloaded uv installer is empty. Check the network and retry."
        }
        $env:UV_UNMANAGED_INSTALL = $RuntimeDirectory
        $env:UV_NO_MODIFY_PATH = "1"
        $currentPowerShell = (Get-Process -Id $PID).Path
        $installerArguments = '-NoLogo -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $installerPath.Replace('"', '""')
        $installerProcess = Start-Process -FilePath $currentPowerShell -ArgumentList $installerArguments -NoNewWindow -PassThru
        $installerTimeoutMilliseconds = (Get-InstallTimeoutSeconds) * 1000
        if (-not $installerProcess.WaitForExit($installerTimeoutMilliseconds)) {
            Stop-OwnedProcessTree -Process $installerProcess
            throw "Project-local uv installation timed out. Check the network or proxy and retry."
        }
        if ($installerProcess.ExitCode -ne 0 -and -not (Test-UvCommand $ProjectUv)) {
            throw "Project-local uv installation failed. Check the network or proxy and retry."
        }
    }
    finally {
        if ($null -eq $previousInstallDirectory) {
            Remove-Item Env:UV_UNMANAGED_INSTALL -ErrorAction SilentlyContinue
        }
        else {
            $env:UV_UNMANAGED_INSTALL = $previousInstallDirectory
        }
        if ($null -eq $previousNoModifyPath) {
            Remove-Item Env:UV_NO_MODIFY_PATH -ErrorAction SilentlyContinue
        }
        else {
            $env:UV_NO_MODIFY_PATH = $previousNoModifyPath
        }
        Remove-Item -LiteralPath $installerPath -Force -ErrorAction SilentlyContinue
    }
    if (-not (Test-Path -LiteralPath $ProjectUv) -or -not (Test-UvCommand $ProjectUv)) {
        throw "uv post-install verification failed. Check security software events and retry."
    }
    return $ProjectUv
}

function Resolve-UvCommand {
    $systemUvCandidates = @(Get-Command uv -CommandType Application -All -ErrorAction SilentlyContinue)
    foreach ($systemUv in $systemUvCandidates) {
        if ($systemUv.Source -ieq $ProjectUv) {
            continue
        }
        if (Test-UvCommand $systemUv.Source) {
            return $systemUv.Source
        }
    }
    if ((Test-Path -LiteralPath $ProjectUv) -and (Test-UvCommand $ProjectUv)) {
        return $ProjectUv
    }
    return Install-ProjectUv
}

function Invoke-UvStep {
    param(
        [Parameter(Mandatory = $true)][string]$UvCommand,
        [Parameter(Mandatory = $true)][string[]]$UvArguments,
        [Parameter(Mandatory = $true)][string]$FailureMessage
    )

    & $UvCommand @UvArguments
    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }
}

function Resolve-NodeCommand {
    param([Parameter(Mandatory = $true)][string]$UvCommand)

    $output = & $UvCommand @(
        "run", "--locked", "--no-sync", "python", "-m", "api.monitoring.windows_first_run",
        "--print-node-executable"
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js runtime resolution failed."
    }
    $lines = @($output | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    if ($lines.Count -eq 0) {
        throw "Node.js runtime resolution returned no executable."
    }
    $nodeCommand = [string]$lines[$lines.Count - 1]
    if (-not (Test-Path -LiteralPath $nodeCommand -PathType Leaf)) {
        throw "Node.js runtime verification failed."
    }
    return (Resolve-Path -LiteralPath $nodeCommand).Path
}

try {
    Set-Location -LiteralPath $ProjectRoot
    $bootstrapAdminPassword = [Environment]::GetEnvironmentVariable("MONITOR_ADMIN_PASSWORD", "Process")
    Remove-Item Env:MONITOR_ADMIN_PASSWORD -ErrorAction SilentlyContinue

    if ([string]::IsNullOrWhiteSpace([string]$env:MONITOR_HOST)) {
        $env:MONITOR_HOST = if ($Mode -eq "Foreground") { "127.0.0.1" } else { "0.0.0.0" }
    }
    if ([string]::IsNullOrWhiteSpace([string]$env:MONITOR_PORT)) {
        $env:MONITOR_PORT = "8080"
    }
    if ([string]::IsNullOrWhiteSpace([string]$env:MONITOR_BROWSER_URL) -and $Mode -eq "Foreground") {
        $env:MONITOR_BROWSER_URL = "http://127.0.0.1:$($env:MONITOR_PORT)/monitor"
    }
    if ([string]::IsNullOrWhiteSpace([string]$env:MONITOR_BROWSER_COOKIE_SYNC_ENABLED)) {
        $env:MONITOR_BROWSER_COOKIE_SYNC_ENABLED = "true"
    }
    if ([string]::IsNullOrWhiteSpace([string]$env:MONITOR_ALLOW_LOCAL_LOGIN_WINDOW)) {
        $env:MONITOR_ALLOW_LOCAL_LOGIN_WINDOW = "true"
    }
    if ([string]::IsNullOrWhiteSpace([string]$env:MONITOR_LOGIN_QR_HEADLESS)) {
        $env:MONITOR_LOGIN_QR_HEADLESS = "false"
    }

    Write-Host "[1/5] Checking project runtime..."
    $uv = Resolve-UvCommand
    Add-ExecutableDirectoryToProcessPath -Executable $uv
    & $uv --version
    if ($LASTEXITCODE -ne 0) {
        throw "uv runtime verification failed."
    }

    Write-Host "[2/5] Preparing Python 3.11 and locked dependencies..."
    Invoke-UvStep -UvCommand $uv -UvArguments @("sync", "--locked") -FailureMessage "Dependency sync failed. Check the network, proxy, and uv.lock consistency."
    $node = Resolve-NodeCommand -UvCommand $uv
    Add-ExecutableDirectoryToProcessPath -Executable $node
    & $node --version
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js runtime verification failed."
    }

    Write-Host "[3/5] Checking data storage, port, and administrator..."
    try {
        if ($null -ne $bootstrapAdminPassword) {
            $env:MONITOR_ADMIN_PASSWORD = $bootstrapAdminPassword
        }
        Invoke-UvStep -UvCommand $uv -UvArguments @(
            "run", "--locked", "--no-sync", "python", "-m", "api.monitoring.windows_first_run",
            "--host", [string]$env:MONITOR_HOST, "--port", [string]$env:MONITOR_PORT
        ) -FailureMessage "First-run preflight failed."
    }
    finally {
        Remove-Item Env:MONITOR_ADMIN_PASSWORD -ErrorAction SilentlyContinue
        $bootstrapAdminPassword = $null
    }

    Write-Host "[4/5] Checking the managed browser..."
    $launcherArguments = @(
        "run", "--locked", "--no-sync", "python", "-m", "api.monitoring.startup_launcher",
        "--host", [string]$env:MONITOR_HOST, "--port", [string]$env:MONITOR_PORT
    )
    if (-not [string]::IsNullOrWhiteSpace([string]$env:MONITOR_BROWSER_URL)) {
        $launcherArguments += @("--browser-url", [string]$env:MONITOR_BROWSER_URL)
    }
    if ($PreflightOnly) {
        $launcherArguments += "--browser-preflight-only"
    }
    elseif ($Mode -eq "Foreground") {
        $launcherArguments += "--foreground"
    }

    if (-not $PreflightOnly) {
        Write-Host "[5/5] Starting the monitor service..."
    }
    Invoke-UvStep -UvCommand $uv -UvArguments $launcherArguments -FailureMessage "Browser preparation or service startup failed."
    if ($PreflightOnly) {
        Write-Host "First-run preflight passed."
    }
}
catch {
    Write-Host ("Startup preparation failed: " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
