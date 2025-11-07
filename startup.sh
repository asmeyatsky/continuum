#!/bin/bash

# ============================================================================
# 🚀 Infinite Concept Expansion Engine - Startup Script
# 
# This script sets up and runs the complete Infinite Concept Expansion Engine
# system, including dependencies, environment variables, and both API and 
# CLI modes of operation.
#
# Usage:
#   ./startup.sh [api|cli|dev] [llm_provider]
# 
# Examples:
#   ./startup.sh api openai           # Start API server with OpenAI
#   ./startup.sh cli anthropic        # Run CLI mode with Anthropic
#   ./startup.sh dev qwen             # Start dev mode with Qwen
#   ./startup.sh api                  # Start API with default (openai)
# ============================================================================

set -e  # Exit on any error

# Color codes for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN} $1 ${NC}"
    echo -e "${CYAN}================================${NC}"
}

# Default values
MODE="api"
LLM_PROVIDER="openai"
ENV_FILE=".env"
PYTHON_CMD="python3"
PIP_CMD="pip3"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies based on OS
install_dependencies() {
    print_header "Installing System Dependencies"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            print_status "Installing packages via Homebrew..."
            brew install python3 curl
        else
            print_error "Homebrew not found. Please install Homebrew first."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            print_status "Installing packages via apt-get..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv curl build-essential
        elif command_exists yum; then
            print_status "Installing packages via yum..."
            sudo yum install -y python3 python3-pip python3-devel curl gcc
        elif command_exists dnf; then
            print_status "Installing packages via dnf..."
            sudo dnf install -y python3 python3-pip python3-devel curl gcc
        else
            print_error "Unsupported package manager. Please install Python 3.9+ manually."
            exit 1
        fi
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Function to check Python version
check_python_version() {
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Installing..."
        install_dependencies
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 9 ]); then
        print_error "Python 3.9 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Python version: $PYTHON_VERSION (✓)"
}

# Function to create virtual environment
setup_virtual_env() {
    print_header "Setting up Virtual Environment"
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Upgrading pip..."
    $PIP_CMD install --upgrade pip setuptools wheel
}

# Function to install Python dependencies
install_python_dependencies() {
    print_header "Installing Python Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_status "Installing from requirements.txt..."
    $PIP_CMD install --break-system-packages -r requirements.txt
    
    print_status "Verifying critical dependencies..."
    for package in "fastapi" "uvicorn" "openai" "anthropic" "google-generativeai" "plotly" "networkx"; do
        if python3 -c "import $package" &>/dev/null; then
            print_status "$package ✓"
        else
            print_warning "$package not available (this may be expected if not using this LLM provider)"
        fi
    done
}

# Function to set up environment variables
setup_environment() {
    print_header "Setting up Environment Variables"
    
    # Check if .env file exists, if not create from example
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            print_status "Creating $ENV_FILE from .env.example..."
            cp .env.example $ENV_FILE
            print_warning "Created $ENV_FILE - please update your API keys before running!"
        else
            print_error "$ENV_FILE not found and no .env.example available!"
            exit 1
        fi
    fi
    
    # Load environment variables
    print_status "Loading environment variables from $ENV_FILE..."
    export $(grep -v '^#' $ENV_FILE | xargs)
    
    # Validate LLM provider
    if [[ ! "$LLM_PROVIDER" =~ ^(openai|anthropic|qwen|gemini|gemini-cli)$ ]]; then
        print_error "Invalid LLM provider: $LLM_PROVIDER"
        print_status "Supported providers: openai, anthropic, qwen, gemini, gemini-cli"
        exit 1
    fi
    
    # Set the LLM provider in environment
    export LLM_PROVIDER="$LLM_PROVIDER"
    
    # Check for required API keys based on provider
    case $LLM_PROVIDER in
        "openai")
            if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-api-key-here" ]; then
                print_warning "OPENAI_API_KEY not set or using default value in $ENV_FILE"
                print_warning "Please update OPENAI_API_KEY in $ENV_FILE to use OpenAI"
            fi
            ;;
        "anthropic")
            if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-your-api-key-here" ]; then
                print_warning "ANTHROPIC_API_KEY not set or using default value in $ENV_FILE"
                print_warning "Please update ANTHROPIC_API_KEY in $ENV_FILE to use Anthropic"
            fi
            ;;
        "qwen")
            if [ -z "$QWEN_API_KEY" ] || [ "$QWEN_API_KEY" = "your-qwen-api-key-here" ]; then
                print_warning "QWEN_API_KEY not set or using default value in $ENV_FILE"
                print_warning "Please update QWEN_API_KEY in $ENV_FILE to use Qwen"
            fi
            ;;
        "gemini")
            if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your-gemini-api-key-here" ]; then
                print_warning "GEMINI_API_KEY not set or using default value in $ENV_FILE"
                print_warning "Please update GEMINI_API_KEY in $ENV_FILE to use Google Gemini"
            fi
            ;;
    esac
    
    print_status "LLM Provider set to: $LLM_PROVIDER"
}

# Function to start the API server
start_api_server() {
    print_header "Starting API Server"
    
    print_status "API server will be available at http://localhost:${API_PORT:-8000}"
    print_status "API documentation at http://localhost:${API_PORT:-8000}/docs"
    print_status "Press Ctrl+C to stop the server"
    
    # Run the API server
    if [ -f "api/app.py" ]; then
        uvicorn api.app:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}
    elif [ -f "main.py" ]; then
        # If there's no dedicated API app, start the main app which probably has API capabilities
        $PYTHON_CMD main.py
    else
        print_error "No API entry point found!"
        exit 1
    fi
}

# Function to run CLI mode
run_cli_mode() {
    print_header "Running CLI Mode"
    
    print_status "Starting Infinite Concept Expansion Engine in CLI mode..."
    print_status "LLM Provider: $LLM_PROVIDER"
    print_status "Starting exploration of 'Artificial Intelligence' concept..."
    
    # Run the main application in CLI mode
    if [ -f "main.py" ]; then
        $PYTHON_CMD main.py
    else
        print_error "main.py not found!"
        exit 1
    fi
}

# Function to start in development mode
start_dev_mode() {
    print_header "Starting in Development Mode"
    
    print_status "Development mode includes:"
    print_status "- Auto-reload on file changes"
    print_status "- Detailed logging"
    print_status "- Both API and monitoring endpoints"
    
    # Set development environment
    export DEBUG=true
    export LOG_LEVEL=DEBUG
    
    print_status "Starting API server with auto-reload..."
    uvicorn api.app:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000} --reload
}

# Function to show usage information
show_usage() {
    echo "Usage: $0 [api|cli|dev] [llm_provider]"
    echo ""
    echo "Modes:"
    echo "  api          Start API server (default)"
    echo "  cli          Run CLI mode"
    echo "  dev          Start development mode with auto-reload"
    echo ""
    echo "LLM Providers:"
    echo "  openai       OpenAI GPT models (default)"
    echo "  anthropic    Anthropic Claude models"
    echo "  qwen         Alibaba Qwen models"
    echo "  gemini       Google Gemini models"
    echo "  gemini-cli   Google Gemini CLI models"
    echo ""
    echo "Examples:"
    echo "  $0 api openai     # Start API with OpenAI"
    echo "  $0 cli anthropic  # Run CLI with Anthropic"
    echo "  $0 dev qwen       # Start dev mode with Qwen"
    echo ""
    echo "Make sure to set your API keys in .env file before running!"
}

# Function to check if all services are ready
check_services() {
    print_header "Verifying System Health"
    
    # Check if required files exist
    REQUIRED_FILES=("requirements.txt" "main.py")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file $file not found!"
            exit 1
        fi
    done
    
    # Check if API file exists
    if [ "$MODE" = "api" ] || [ "$MODE" = "dev" ]; then
        if [ ! -f "api/app.py" ]; then
            print_warning "API entry point (api/app.py) not found"
        fi
    fi
    
    print_status "All required files present ✓"
    
    # Check if virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Virtual environment not activated - activating now"
        setup_virtual_env
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        api|cli|dev)
            MODE="$1"
            shift
            ;;
        openai|anthropic|qwen|gemini|gemini-cli)
            LLM_PROVIDER="$1"
            shift
            ;;
        *)
            print_error "Unknown argument: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
print_header "🚀 Infinite Concept Expansion Engine - Startup Script"

# Check Python version
check_python_version

# Setup virtual environment
setup_virtual_env

# Install dependencies
install_python_dependencies

# Setup environment variables
setup_environment

# Verify all services are ready
check_services

# Set LLM provider
export LLM_PROVIDER="$LLM_PROVIDER"
print_status "Using LLM provider: $LLM_PROVIDER"

# Execute based on mode
case $MODE in
    api)
        start_api_server
        ;;
    cli)
        run_cli_mode
        ;;
    dev)
        start_dev_mode
        ;;
    *)
        print_error "Invalid mode: $MODE"
        show_usage
        exit 1
        ;;
esac