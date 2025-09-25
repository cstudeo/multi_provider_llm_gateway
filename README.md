# Multi-Provider LLM Interface with Distributed Rate Limiting

A production-ready system that provides a unified interface to multiple Large Language Model (LLM) providers with distributed rate limiting capabilities.

## Features

* **Multi-Provider Support**: Unified interface for OpenAI, Anthropic, and Google Gemini
* **Distributed Rate Limiting**: Redis-based rate limiting across multiple processes/servers
* **Automatic Failover**: Seamless switching between providers when one fails
* **REST API**: Clean Flask-based API with comprehensive endpoints
* **Health Monitoring**: Built-in health checks for all components
* **Scalable Architecture**: Stateless design for horizontal scaling

## Architecture

### Core Components

1. **LLM Interface Layer** (`llm_interface/`)
   * `BaseLLMClient`: Abstract base class for all providers
   * Provider-specific adapters: `OpenAIClient`, `AnthropicClient`, `GoogleClient`
   * Standardized request/response models

2. **Rate Limiting Layer** (`rate_limiter/`)
   * `DistributedRateLimiter`: Redis-based sliding window counter
   * Atomic operations using Lua scripts
   * Support for global and per-provider limits

3. **Service Layer** (`llm_service.py`)
   * `LLMService`: Orchestrates providers with rate limiting
   * Automatic failover between providers
   * Health monitoring and status reporting

4. **API Layer** (`app.py`)
   * Flask REST API with comprehensive endpoints
   * Error handling and rate limit responses
   * CORS support for web applications

5. **Frontend Layer** (`frontend/`)
   * React-based web interface
   * Real-time rate limit monitoring
   * Provider selection and configuration
   * Responsive design for all devices

## Prerequisites

* Python 3.8+
* Node.js 16+ (for React frontend)
* Redis server
* API keys for LLM providers:
  * OpenAI API key
  * Anthropic API key
  * Google AI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tapistro
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Start Redis server**
   ```bash
   # Using Docker (recommended)
   docker run -d --name redis -p 6379:6379 redis:alpine
   
   # Or install Redis locally
   # macOS: brew install redis && brew services start redis
   # Ubuntu: sudo apt install redis-server
   ```

## Configuration

Edit the `.env` file with your configuration:

```env
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Rate Limiting Configuration
GLOBAL_RATE_LIMIT=100
GLOBAL_WINDOW_SECONDS=60
OPENAI_RATE_LIMIT=50
ANTHROPIC_RATE_LIMIT=30
GOOGLE_RATE_LIMIT=20

# Flask Configuration
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

## Usage

### Development Mode

Run both backend and frontend in development mode:
```bash
python run_dev.py
```

This will start:
* Flask backend on http://localhost:5000
* React frontend on http://localhost:3000

### Production Mode

1. **Build the frontend:**
   ```bash
   python build_frontend.py
   ```

2. **Run the production server:**
   ```bash
   python main.py server
   ```

The web interface will be available at http://localhost:5000

### Command Line Interface

Test the service:
```bash
python main.py test
```

### Web Interface

The React frontend provides a modern, intuitive interface with:
* **Provider Selection**: Choose between OpenAI, Anthropic, and Google
* **Real-time Generation**: Generate text with live response display
* **Failover Support**: Automatic provider switching on failures
* **Rate Limit Monitoring**: Visual rate limit status and usage tracking
* **System Health**: Real-time health status of all components
* **Responsive Design**: Works on desktop and mobile devices

### REST API Endpoints

#### Health Check
```bash
GET /health
```

#### Get Available Providers
```bash
GET /providers
```

#### Generate Text
```bash
POST /generate
Content-Type: application/json

{
  "provider": "openai",
  "prompt": "Hello, world!",
  "user_id": "user123",
  "max_tokens": 100,
  "temperature": 0.7
}
```

#### Generate with Failover
```bash
POST /generate/failover
Content-Type: application/json

{
  "preferred_provider": "openai",
  "prompt": "Hello, world!",
  "user_id": "user123"
}
```

#### Get Rate Limit Status
```bash
GET /rate-limit/openai?user_id=user123
```

#### Reset Rate Limits (Admin)
```bash
POST /rate-limit/reset/openai
Content-Type: application/json

{
  "user_id": "user123"
}
```

### Python SDK Usage

```python
from llm_service import LLMService

# Initialize service
service = LLMService()

# Generate with specific provider
response = service.generate("openai", "Hello, world!")
print(response.content)

# Check rate limit status
status = service.get_rate_limit_status("openai", "user123")
print(status)
```

## Design Decisions

### Why Adapter Pattern for LLMs?
* **Flexibility**: Easy to add new providers without changing core logic
* **Consistency**: Unified interface across all providers
* **Maintainability**: Provider-specific code is isolated

### Why Redis for Rate Limiting?
* **Atomic Operations**: Lua scripts ensure consistency
* **Performance**: In-memory storage with sub-millisecond latency
* **Scalability**: Horizontal scaling with Redis Cluster
* **Persistence**: Optional persistence for rate limit data

### Why Sliding Window Counter?
* **Accuracy**: More precise than fixed window
* **Fairness**: Avoids burstiness at window edges
* **Simplicity**: Easier to implement than token bucket

### Architecture Benefits
* **Stateless Workers**: Easy horizontal scaling
* **Fault Tolerance**: Graceful degradation when Redis is unavailable
* **Provider Independence**: Each provider can be configured independently
* **Rate Limit Flexibility**: Global and per-provider limits

## Testing

The system includes comprehensive error handling and graceful degradation:

* **Provider Failures**: Automatic failover to healthy providers
* **Redis Unavailable**: Continues operation without rate limiting
* **Rate Limit Exceeded**: Clear error messages with status information
* **Invalid Requests**: Proper validation and error responses

## Scaling Considerations

### Horizontal Scaling
* Deploy multiple API server instances behind a load balancer
* Use Redis Cluster for distributed rate limiting
* Stateless design allows unlimited horizontal scaling

### Performance Optimization
* Redis connection pooling
* Provider connection reuse
* Response caching (can be added)

### Monitoring
* Health check endpoints for all components
* Rate limit status monitoring
* Provider performance metrics

## Security Considerations

* API keys stored in environment variables
* Rate limiting prevents abuse
* Input validation on all endpoints
* CORS configuration for web security

## Error Handling

The system handles various error scenarios:

* **Rate Limit Exceeded**: HTTP 429 with rate limit information
* **Provider Unavailable**: Automatic failover or clear error messages
* **Invalid Configuration**: Startup validation with helpful error messages
* **Redis Connection Issues**: Graceful degradation without rate limiting

## Future Enhancements

* **Caching Layer**: Response caching for improved performance
* **Metrics Collection**: Prometheus/Grafana integration
* **Authentication**: JWT-based authentication system
* **WebSocket Support**: Real-time streaming responses
* **Provider Load Balancing**: Intelligent provider selection
* **Cost Tracking**: Token usage and cost monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Built for production-ready LLM applications**
