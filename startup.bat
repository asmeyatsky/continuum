@echo off
REM ============================================================================
REM 🚀 Infinite Concept Expansion Engine - Windows Startup Script
REM 
REM This script sets up and runs the complete Infinite Concept Expansion Engine
REM system on Windows, including dependencies, environment variables, and both 
REM API and CLI modes of operation.
REM
REM Usage:
REM   startup.bat [api|cli|dev] [llm_provider]
REM 
REM Examples:
REM   startup.bat api openai           REM Start API server with OpenAI
REM   startup.bat cli anthropic        REM Run CLI mode with Anthropic
REM   startup.bat dev qwen             REM Start dev mode with Qwen
REM   startup.bat api                  REM Start API with default (openai)
REM ============================================================================

setlocal enabledelayedexpansion

REM Default values
set MODE=api
set LLM_PROVIDER=openai
set ENV_FILE=.env
set PYTHON_CMD=python
set PIP_CMD=pip

REM Function to print colored output
echo [INFO] Initializing Infinite Concept Expansion Engine...

REM Check if Python is installed
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://python.org
    exit /b 1
)

REM Check Python version
for /f "delims=" %%i in ('python --version 2^>^&1 ^| findstr /r "[0-9]*\.[0-9]*"') do set PYTHON_VERSION=%%i
for /f "tokens=2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MINOR=%%a
    goto :version_check
)
:version_check
if !PYTHON_MINOR! LSS 9 (
    echo [ERROR] Python 3.9 or higher is required. Current version: !PYTHON_VERSION!
    exit /b 1
)
echo [INFO] Python version: !PYTHON_VERSION! (✓)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)
echo [INFO] Virtual environment activated

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install Python dependencies
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    exit /b 1
)

echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Check if .env file exists, if not create from example
if not exist "%ENV_FILE%" (
    if exist ".env.example" (
        echo [INFO] Creating %ENV_FILE% from .env.example...
        copy .env.example %ENV_FILE%
        echo [WARN] Created %ENV_FILE% - please update your API keys before running!
    ) else (
        echo [ERROR] %ENV_FILE% not found and no .env.example available!
        exit /b 1
    )
)

REM Load environment variables from .env file
for /f "usebackq eol=# delims=" %%i in ("%ENV_FILE%") do (
    for /f "tokens=1,* delims==" %%a in ("%%i") do (
        set "%%a=%%b"
    )
)

REM Validate LLM provider
if /i not "%LLM_PROVIDER%"=="openai" (
if /i not "%LLM_PROVIDER%"=="anthropic" (
if /i not "%LLM_PROVIDER%"=="qwen" (
if /i not "%LLM_PROVIDER%"=="gemini" (
if /i not "%LLM_PROVIDER%"=="gemini-cli" (
    echo [ERROR] Invalid LLM provider: %LLM_PROVIDER%
    echo Supported providers: openai, anthropic, qwen, gemini, gemini-cli
    exit /b 1
)))))

REM Set the LLM provider in environment
set LLM_PROVIDER=%LLM_PROVIDER%
echo [INFO] LLM Provider set to: %LLM_PROVIDER%

REM Check for required API keys based on provider
if /i "%LLM_PROVIDER%"=="openai" (
    if "%OPENAI_API_KEY%"=="" (
        echo [WARN] OPENAI_API_KEY not set in %ENV_FILE%
        echo Please update OPENAI_API_KEY in %ENV_FILE% to use OpenAI
    )
    if "%OPENAI_API_KEY%"=="sk-your-api-key-here" (
        echo [WARN] Using default OPENAI_API_KEY value in %ENV_FILE%
        echo Please update OPENAI_API_KEY in %ENV_FILE% to use OpenAI
    )
)
if /i "%LLM_PROVIDER%"=="anthropic" (
    if "%ANTHROPIC_API_KEY%"=="" (
        echo [WARN] ANTHROPIC_API_KEY not set in %ENV_FILE%
        echo Please update ANTHROPIC_API_KEY in %ENV_FILE% to use Anthropic
    )
    if "%ANTHROPIC_API_KEY%"=="sk-ant-your-api-key-here" (
        echo [WARN] Using default ANTHROPIC_API_KEY value in %ENV_FILE%
        echo Please update ANTHROPIC_API_KEY in %ENV_FILE% to use Anthropic
    )
)
if /i "%LLM_PROVIDER%"=="qwen" (
    if "%QWEN_API_KEY%"=="" (
        echo [WARN] QWEN_API_KEY not set in %ENV_FILE%
        echo Please update QWEN_API_KEY in %ENV_FILE% to use Qwen
    )
    if "%QWEN_API_KEY%"=="your-qwen-api-key-here" (
        echo [WARN] Using default QWEN_API_KEY value in %ENV_FILE%
        echo Please update QWEN_API_KEY in %ENV_FILE% to use Qwen
    )
)
if /i "%LLM_PROVIDER%"=="gemini" (
    if "%GEMINI_API_KEY%"=="" (
        echo [WARN] GEMINI_API_KEY not set in %ENV_FILE%
        echo Please update GEMINI_API_KEY in %ENV_FILE% to use Google Gemini
    )
    if "%GEMINI_API_KEY%"=="your-gemini-api-key-here" (
        echo [WARN] Using default GEMINI_API_KEY value in %ENV_FILE%
        echo Please update GEMINI_API_KEY in %ENV_FILE% to use Google Gemini
    )
)

REM Parse command line arguments
:parse_args
if "%~1"=="" goto start_app
if /i "%~1"=="api" (
    set MODE=api
    shift
    goto parse_args
)
if /i "%~1"=="cli" (
    set MODE=cli
    shift
    goto parse_args
)
if /i "%~1"=="dev" (
    set MODE=dev
    shift
    goto parse_args
)
if /i "%~1"=="openai" (
    set LLM_PROVIDER=openai
    shift
    goto parse_args
)
if /i "%~1"=="anthropic" (
    set LLM_PROVIDER=anthropic
    shift
    goto parse_args
)
if /i "%~1"=="qwen" (
    set LLM_PROVIDER=qwen
    shift
    goto parse_args
)
if /i "%~1"=="gemini" (
    set LLM_PROVIDER=gemini
    shift
    goto parse_args
)
if /i "%~1"=="gemini-cli" (
    set LLM_PROVIDER=gemini-cli
    shift
    goto parse_args
)

REM Validate arguments
if /i not "%MODE%"=="api" (
if /i not "%MODE%"=="cli" (
if /i not "%MODE%"=="dev" (
    echo [ERROR] Invalid mode: %MODE%
    echo Usage: %~nx0 [api^|cli^|dev] [llm_provider]
    exit /b 1
)))

REM Verify required files
if not exist "main.py" (
    echo [ERROR] main.py not found!
    exit /b 1
)

if /i "%MODE%"=="api" (
if /i "%MODE%"=="dev" (
    if not exist "api\app.py" (
        echo [WARN] API entry point (api\app.py) not found
    )
))

echo [INFO] All required files present ✓

REM Set LLM provider
set LLM_PROVIDER=%LLM_PROVIDER%
echo [INFO] Using LLM provider: %LLM_PROVIDER%

REM Execute based on mode
if /i "%MODE%"=="api" goto start_api
if /i "%MODE%"=="cli" goto start_cli
if /i "%MODE%"=="dev" goto start_dev

goto :eof

:start_api
echo [INFO] Starting API Server
echo API server will be available at http://localhost:%API_PORT:8000%
echo API documentation at http://localhost:%API_PORT:8000%/docs
echo Press Ctrl+C to stop the server
if exist "api\app.py" (
    python -m api.app
) else (
    echo [ERROR] No API entry point found!
    exit /b 1
)
goto :eof

:start_cli
echo [INFO] Running CLI Mode
echo Starting Infinite Concept Expansion Engine in CLI mode...
echo LLM Provider: %LLM_PROVIDER%
echo Starting exploration of 'Artificial Intelligence' concept...
if exist "main.py" (
    python main.py
) else (
    echo [ERROR] main.py not found!
    exit /b 1
)
goto :eof

:start_dev
echo [INFO] Starting in Development Mode
echo Development mode includes:
echo - Auto-reload on file changes
echo - Detailed logging
echo - Both API and monitoring endpoints
set DEBUG=true
set LOG_LEVEL=DEBUG
echo [INFO] Starting API server with auto-reload...
uvicorn api.app:app --host %API_HOST:0.0.0.0% --port %API_PORT:8000% --reload
goto :eof