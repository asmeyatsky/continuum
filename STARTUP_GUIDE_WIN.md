# 🚀 Infinite Concept Expansion Engine - Windows Startup Guide

This guide explains how to easily set up and run the Infinite Concept Expansion Engine on Windows using the provided startup script.

## 📋 Prerequisites

- **Python 3.9+** installed and added to PATH
- **API keys** for your chosen LLM provider (OpenAI, Anthropic, Qwen, or Google Gemini)
- **Visual C++ Build Tools** (for some dependencies)

## 🚀 Quick Start

### 1. Prepare Environment

1. **Install Python 3.9+** from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Verify Python installation:**
   ```cmd
   python --version
   ```

3. **Install required packages:**
   ```cmd
   python -m pip install --upgrade pip setuptools wheel
   ```

### 2. Configure Environment Variables

1. **Copy the example environment file:**
   ```cmd
   copy .env.example .env
   ```

2. **Update the `.env` file with your API keys:**
   - For OpenAI: `OPENAI_API_KEY=your-openai-api-key`
   - For Anthropic: `ANTHROPIC_API_KEY=your-anthropic-api-key`
   - For Qwen: `QWEN_API_KEY=your-qwen-api-key`
   - For Google Gemini: `GEMINI_API_KEY=your-gemini-api-key`

### 3. Run the Startup Script

Open Command Prompt or PowerShell and run:

```cmd
# For API mode with OpenAI (default)
startup.bat api openai

# For CLI mode with Anthropic
startup.bat cli anthropic

# For development mode with Qwen
startup.bat dev qwen
```

## 🔧 Configuration Options

### LLM Providers

The system supports multiple LLM providers:

- **openai**: OpenAI GPT models (default)
- **anthropic**: Anthropic Claude models
- **qwen**: Alibaba Qwen models
- **gemini**: Google Gemini models
- **gemini-cli**: Google Gemini CLI models

### Run Modes

- `api`: Start the API server (default)
- `cli`: Run CLI mode with interactive exploration
- `dev`: Start development mode with auto-reload

## 🌐 Accessing the Application

### API Mode
- **API Endpoint**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

## 🔍 Testing the Installation

After starting the application, you can test it:

```cmd
# Test the root endpoint
curl http://localhost:8000/

# Or using PowerShell
Invoke-RestMethod http://localhost:8000/
```

## 🛡️ Security Notes

- Keep your API keys secure and never commit them to version control
- In production, configure CORS settings appropriately

## 🐞 Troubleshooting

1. **If Python is not recognized:**
   - Ensure Python is installed and added to PATH
   - Restart Command Prompt after installing Python

2. **If dependencies fail to install:**
   - Make sure you have internet connection
   - Try running Command Prompt as Administrator
   - Install Visual C++ Build Tools if needed

3. **If the API doesn't start:**
   - Check that all required environment variables are set in `.env`
   - Verify your API keys are valid
   - Look at the error messages for specific issues

4. **Virtual environment issues:**
   - If venv creation fails, try: `python -m ensurepip --upgrade`

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