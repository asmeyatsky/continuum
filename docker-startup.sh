#!/bin/bash

# ============================================================================
# 🐳 Infinite Concept Expansion Engine - Docker Startup Script
# 
# This script starts the complete system using Docker Compose with all
# services (API, database, cache, monitoring).
#
# Usage:
#   ./docker-startup.sh [up|down|logs|build]
# 
# Examples:
#   ./docker-startup.sh up             # Start all services
#   ./docker-startup.sh up openai      # Start with OpenAI provider
#   ./docker-startup.sh down           # Stop all services
#   ./docker-startup.sh logs           # View service logs
#   ./docker-startup.sh build          # Rebuild images
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
ACTION="up"
LLM_PROVIDER="openai"
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if ! command_exists docker; then
        print_error "Docker is not installed or not in PATH"
        print_status "Please install Docker from https://docker.com"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        if ! command_exists docker compose; then
            print_error "Docker Compose is not installed"
            print_status "Please install Docker Compose"
            exit 1
        fi
        # Use 'docker compose' instead of 'docker-compose'
        DOCKER_COMPOSE_CMD="docker compose"
    else
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
    
    print_status "Docker ✓"
    print_status "Docker Compose ✓"
}

# Function to set up environment
setup_environment() {
    print_header "Setting up Environment"
    
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

# Function to start services
start_services() {
    print_header "Starting Docker Services"
    
    print_status "Building and starting services..."
    $DOCKER_COMPOSE_CMD up -d --build
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Show running services
    print_status "Running services:"
    $DOCKER_COMPOSE_CMD ps
    
    print_status "API will be available at http://localhost:8000"
    print_status "API documentation at http://localhost:8000/docs"
    print_status "Grafana dashboard at http://localhost:3000"
    print_status "Jaeger tracing at http://localhost:16686"
    print_status "Press Ctrl+C to stop all services"
}

# Function to stop services
stop_services() {
    print_header "Stopping Docker Services"
    
    if [ -f "$COMPOSE_FILE" ]; then
        print_status "Stopping all services..."
        $DOCKER_COMPOSE_CMD down
        print_status "All services stopped"
    else
        print_error "$COMPOSE_FILE not found!"
        exit 1
    fi
}

# Function to view logs
view_logs() {
    print_header "Viewing Docker Logs"
    
    if [ -f "$COMPOSE_FILE" ]; then
        print_status "Showing logs from all services..."
        $DOCKER_COMPOSE_CMD logs -f
    else
        print_error "$COMPOSE_FILE not found!"
        exit 1
    fi
}

# Function to rebuild images
rebuild_images() {
    print_header "Rebuilding Docker Images"
    
    if [ -f "$COMPOSE_FILE" ]; then
        print_status "Rebuilding all images..."
        $DOCKER_COMPOSE_CMD build --no-cache
        print_status "Rebuild complete"
    else
        print_error "$COMPOSE_FILE not found!"
        exit 1
    fi
}

# Function to show usage information
show_usage() {
    echo "Usage: $0 [up|down|logs|build] [llm_provider]"
    echo ""
    echo "Commands:"
    echo "  up             Start all services (default)"
    echo "  down           Stop all services"
    echo "  logs           View service logs"
    echo "  build          Rebuild Docker images"
    echo ""
    echo "LLM Providers:"
    echo "  openai         OpenAI GPT models (default)"
    echo "  anthropic      Anthropic Claude models"
    echo "  qwen           Alibaba Qwen models"
    echo "  gemini         Google Gemini models"
    echo "  gemini-cli     Google Gemini CLI models"
    echo ""
    echo "Examples:"
    echo "  $0 up openai       # Start all services with OpenAI"
    echo "  $0 up              # Start all services with default (openai)"
    echo "  $0 down            # Stop all services"
    echo "  $0 logs            # View all service logs"
    echo "  $0 build           # Rebuild Docker images"
    echo ""
    echo "Make sure to set your API keys in .env file before running!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        up|down|logs|build)
            ACTION="$1"
            shift
            ;;
        openai|anthropic|qwen|gemini|gemini-cli)
            LLM_PROVIDER="$1"
            shift
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
print_header "🐳 Infinite Concept Expansion Engine - Docker Startup"

# Check prerequisites
check_prerequisites

# Setup environment
setup_environment

# Execute based on action
case $ACTION in
    up)
        start_services
        ;;
    down)
        stop_services
        ;;
    logs)
        view_logs
        ;;
    build)
        rebuild_images
        ;;
    *)
        print_error "Invalid action: $ACTION"
        show_usage
        exit 1
        ;;
esac