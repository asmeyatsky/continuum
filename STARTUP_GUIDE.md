# 🚀 Infinite Concept Expansion Engine - Startup Guide

This guide explains how to easily set up and run the Infinite Concept Expansion Engine using the provided startup scripts.

## 📋 Prerequisites

- **Python 3.9+** (for non-Docker setup)
- **Docker & Docker Compose** (for Docker setup)
- **API keys** for your chosen LLM provider (OpenAI, Anthropic, Qwen, or Google Gemini)

## 🚀 Quick Start Options

### Option 1: Simple Python Setup (Recommended for development)

1. **Make the script executable:**
   ```bash
   chmod +x startup.sh
   ```

2. **Run the startup script:**
   ```bash
   # For API mode with OpenAI
   ./startup.sh api openai
   
   # For CLI mode with Anthropic  
   ./startup.sh cli anthropic
   
   # For development mode with Qwen
   ./startup.sh dev qwen
   ```

### Option 2: Docker Setup (Recommended for production)

1. **Make the script executable:**
   ```bash
   chmod +x docker-startup.sh
   ```

2. **Run the Docker startup script:**
   ```bash
   # Start all services (API, database, cache, monitoring)
   ./docker-startup.sh up openai
   
   # View logs
   ./docker-startup.sh logs
   
   # Stop all services
   ./docker-startup.sh down
   ```

## 🔧 Configuration

### Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update the `.env` file with your API keys:**
   - For OpenAI: `OPENAI_API_KEY=your-openai-api-key`
   - For Anthropic: `ANTHROPIC_API_KEY=your-anthropic-api-key`
   - For Qwen: `QWEN_API_KEY=your-qwen-api-key`
   - For Google Gemini: `GEMINI_API_KEY=your-gemini-api-key`

### LLM Providers

The system supports multiple LLM providers:

- **openai**: OpenAI GPT models (default)
- **anthropic**: Anthropic Claude models
- **qwen**: Alibaba Qwen models
- **gemini**: Google Gemini models
- **gemini-cli**: Google Gemini CLI models

## 🛠️ Startup Script Options

### Basic Startup Script (`startup.sh`)

```bash
./startup.sh [mode] [llm_provider]
```

**Modes:**
- `api`: Start the API server (default)
- `cli`: Run CLI mode with interactive exploration
- `dev`: Start development mode with auto-reload

**Examples:**
```bash
# API mode with OpenAI (default)
./startup.sh api openai

# CLI mode with Anthropic
./startup.sh cli anthropic

# Development mode with Qwen
./startup.sh dev qwen
```

### Docker Startup Script (`docker-startup.sh`)

```bash
./docker-startup.sh [action] [llm_provider]
```

**Actions:**
- `up`: Start all services (default)
- `down`: Stop all services
- `logs`: View service logs
- `build`: Rebuild Docker images

**Examples:**
```bash
# Start all services with OpenAI
./docker-startup.sh up openai

# View logs
./docker-startup.sh logs

# Stop all services
./docker-startup.sh down

# Rebuild images
./docker-startup.sh build
```

## 🌐 Accessing the Application

### API Mode
- **API Endpoint**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Metrics**: `http://localhost:8000/metrics`

### Docker Services (when using docker-startup.sh)
- **API**: `http://localhost:8000`
- **Grafana Dashboard**: `http://localhost:3000` (admin/admin)
- **Jaeger Tracing**: `http://localhost:16686`
- **Prometheus**: `http://localhost:9090`

## 🔍 Available Endpoints (API Mode)

When running in API mode, the following endpoints are available:

- `POST /api/concepts/expand` - Submit a concept for expansion
- `POST /api/search` - Search the knowledge graph
- `GET /api/graph` - Get the knowledge graph
- `POST /api/feedback` - Submit feedback

Full API documentation is available at `http://localhost:8000/docs`

## 🧪 Testing the Installation

After starting the application, you can test it:

```bash
# Test the root endpoint
curl http://localhost:8000/

# Test concept expansion (replace 'artificial intelligence' with your concept)
curl -X POST "http://localhost:8000/api/concepts/expand" \
  -H "Content-Type: application/json" \
  -d '{"concept": "artificial intelligence", "context": "in education"}'
```

## 🛡️ Security Notes

- Keep your API keys secure and never commit them to version control
- The default Docker setup uses default passwords for Grafana (admin/admin) - change these in production
- In production, configure CORS settings appropriately

## 🐞 Troubleshooting

1. **If you get permission errors:**
   ```bash
   chmod +x startup.sh docker-startup.sh
   ```

2. **If dependencies fail to install:**
   - Ensure you have Python 3.9+ installed
   - Check that your internet connection is working
   - Try running `pip install --upgrade pip` first

3. **If the API doesn't start:**
   - Check that all required environment variables are set
   - Verify your API keys are valid
   - Look at the error messages for specific issues

4. **Docker issues:**
   - Ensure Docker and Docker Compose are properly installed
   - Check that Docker daemon is running
   - If you get port conflicts, check if other services are using ports 8000, 3000, 8080, etc.

## 📊 Features

The Infinite Concept Expansion Engine provides:

- 🧠 **Autonomous Research Generation**: Continuously expanding analysis with sources
- 📊 **Knowledge Graph Construction**: Interactive 3D visualizations
- 📈 **Trend Forecasting**: Pattern recognition and trend identification
- 🎨 **Educational Content Creation**: Complete multimedia courses
- 🔍 **Innovation Scouting**: Discover novel applications
- 🔄 **Continuous Learning**: Runs indefinitely, getting better over time
- 🧠 **Persistent Learning**: Improvements saved across sessions
- 🎨 **Stunning Visualizations**: 3D graphs and interactive dashboards

Enjoy exploring knowledge with the Infinite Concept Expansion Engine! 🌟