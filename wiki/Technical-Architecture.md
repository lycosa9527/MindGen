# Technical Architecture

## 🏗️ **MindGen v0.1.0 Technical Architecture**

### **System Overview**

MindGen is a production-ready application designed to help teachers create superior teaching plans through iterative AI collaboration. The system uses three LLM APIs (Qwen, DeepSeek, and GPT-4o) that generate teaching plans, then cross-analyze and improve each other's plans through multiple rounds of refinement.

---

## 🎯 **Core Architecture Principles**

### **1. Multi-Agent Collaboration**
- **Teaching Plan Agent**: Generates initial plans from three LLMs
- **Cross-Analysis Agent**: Analyzes plans cross-model and generates feedback
- **Improvement Agent**: Enhances plans based on analysis feedback
- **Knowledge & Memory Agent**: Manages knowledge base queries and conversation memory

### **2. Quality-Driven Process**
- **Iterative Improvement**: Systematic refinement through cross-analysis
- **Quality Thresholds**: Automatic convergence when quality standards are met
- **Cross-Model Analysis**: Each model analyzes and critiques others' plans

### **3. Production-Ready Design**
- **Comprehensive Error Handling**: Robust error management and fallback strategies
- **Real-Time Monitoring**: Live progress tracking with detailed status updates
- **Production-Grade Logging**: Structured logging with real-time WebSocket streaming

---

## 🔄 **Workflow Process**

```mermaid
graph TD
    A[Teacher Input] --> B[Workflow Manager]
    B --> C[Teaching Plan Agent]
    
    C --> D[Qwen Plan Generator]
    C --> E[DeepSeek Plan Generator]
    C --> F[GPT-4o Plan Generator]
    
    D --> G[Initial Teaching Plans]
    E --> G
    F --> G
    
    G --> H[Cross-Analysis Agent]
    H --> I[Qwen Analyzes DeepSeek & GPT-4o]
    H --> J[DeepSeek Analyzes Qwen & GPT-4o]
    H --> K[GPT-4o Analyzes Qwen & DeepSeek]
    
    I --> L[Analysis Reports]
    J --> L
    K --> L
    
    L --> M{Quality Threshold Met?}
    M -->|No| N[Improvement Agent]
    M -->|Yes| O[Final Teaching Plan]
    
    N --> P[Qwen Improves Based on Feedback]
    N --> Q[DeepSeek Improves Based on Feedback]
    N --> R[GPT-4o Improves Based on Feedback]
    
    P --> S[Improved Plans]
    Q --> S
    R --> S
    
    S --> H
    
    subgraph Support Systems
        T[Knowledge & Memory Agent] --> C
        T --> H
        T --> N
        U[Configuration Manager] --> All Components
        V[Error Handler] --> All Components
        W[Progress Monitor] --> All Components
    end
```

---

## 🏛️ **System Components**

### **1. Workflow Manager**
- **Purpose**: Central orchestration of the teaching plan improvement process
- **Responsibilities**: 
  - Iteration control and quality assessment
  - State management and progress tracking
  - Error handling and recovery
  - Real-time status updates

### **2. Teaching Plan Agent**
- **Purpose**: Generates initial teaching plans using multiple LLMs
- **Process**:
  - Parallel generation from Qwen, DeepSeek, and GPT-4o
  - Structured output parsing with Pydantic models
  - Quality validation and error handling

### **3. Cross-Analysis Agent**
- **Purpose**: Performs cross-model analysis of teaching plans
- **Process**:
  - Each model analyzes plans from other models
  - Generates detailed feedback and improvement suggestions
  - Calculates quality metrics and scores

### **4. Improvement Agent**
- **Purpose**: Enhances teaching plans based on analysis feedback
- **Process**:
  - Extracts relevant feedback for each model
  - Generates improved versions of plans
  - Maintains plan structure and educational standards

### **5. Knowledge & Memory Agent**
- **Purpose**: Manages educational knowledge base and conversation memory
- **Features**:
  - Curriculum standards querying
  - Best practices retrieval
  - Conversation history management
  - Context preservation

---

## 🛠️ **Technology Stack**

### **Backend Framework**
- **Flask 3.0.0**: Modern web framework with excellent performance
- **Flask-SocketIO**: Real-time WebSocket communication
- **Flask-Session**: Secure session management

### **AI Framework**
- **LangChain**: Agent-based architecture for LLM interactions
- **LangChain Core**: Core functionality and utilities
- **LangChain Community**: Community integrations and tools
- **LangChain Experimental**: Experimental features and capabilities

### **LLM Integrations**
- **Qwen (Alibaba Cloud)**: Chinese language model with strong educational capabilities
- **DeepSeek**: Advanced reasoning and analysis capabilities
- **Personal ChatGPT Server**: OpenAI-compatible server for GPT-4o functionality

### **Data Management**
- **Pydantic**: Structured data validation and serialization
- **YAML**: Configuration management with environment variable support
- **JSON**: API communication and data exchange

### **Monitoring & Logging**
- **psutil**: System resource monitoring
- **RotatingFileHandler**: Production-grade log management
- **WebSocket Logging**: Real-time log streaming

---

## 📊 **Quality Metrics**

### **Assessment Dimensions**
- **Curriculum Alignment**: How well the plan aligns with educational standards
- **Engagement Factor**: Student engagement and interactivity
- **Assessment Quality**: Effectiveness of assessment methods
- **Innovation Score**: Creativity and novel approaches
- **Practicality**: Feasibility and implementation ease

### **Quality Calculation**
```python
def calculate_quality_score(analysis_reports):
    weights = {
        'curriculum_alignment': 0.25,
        'engagement_factor': 0.20,
        'assessment_quality': 0.20,
        'innovation_score': 0.15,
        'practicality': 0.20
    }
    
    total_score = 0
    for dimension, weight in weights.items():
        dimension_score = extract_dimension_score(analysis_reports, dimension)
        total_score += dimension_score * weight
    
    return total_score
```

---

## 🔒 **Security Architecture**

### **API Key Management**
- **Environment Variables**: Secure storage of sensitive credentials
- **Configuration Validation**: Automatic validation of required settings
- **Error Sanitization**: No sensitive data exposure in error messages

### **Input Validation**
- **Comprehensive Sanitization**: All user inputs validated and sanitized
- **Type Checking**: Pydantic models ensure data integrity
- **Boundary Validation**: Proper limits on input values

### **Session Management**
- **Secure Sessions**: Flask-Session with secure configuration
- **CORS Protection**: Proper cross-origin resource sharing setup
- **Error Handling**: Graceful error management without data leakage

---

## 📈 **Performance Architecture**

### **Monitoring Features**
- **CPU Usage**: Real-time CPU monitoring with psutil
- **Memory Usage**: Memory consumption tracking
- **Response Times**: Operation duration measurement
- **Error Rates**: Failure rate tracking and analysis
- **Throughput**: Operations per second monitoring

### **Optimization Strategies**
- **Async Operations**: Non-blocking background tasks
- **Connection Pooling**: Efficient API connection management
- **Caching**: Memory-based caching for repeated operations
- **Resource Management**: Automatic cleanup and garbage collection

---

## 🚀 **Deployment Architecture**

### **Production Deployment**
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t mindgen .
docker run -p 5000:5000 mindgen
```

### **Environment Configuration**
- **Development**: Flask development server with debug mode
- **Production**: Gunicorn with multiple workers
- **Container**: Docker with proper resource limits

---

## 🔧 **Configuration Management**

### **System Configuration (`config/system.yaml`)**
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

### **Model Configuration (`config/models.yaml`)**
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

---

## 📋 **API Endpoints**

### **Core Endpoints**
- `GET /` - Main application interface
- `POST /api/start` - Start teaching plan generation workflow
- `GET /api/status` - Get current system status
- `GET /api/config` - Get configuration (without sensitive data)
- `POST /api/test-connection` - Test LLM API connections
- `POST /api/reset` - Reset workflow state

### **Monitoring Endpoints**
- `GET /health` - Health check endpoint
- `GET /metrics` - System performance metrics
- `GET /api/debug/<component>` - Debug information for specific components

### **WebSocket Events**
- `connect` - Client connection handling
- `disconnect` - Client disconnection handling
- `request_status` - Status request from client
- `start_workflow` - Workflow start request via WebSocket
- `request_debug` - Debug request from client

---

## 🎯 **Architecture Benefits**

### **1. Scalability**
- **Modular Design**: Easy to extend and modify components
- **Agent-Based Architecture**: Independent agent development and testing
- **Configuration-Driven**: Flexible configuration without code changes

### **2. Reliability**
- **Comprehensive Error Handling**: Robust error management and recovery
- **Fallback Strategies**: Automatic model switching on failures
- **Circuit Breaker**: Prevents cascading failures

### **3. Maintainability**
- **Clean Separation of Concerns**: Clear component responsibilities
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Documentation**: Complete documentation for all components

### **4. Performance**
- **Real-Time Updates**: WebSocket-based live progress tracking
- **Optimized Operations**: Efficient API calls and data processing
- **Resource Monitoring**: Comprehensive system resource tracking

---

**MindGen v0.1.0** - Advanced AI-powered teaching plan generator with sophisticated multi-agent architecture.

---

*Last Updated: August 2025*  
*Version: v0.1.0 (Production Ready)* 