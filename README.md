# TextLayer Technical Interview

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

</div>

This repository contains a simplified version of the TextLayer Core template, specifically designed for technical interview purposes. It provides a foundation for demonstrating your skills in building AI applications with Flask and related technologies.

## 📋 Quick Start

### Using Make (Recommended)

The project includes a Makefile with helpful commands for setup and running:

```bash
# Initialize the project (creates venv, installs dependencies, sets up .env)
make init

# Start the Flask server
make start

# For help with available commands
make help
```

### Manual Setup

1. Clone the repository
2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   FLASK_APP=application.py python -m flask run
   ```
6. Access the application at http://127.0.0.1:5000

### Using Docker

You can also run the application in a Docker container:

```bash
# Build the Docker image
docker build -t textlayer-interview .

# Run the container
docker run -p 5000:5000 textlayer-interview
```

## ⚙️ Configuration

The application is configured through environment variables in the `.env` file. Key configuration variables include:

```
# Flask Configuration
FLASK_CONFIG=DEV

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
KNN_EMBEDDING_DIMENSION=1536

# Langfuse Configuration (for observability)
LANGFUSE_PUBLIC_KEY=pk-your-public-key-here
LANGFUSE_SECRET_KEY=sk-your-secret-key-here
LANGFUSE_HOST=https://cloud.langfuse.com
```

Make sure to update these values with your actual API keys before running the application.

## 🔍 Overview

TextLayer Core is a template for building AI applications. This interview version includes the core structure and essential integrations to demonstrate your ability to work with AI services, Flask, and modern Python application architecture.

## ✨ Features

- Flask application structure with modular organization
- Integration with LiteLLM for unified access to multiple LLM providers
- Langfuse integration for prompt management and observability
- Environment-based configuration management

## 🏛️ Architecture

### Application Flow

The TextLayer Core template implements a clean, modular architecture for AI applications:

1. **Request Handling**: 
   - Controllers receive and process incoming API requests
   - Validation through schema definitions

2. **Command Processing**:
   - Business logic is organized in command handlers
   - Separation of concerns with distinct command modules

3. **Service Integration**:
   - External services wrapped in service modules
   - Modular design for extensibility

4. **Response Handling**:
   - Structured API responses
   - Error handling with custom error types

### Langfuse Integration

[Langfuse](https://langfuse.com/docs) is integrated throughout the application to provide prompt management and observability:

1. **Prompt Management**:
   - Centralized storage and versioning of prompts
   - Prompt templates with variable substitution

2. **Observability with Trace Logging**:
   - Process flows create Langfuse traces
   - Key processing steps are tagged with observe markers

Example trace tags implementation:

```python
# use the @observe tag for logging traces
@observe()
def add_numbers(a: int, b: int) -> int:
    """
    Example function demonstrating Langfuse trace logging.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        Sum of the two numbers
    """
    return a + b
```

### LiteLLM Integration

The application uses [LiteLLM](https://docs.litellm.ai/) in the `services/llm` module to provide a unified interface for multiple LLM providers:

1. **Provider Agnostic Interface**:
   - Single interface to access multiple LLM providers (OpenAI, Anthropic, etc.)
   - Simplified model switching and fallback mechanisms
   - Standardized input/output formats

Example LiteLLM usage:

```python
from litellm import completion

response = completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Analyze this content..."}],
    temperature=0.7,
    max_tokens=2000
)
```

## 🚀 Interview Tasks

As part of the interview process, you may be asked to:

1. Extend the application with new features
2. Modify existing components
3. Debug issues in the codebase
4. Optimize performance
5. Implement best practices for security and scalability

## 📁 Project Structure

```
textlayer-interview/
├── app/                # Application package
│   ├── __init__.py     # App initialization
│   ├── commands/       # Command handlers
│   ├── controllers/    # API controllers
│   ├── models/         # Data models
│   └── services/       # External services integration
├── application.py      # Application entry point
├── config.py           # Configuration settings
├── requirements.txt    # Dependencies
├── Dockerfile          # Container definition
├── Makefile            # Build automation
└── .env.example        # Environment variable template
```

## 📝 Notes for Candidates

- Focus on demonstrating clean, maintainable code
- Show your understanding of Python best practices
- Consider edge cases and error handling
- Document your code appropriately
- Be prepared to explain your design decisions 