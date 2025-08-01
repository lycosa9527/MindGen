# MindGen - AI-Powered Teaching Plan Generator

**Version:** v0.1.0  
**Status:** Production Ready  
**Primary Goal:** Help teachers create better teaching plans through collaborative AI assistance

## 🎯 Overview

MindGen is a production-ready application that uses multiple Large Language Models (Qwen, DeepSeek, and Personal ChatGPT Server) to collaboratively generate and iteratively improve teaching plans. The system employs a quality-driven approach where models cross-analyze each other's plans and refine them until quality thresholds are met.

## ✨ Key Features

- **Multi-Agent AI Collaboration**: Three LLMs work together to generate superior teaching plans
- **Iterative Improvement**: Cross-analysis and refinement until quality standards are achieved
- **Quality-Driven Process**: Automatic convergence when quality thresholds are met
- **Real-Time Monitoring**: Live progress tracking with detailed status updates
- **Modern Web Interface**: Professional, responsive UI with real-time updates
- **Comprehensive Error Handling**: Robust error management and fallback strategies
- **Performance Monitoring**: System resource tracking and performance metrics
- **Production-Grade Logging**: Structured logging with real-time WebSocket streaming

## 🏗️ Architecture

### Core Components

1. **Workflow Manager**: Coordinates the entire teaching plan improvement process
2. **Teaching Plan Agent**: Generates initial plans from three LLMs
3. **Cross-Analysis Agent**: Analyzes plans cross-model and generates feedback
4. **Improvement Agent**: Enhances plans based on analysis feedback
5. **Knowledge & Memory Agent**: Manages knowledge base queries and conversation memory

### Technology Stack

- **Backend**: Python 3.8+, Flask 3.0.0, Flask-SocketIO
- **AI Framework**: LangChain with agent-based architecture
- **LLM Integrations**: Qwen (Alibaba Cloud), DeepSeek, Personal ChatGPT Server
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Real-time Communication**: WebSocket (Socket.IO)
- **Configuration**: YAML-based with environment variable support
- **Data Models**: Pydantic for structured data validation

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for Qwen, DeepSeek, and Personal ChatGPT Server

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MindGen
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys:
   # - QWEN_API_KEY: Your Qwen API key
   # - DEEPSEEK_API_KEY: Your DeepSeek API key
   # - PERSONAL_CHATGPT_URL: Your Personal ChatGPT Server URL
   # - PERSONAL_CHATGPT_API_KEY: Your Personal ChatGPT Server API key
   # - FLASK_SECRET_KEY: A secure random string for Flask sessions
   ```

4. **Configure API keys**
   ```bash
   # Add your API keys to .env
   QWEN_API_KEY=your_qwen_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   PERSONAL_CHATGPT_URL=your_personal_chatgpt_server_url
   PERSONAL_CHATGPT_API_KEY=your_personal_chatgpt_api_key
   FLASK_SECRET_KEY=your_flask_secret_key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Start generating teaching plans!

## 📁 Project Structure

```
MindGen/
├── app.py                          # Main Flask application
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── env.example                     # Environment variables template
├── config/                         # Configuration files
│   ├── config_manager.py          # Configuration management
│   ├── system.yaml                # System configuration
│   └── models.yaml                # LLM configuration
├── services/                       # Core services
│   ├── workflow_manager.py        # Main workflow coordinator
│   ├── llm_service.py            # LangChain LLM integrations
│   ├── error_handler.py          # Error handling and retry logic
│   ├── performance_monitor.py    # System performance monitoring
│   ├── quality_metrics.py        # Quality assessment and metrics
│   ├── banner.py                 # Application banner display
│   └── agents/                   # LangChain agents
│       ├── __init__.py
│       ├── teaching_plan_agent.py
│       ├── cross_analysis_agent.py
│       ├── improvement_agent.py
│       └── knowledge_memory_agent.py
├── templates/                      # HTML templates
│   ├── index.html                 # Main application interface
│   ├── 404.html                   # 404 error page
│   └── 500.html                   # 500 error page
├── docs/                          # Documentation
│   ├── TECHNICAL_ARCHITECTURE.md  # Detailed architecture documentation
│   ├── CODE_REVIEW_REPORT.md      # Comprehensive code review
│   ├── VERSION_UPDATE_SUMMARY.md  # Version update documentation
│   └── logic_check.py             # Logic validation script
└── logs/                          # Application logs
    └── mindgen.log
```

## 🔧 Configuration

### System Configuration (`config/system.yaml`)

```yaml
system:
  max_iterations: 3
  quality_threshold: 0.8
  timeout_per_round: 300
  debug_mode: false

agents:
  teaching_plan:
    timeout: 60
    retry_attempts: 3
  cross_analysis:
    timeout: 90
    retry_attempts: 2
  improvement:
    timeout: 60
    retry_attempts: 3
  knowledge_memory:
    timeout: 30
    retry_attempts: 2
```

### Model Configuration (`config/models.yaml`)

```yaml
models:
  qwen:
    api_url: "https://api.qwen.ai/v1/chat/completions"
    api_key: "${QWEN_API_KEY}"
    model_name: "qwen-turbo"
    timeout: 45
  deepseek:
    api_url: "https://api.deepseek.com/v1/chat/completions"
    api_key: "${DEEPSEEK_API_KEY}"
    model_name: "deepseek-chat"
    timeout: 30
  personal_chatgpt:
    api_url: "${PERSONAL_CHATGPT_URL}"
    api_key: "${PERSONAL_CHATGPT_API_KEY}"
    model_name: "gpt-4o"
    timeout: 60
```

## 🔄 Workflow Process

1. **Teacher Input**: Teacher provides subject, grade, and learning objectives
2. **Initial Plan Generation**: Three LLMs generate initial teaching plans
3. **Cross-Analysis**: Each model analyzes the other two models' plans
4. **Quality Assessment**: Calculate overall quality score
5. **Iteration Decision**: If quality threshold not met, continue to step 6
6. **Plan Improvement**: Improve plans based on analysis feedback
7. **Loop Back**: Return to step 3 for next iteration
8. **Final Plan**: Generate final teaching plan when quality threshold is met

## 🎨 User Interface

The application features a modern, professional web interface with:

- **Clean Design**: Professional gradient background with card-based layout
- **Real-Time Updates**: Live progress tracking with animated progress bars
- **Status Updates**: Detailed status messages with icons and timestamps
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Interactive Elements**: Hover effects and smooth animations

## 📊 Monitoring and Debugging

### Health Check Endpoint
```bash
curl http://localhost:5000/health
```

### Status API
```bash
curl http://localhost:5000/api/status
```

### Configuration API
```bash
curl http://localhost:5000/api/config
```

### Debug Information
```bash
curl http://localhost:5000/api/debug/workflow_manager
```

### Test LLM Connections
```bash
curl -X POST http://localhost:5000/api/test-connection \
  -H "Content-Type: application/json" \
  -d '{"model": "all"}'
```

## 🔍 Quality Metrics

The system tracks multiple quality dimensions:

- **Curriculum Alignment**: How well the plan aligns with educational standards
- **Engagement Factor**: Student engagement and interactivity
- **Assessment Quality**: Effectiveness of assessment methods
- **Innovation Score**: Creativity and novel approaches
- **Practicality**: Feasibility and implementation ease

## 🛠️ Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Testing

```bash
pytest tests/
```

### Logging

Logs are stored in `logs/mindgen.log` with rotating file handler:
- Maximum file size: 10MB
- Backup count: 5 files
- Log level: INFO (configurable)
- Real-time WebSocket streaming

## 🚨 Error Handling

The application includes comprehensive error handling:

- **Retry Logic**: Exponential backoff for transient failures
- **Fallback Strategies**: Automatic model switching on failures
- **Circuit Breaker**: Prevents cascading failures
- **Graceful Degradation**: Continues operation with reduced functionality
- **Detailed Logging**: Comprehensive error tracking and debugging

## 🔒 Security Considerations

- **API Key Management**: Environment variable-based configuration
- **Input Validation**: Comprehensive input sanitization
- **Error Sanitization**: No sensitive data in error messages
- **Session Management**: Secure session handling
- **CORS Configuration**: Proper cross-origin resource sharing setup

## 📈 Performance

### Monitoring Features

- **CPU Usage**: Real-time CPU monitoring
- **Memory Usage**: Memory consumption tracking
- **Response Times**: Operation duration measurement
- **Error Rates**: Failure rate tracking
- **Throughput**: Operations per second

### Optimization

- **Async Operations**: Non-blocking background tasks
- **Connection Pooling**: Efficient API connection management
- **Caching**: Memory-based caching for repeated operations
- **Resource Management**: Automatic cleanup and garbage collection

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```bash
docker build -t mindgen .
docker run -p 5000:5000 mindgen
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Documentation**: See `TECHNICAL_ARCHITECTURE.md` for detailed architecture
- **Code Review**: See `CODE_REVIEW_REPORT.md` for comprehensive analysis
- **Issues**: Report bugs and feature requests via GitHub issues
- **Discussions**: Use GitHub discussions for general questions

## 🔮 Roadmap

### v0.2.0 (Planned)
- [ ] Enhanced knowledge base integration
- [ ] Advanced quality metrics
- [ ] Teacher feedback integration
- [ ] Plan export functionality

### v0.3.0 (Planned)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] API rate limiting
- [ ] Enhanced security features

---

**MindGen v0.1.0** - Empowering teachers with collaborative AI assistance for superior teaching plans. 