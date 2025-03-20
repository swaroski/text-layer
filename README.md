# TextLayer Core

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

</div>

A Flask application template for building AI applications with TextLayer. This template provides core resources and structure for creating robust AI-powered services.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
  - [Application Flow](#application-flow)
  - [Langfuse Integration](#langfuse-integration)
  - [LiteLLM Integration](#litellm-integration)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🔍 Overview

TextLayer Core is a template for building AI applications. It provides a structured foundation with built-in integrations for AI services, search capabilities, and observability. The template is designed to be extended with additional integrations based on specific project requirements.

## ✨ Features

- Flask application structure with modular organization
- Integration with LiteLLM for unified access to multiple LLM providers
- Search capabilities with Elasticsearch/OpenSearch
- AWS integration for cloud deployment
- Langfuse integration for prompt management and observability
- Containerized deployment via Docker
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
   - A/B testing of different prompt variants
   - Prompt templates with variable substitution
   - Prompt performance analytics

2. **Observability with Trace Logging**:
   - Process flows create Langfuse traces
   - Key processing steps are tagged with observe markers
   - Spans capture duration and metadata for performance analysis
   - Scores and feedback can be logged for quality assessment

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

The trace logging enables detailed analytics on:
- End-to-end processing time
- LLM response latency
- Error rates and types
- Prompt effectiveness
- User feedback correlation

For more information on Langfuse integration, see the [Langfuse Documentation](https://langfuse.com/docs/sdk/python).

### LiteLLM Integration

The application uses [LiteLLM](https://docs.litellm.ai/) in the `services/llm` module to provide a unified interface for multiple LLM providers:

1. **Provider Agnostic Interface**:
   - Single interface to access multiple LLM providers (OpenAI, Anthropic, etc.)
   - Simplified model switching and fallback mechanisms
   - Standardized input/output formats

2. **Features Utilized**:
   - Model routing
   - Cost tracking and budget management
   - Caching and rate limiting
   - Automatic retries and error handling

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

LiteLLM allows the application to easily switch between different LLM providers without changing the codebase, enabling model experimentation and fallback strategies.

For more information on LiteLLM integration, see the [LiteLLM Documentation](https://docs.litellm.ai/).

## 📋 Prerequisites

- Python 3.9
- [Docker](https://docs.docker.com/engine/install/) (for building and testing the container)
- [Doppler](https://dashboard.doppler.com/register) account & [Doppler CLI](https://docs.doppler.com/docs/install-cli) (recommended for secrets management)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) (if deploying to AWS)
- Access to LLM providers (OpenAI, Anthropic, etc.)
- Langfuse account for prompt management and observability

## 🚀 Installation

### Local Development

1. Clone the repository

```bash
git clone https://github.com/TextLayer/textlayer-core.git
cd textlayer-core
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables

```bash
cp .env.example .env  # Create from example if available
# Edit .env with your configuration
```

### Using `uv` for Dependency Management

This project supports the use of the `uv` Python package manager for managing dependencies:

- Install `uv` globally using `pipx`:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install pipx
   pipx install uv
   ```

- Install dependencies using `uv`:

   ```bash
   # Install all dependencies including dev dependencies
   # This will install the dependencies on your system which should be the dev container
   # -e flag installs the package in editable mode which is useful for development
   uv pip install -e .[dev] --system

   # Install only production dependencies
   uv pip install . --system --no-cache-dir
   ```

### Development with Docker

You can also use Docker for local development (recommended):

```bash
# Build and run the development Docker container
docker build -t textlayer-core -f Dockerfile .
docker run -p 5000:5000 textlayer-core
```

## ⚙️ Configuration

The application is configured through environment variables. Key configuration variables include:

| Category | Environment Variables | Description |
|----------|----------------------|-------------|
| **Flask** | `FLASK_CONFIG` | Environment configuration (DEV, TEST, STAGING, PROD) |
| **AWS** | `ACCESS_KEY_ID`, `SECRET_ACCESS_KEY`, `REGION` | AWS credentials and region |
| **Elasticsearch** | `ELASTICSEARCH_URL`, `ELASTICSEARCH_USER`, `ELASTICSEARCH_PASSWORD` | Elasticsearch connection details |
| **Langfuse** | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` | Langfuse API configuration |
| **LLM** | `LLM_API_KEY` | Generic API key for LLM providers |

For secrets management, Doppler is recommended:

1. Make a [Doppler](https://doppler.com) account
2. Download the [Doppler CLI](https://docs.doppler.com/docs/install-cli)
3. Run `doppler login`
4. Run `doppler setup` and select your environment
5. Start the application with automated secrets injection: `doppler run -- flask run`

## 📝 Usage

### Running Locally

```bash
# With regular environment variables
flask run

# Or with Doppler (recommended)
doppler run -- flask run
```

### CLI Commands

The application provides CLI commands for maintenance and testing:

```bash
# Run tests
flask test

# Run tests with coverage
flask test --coverage
```

## 🚢 Deployment

This template supports deployment as a containerized application.

### Building the Docker Image

```bash
docker build -t textlayer-app -f Dockerfile .
```

### Deploying to AWS

For AWS deployment, the template includes support for:
- Amazon ECR for container registry
- AWS Lambda for serverless deployment
- Amazon ECS for container orchestration

Specific deployment instructions depend on your chosen AWS service.

## 📁 Project Structure

```
textlayer-core/
├── app/                        # Main application code
│   ├── commands/               # Command handlers for business logic
│   ├── controllers/            # Request controllers
│   ├── core/                   # Core application functionality
│   ├── errors/                 # Error handling
│   ├── middlewares/            # HTTP middleware
│   ├── routes/                 # API route definitions
│   ├── schemas/                # Data validation schemas
│   ├── services/               # External service integrations
│   │   ├── aws/                # AWS integration
│   │   ├── email/              # Email service
│   │   ├── llm/                # LiteLLM integration
│   │   └── search/             # Search service integration
│   ├── utils/                  # Utility functions
│   ├── aws_triggers/           # AWS Lambda triggers
│   ├── cli/                    # Command-line interface tools
│   ├── decorators.py           # Decorators
│   ├── extensions.py           # Flask extensions
│   ├── log.py                  # Logging configuration
│   └── __init__.py             # Application initialization
├── application.py              # Application entry point
├── config.py                   # Configuration management
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore file
└── README.md                   # This documentation
```

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 