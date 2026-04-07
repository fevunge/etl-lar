# ETL-LAR Control Script - PowerShell version

function Show-Help {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host " .\etl-lar.ps1 start  - Start the application: init the database container, run the ETL-LAR application, and start the web server."
    Write-Host " .\etl-lar.ps1 stop   - Stop the ETL-LAR services and remove containers."
    Write-Host " .\etl-lar.ps1 run    - Run the ETL-LAR application in command line mode."
    Write-Host " .\etl-lar.ps1 app    - Run the ETL-LAR application in web server mode."
    Write-Host " .\etl-lar.ps1 help   - Display this help message"
    Write-Host " .\etl-lar.ps1 database - Initialize only the database container"
    exit 1
}

function Test-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Error: Docker is not installed."
        return $false
    }
    return $true
}

function Test-DockerCompose {
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue) -and 
        -not (Get-Command "docker" -ErrorAction SilentlyContinue) -or 
        -not (& docker compose version -ErrorAction SilentlyContinue)) {
        
        Write-Error "Error: docker-compose is not installed."
        return $false
    }
    return $true
}

function Test-EnvFile {
    if (Test-Path .env) {
        Write-Host ".env file found: Using environment variables from .env file." -ForegroundColor Green
        # No need to source in PowerShell, .env is usually read by docker-compose or python-dotenv
    }
    else {
        Write-Error ".env file not found."
        if (Test-Path .env.example) {
            Copy-Item .env.example .env
            Write-Host "A .env file has been created from .env.example. Please review and update the environment variables as needed." -ForegroundColor Yellow
        }
        else {
            Write-Error "Please create a .env file with the required environment variables."
            Write-Error "SEE README.md for more details."
            return $false
        }
    }
    return $true
}

function Test-PythonPackages {
    if (-not (Test-Path requirements.txt)) {
        Write-Host "No requirements.txt file found. Skipping Python package verification." -ForegroundColor Yellow
        return $true
    }

    Write-Host "Checking for required Python packages..." -ForegroundColor Cyan

    $packages = Get-Content requirements.txt | Where-Object { $_ -notmatch '^\s*#' -and $_ -ne '' }

    foreach ($package in $packages) {
        $pkg = $package.Trim().Split('=')[0].Split('>')[0].Split('<')[0].Trim()
        if (-not (pip show $pkg 2>$null)) {
            Write-Error "Required Python package '$pkg' is not installed."
            Write-Host "Please install the required packages using: pip install -r requirements.txt" -ForegroundColor Yellow
            return $false
        }
    }

    Write-Host "All required Python packages are installed." -ForegroundColor Green
    return $true
}

function Initialize-Database {
    if (-not (Test-Docker) -or -not (Test-DockerCompose)) {
        exit 1
    }

    Write-Host "Initializing database container..." -ForegroundColor Cyan
    try {
        docker-compose up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Database container started successfully." -ForegroundColor Green
        }
        else {
            throw "Failed to start database container."
        }
    }
    catch {
        Write-Error "Failed to start database container."
        exit 1
    }
}

function Invoke-Run {
    if (-not (Test-EnvFile)) { exit 1 }
    if (-not (Test-PythonPackages)) { exit 1 }

    Write-Host "Running ETL-LAR application in command line mode..." -ForegroundColor Cyan
    python ./src/main.py
}

function Invoke-App {
    if (-not (Test-EnvFile)) { exit 1 }
    if (-not (Test-PythonPackages)) { exit 1 }

    Write-Host "Running ETL-LAR application in web server mode..." -ForegroundColor Cyan
    python -m streamlit run ./src/dashboard.py --server.port 8501
}

function Start-Application {
    Initialize-Database

    Write-Host "`nChoose application mode:" -ForegroundColor Cyan
    Write-Host "1) CLI application"
    Write-Host "2) WEB application"
    $choice = Read-Host "Enter your choice (default: WEB)"

    switch ($choice) {
        "1" { Invoke-Run }
        "2" { Invoke-App }
        default { Invoke-App }
    }
}

function Stop-Application {
    Write-Host "Stopping ETL-LAR application..." -ForegroundColor Cyan
    try {
        docker-compose down
        if ($LASTEXITCODE -eq 0) {
            Write-Host "ETL-LAR application stopped successfully." -ForegroundColor Green
        }
        else {
            throw "Failed to stop application."
        }
    }
    catch {
        Write-Error "Failed to stop ETL-LAR application."
        exit 1
    }
}

# ===================== MAIN =====================

if (-not $args) {
    Show-Help
}

switch ($args[0].ToLower()) {
    "start"     { Start-Application }
    "stop"      { Stop-Application }
    "run"       { Invoke-Run }
    "app"       { Invoke-App }
    "help"      { Show-Help }
    "database"  { Initialize-Database }
    default {
        Write-Error "Error: Invalid command '$($args[0])'"
        Show-Help
    }
}