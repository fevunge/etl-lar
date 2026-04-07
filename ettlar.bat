@echo off
setlocal EnableDelayedExpansion

:: =============================================
:: ETL-LAR Control Script for Windows (CMD / .bat)
:: =============================================

:help
echo.
echo Usage:
echo   %~nx0 start     - Start the application: init DB + run ETL-LAR (CLI or Web)
echo   %~nx0 stop      - Stop the ETL-LAR services and remove containers
echo   %~nx0 run       - Run the ETL-LAR application in command line mode
echo   %~nx0 app       - Run the ETL-LAR application in web server mode
echo   %~nx0 database  - Initialize only the database container
echo   %~nx0 help      - Show this help message
echo.
exit /b 1

:verify_docker
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed. >&2
    exit /b 1
)
exit /b 0

:verify_docker_compose
where docker-compose >nul 2>&1
if %errorlevel% equ 0 exit /b 0

docker compose version >nul 2>&1
if %errorlevel% equ 0 exit /b 0

echo Error: docker-compose is not installed. >&2
exit /b 1

:verify_env
if exist .env (
    echo .env file found: Using environment variables from .env file.
) else (
    echo Error: .env file not found. >&2
    if exist .env.example (
        copy .env.example .env >nul
        echo A .env file has been created from .env.example.
        echo Please review and update the environment variables as needed. >&2
    ) else (
        echo Please create a .env file with the required environment variables. >&2
        echo SEE README.md for more details. >&2
        exit /b 1
    )
)
exit /b 0

:verify_python_packages
if not exist requirements.txt (
    echo No requirements.txt file found. Skipping Python package verification.
    exit /b 0
)

echo Checking for required Python packages...
for /f "usebackq delims=" %%p in ("requirements.txt") do (
    set "pkg=%%p"
    :: remove comments and empty lines
    echo !pkg! | findstr /r /c:"^ *#" /c:"^ *$" >nul && continue

    :: get only package name (remove version specifiers)
    for /f "tokens=1 delims=>=< " %%a in ("!pkg!") do set "clean_pkg=%%a"

    pip show !clean_pkg! >nul 2>&1
    if errorlevel 1 (
        echo Error: Required Python package '!clean_pkg!' is not installed. >&2
        echo Please install the required packages using: pip install -r requirements.txt >&2
        exit /b 1
    )
)
echo All required Python packages are installed.
exit /b 0

:database_init
call :verify_docker
if errorlevel 1 exit /b 1
call :verify_docker_compose
if errorlevel 1 exit /b 1

echo Initializing database container...
docker-compose up -d
if errorlevel 1 (
    echo Failed to start database container. >&2
    exit /b 1
)
echo Database container started successfully.
exit /b 0

:run_cli
call :verify_env
if errorlevel 1 exit /b 1
call :verify_python_packages
if errorlevel 1 exit /b 1

echo Running ETL-LAR application in command line mode...
python .\src\main.py
exit /b 0

:run_app
call :verify_env
if errorlevel 1 exit /b 1
call :verify_python_packages
if errorlevel 1 exit /b 1

echo Running ETL-LAR application in web server mode...
python -m streamlit run .\src\dashboard.py --server.port 8501
exit /b 0

:start_app
call :database_init
if errorlevel 1 exit /b 1

echo.
echo Choose application mode:
echo 1^) CLI application
echo 2^) WEB application
set /p choice="Enter your choice (default: WEB): "

if "%choice%"=="1" (
    call :run_cli
) else (
    call :run_app
)
exit /b 0

:stop_app
echo Stopping ETL-LAR application...
docker-compose down
if errorlevel 1 (
    echo Failed to stop ETL-LAR application. >&2
    exit /b 1
)
echo ETL-LAR application stopped successfully.
exit /b 0

:: ===================== MAIN =====================

if "%~1"=="" goto help

if /i "%~1"=="start"     ( call :start_app    & goto :eof )
if /i "%~1"=="stop"      ( call :stop_app     & goto :eof )
if /i "%~1"=="run"       ( call :run_cli      & goto :eof )
if /i "%~1"=="app"       ( call :run_app      & goto :eof )
if /i "%~1"=="database"  ( call :database_init & goto :eof )
if /i "%~1"=="help"      ( goto help )

echo Error: Invalid command '%~1' >&2
goto help