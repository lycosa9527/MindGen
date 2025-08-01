# API Documentation

## 📋 **MindGen v0.1.0 API Reference**

This document provides comprehensive API documentation for the MindGen application.

---

## 🚀 **Base URL**

```
http://localhost:5000
```

---

## 📊 **Core Endpoints**

### **1. Main Application Interface**

**GET /**  
Returns the main application interface.

**Response:** HTML page with the MindGen web interface.

**Example:**
```bash
curl http://localhost:5000/
```

---

### **2. Start Workflow**

**POST /api/start**  
Initiates the teaching plan generation workflow.

**Request Body:**
```json
{
  "subject": "Mathematics",
  "grade": "Grade 8",
  "objectives": "Students will learn about linear equations and their applications",
  "max_rounds": 3
}
```

**Response:**
```json
{
  "status": "started",
  "max_rounds": 3,
  "message": "Teaching plan generation started"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "grade": "Grade 8",
    "objectives": "Students will learn about linear equations and their applications",
    "max_rounds": 3
  }'
```

---

### **3. Get System Status**

**GET /api/status**  
Returns the current system status and workflow information.

**Response:**
```json
{
  "workflow_status": {
    "is_running": false,
    "current_iteration": 0,
    "max_iterations": 3,
    "quality_score": 0.0,
    "status": "idle"
  },
  "performance": {
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "response_times": {
      "average": 2.3,
      "min": 0.5,
      "max": 8.1
    },
    "error_rates": {
      "total_requests": 150,
      "failed_requests": 2,
      "success_rate": 98.7
    }
  },
  "health": {
    "status": "healthy",
    "timestamp": 1640995200
  },
  "timestamp": 1640995200
}
```

**Example:**
```bash
curl http://localhost:5000/api/status
```

---

### **4. Get Configuration**

**GET /api/config**  
Returns system configuration (without sensitive data).

**Response:**
```json
{
  "system": {
    "max_iterations": 3,
    "quality_threshold": 0.8,
    "timeout_per_round": 300,
    "debug_mode": false
  },
  "agents": {
    "teaching_plan": {
      "timeout": 60,
      "retry_attempts": 3
    },
    "cross_analysis": {
      "timeout": 90,
      "retry_attempts": 2
    },
    "improvement": {
      "timeout": 60,
      "retry_attempts": 3
    },
    "knowledge_memory": {
      "timeout": 30,
      "retry_attempts": 2
    }
  },
  "models": {
    "qwen": {
      "api_url": "https://api.qwen.ai/v1/chat/completions",
      "api_key": "***",
      "model_name": "qwen-turbo",
      "timeout": 45
    },
    "deepseek": {
      "api_url": "https://api.deepseek.com/v1/chat/completions",
      "api_key": "***",
      "model_name": "deepseek-chat",
      "timeout": 30
    },
    "personal_chatgpt": {
      "api_url": "***",
      "api_key": "***",
      "model_name": "gpt-4o",
      "timeout": 60
    }
  },
  "flask": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mindgen.log",
    "max_size": "10MB",
    "backup_count": 5
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/config
```

---

### **5. Test LLM Connections**

**POST /api/test-connection**  
Tests the connection to LLM APIs.

**Request Body:**
```json
{
  "model": "all"
}
```

**Response:**
```json
{
  "qwen": {
    "status": "success",
    "response_time": 1.2,
    "message": "Connection successful"
  },
  "deepseek": {
    "status": "success",
    "response_time": 0.8,
    "message": "Connection successful"
  },
  "personal_chatgpt": {
    "status": "success",
    "response_time": 1.5,
    "message": "Connection successful"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/test-connection \
  -H "Content-Type: application/json" \
  -d '{"model": "all"}'
```

---

### **6. Reset Workflow**

**POST /api/reset**  
Resets the workflow state and clears all data.

**Response:**
```json
{
  "status": "success",
  "message": "Workflow reset successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/reset
```

---

## 📈 **Monitoring Endpoints**

### **1. Health Check**

**GET /health**  
Returns the health status of the application.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200,
  "version": "v0.1.0",
  "health": {
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "uptime": 3600
  }
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### **2. Performance Metrics**

**GET /metrics**  
Returns detailed performance metrics.

**Response:**
```json
{
  "cpu_usage": 15.2,
  "memory_usage": 45.8,
  "response_times": {
    "average": 2.3,
    "min": 0.5,
    "max": 8.1,
    "p95": 4.2,
    "p99": 6.8
  },
  "error_rates": {
    "total_requests": 150,
    "failed_requests": 2,
    "success_rate": 98.7,
    "error_rate": 1.3
  },
  "throughput": {
    "requests_per_second": 12.5,
    "operations_per_second": 8.2
  },
  "timestamp": 1640995200
}
```

**Example:**
```bash
curl http://localhost:5000/metrics
```

---

### **3. Debug Information**

**GET /api/debug/<component>**  
Returns debug information for a specific component.

**Components:**
- `workflow_manager`
- `teaching_plan_agent`
- `cross_analysis_agent`
- `improvement_agent`
- `knowledge_memory_agent`
- `system`

**Response:**
```json
{
  "component": "workflow_manager",
  "status": "idle",
  "current_iteration": 0,
  "max_iterations": 3,
  "quality_score": 0.0,
  "debug_data": {
    "teaching_plan_agent": [],
    "cross_analysis_agent": [],
    "improvement_agent": [],
    "knowledge_memory_agent": []
  },
  "timestamp": 1640995200
}
```

**Example:**
```bash
curl http://localhost:5000/api/debug/workflow_manager
```

---

## 🔌 **WebSocket Events**

### **Connection Events**

**Event: `connect`**  
Emitted when a client connects to the WebSocket.

**Event: `disconnect`**  
Emitted when a client disconnects from the WebSocket.

### **Client Events**

**Event: `request_status`**  
Request current system status.

**Event: `start_workflow`**  
Start the teaching plan generation workflow via WebSocket.

**Request:**
```json
{
  "subject": "Mathematics",
  "grade": "Grade 8",
  "objectives": "Students will learn about linear equations and their applications",
  "max_rounds": 3
}
```

**Event: `request_debug`**  
Request debug information for a specific component.

**Request:**
```json
{
  "component": "workflow_manager"
}
```

### **Server Events**

**Event: `status`**  
General status updates.

**Event: `status_update`**  
Detailed status updates.

**Event: `workflow_started`**  
Confirmation that workflow has started.

**Event: `iteration_start`**  
Notification that a new iteration has started.

**Event: `plan_generated`**  
Notification that a teaching plan has been generated.

**Event: `analysis_complete`**  
Notification that cross-analysis has completed.

**Event: `plan_improved`**  
Notification that a plan has been improved.

**Event: `workflow_complete`**  
Notification that the workflow has completed.

**Event: `error`**  
Error notifications.

**Event: `log`**  
Real-time log entries.

**Event: `debug_info`**  
Debug information response.

---

## 🔒 **Error Handling**

### **Error Response Format**

All API endpoints return errors in the following format:

```json
{
  "error": "Error message description",
  "status_code": 400
}
```

### **Common Error Codes**

| **Code** | **Description** |
|----------|-----------------|
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Endpoint not found |
| 500 | Internal Server Error - Server error |

### **Error Examples**

**400 Bad Request:**
```json
{
  "error": "Subject is required",
  "status_code": 400
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "status_code": 500
}
```

---

## 📝 **Request/Response Examples**

### **Complete Workflow Example**

1. **Start Workflow:**
```bash
curl -X POST http://localhost:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Science",
    "grade": "Grade 7",
    "objectives": "Students will understand the water cycle and its importance",
    "max_rounds": 3
  }'
```

2. **Check Status:**
```bash
curl http://localhost:5000/api/status
```

3. **Get Final Results:**
```bash
curl http://localhost:5000/api/debug/workflow_manager
```

---

## 🔧 **Configuration**

### **Environment Variables**

Required environment variables:
- `QWEN_API_KEY` - Qwen API key
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `PERSONAL_CHATGPT_URL` - Personal ChatGPT Server URL
- `PERSONAL_CHATGPT_API_KEY` - Personal ChatGPT Server API key
- `FLASK_SECRET_KEY` - Flask session secret

### **Optional Environment Variables**

- `FLASK_DEBUG` - Enable debug mode
- `FLASK_HOST` - Host binding
- `FLASK_PORT` - Port number
- `LOG_LEVEL` - Logging level
- `ENABLE_MONITORING` - Enable performance monitoring

---

## 🚀 **Rate Limiting**

Currently, the API does not implement rate limiting. For production deployments, consider implementing rate limiting based on your requirements.

---

## 📊 **Performance Considerations**

- **Response Times**: Most API calls should complete within 2-5 seconds
- **Concurrent Requests**: The system can handle multiple concurrent requests
- **WebSocket Connections**: Supports multiple simultaneous WebSocket connections
- **Memory Usage**: Monitor memory usage during long-running workflows

---

**MindGen v0.1.0 API** - Comprehensive API documentation for the AI-powered teaching plan generator.

---

*Last Updated: August 2025*  
*Version: v0.1.0 (Production Ready)* 