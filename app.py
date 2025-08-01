# app.py - Main Flask application for MindGen v0.1.0
from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO
from flask_session import Session
import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from config.config_manager import ConfigManager
from services.workflow_manager import WorkflowManager
from services.error_handler import ErrorHandler
from services.performance_monitor import PerformanceMonitor
from services.banner import display_banner

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize configuration
config_manager = ConfigManager()

# Setup enhanced logging with WebSocket streaming
def setup_logger():
    """Setup enhanced logging with WebSocket streaming capability for MindGen v0.1.0"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure rotating file handler
    handler = RotatingFileHandler(
        'logs/mindgen.log', 
        maxBytes=10000000, 
        backupCount=5
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Configure console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    # Add SocketIO log handler for real-time logging
    class SocketIOLogHandler(logging.Handler):
        def emit(self, record):
            try:
                log_entry = {
                    'timestamp': time.strftime('%H:%M:%S'),
                    'level': record.levelname,
                    'message': self.format(record),
                    'module': record.module,
                    'function': record.funcName
                }
                socketio.emit('log', log_entry)
            except Exception as e:
                # Prevent logging errors from causing issues
                pass
    
    socket_handler = SocketIOLogHandler()
    socket_handler.setFormatter(formatter)
    logger.addHandler(socket_handler)
    
    return logger

# Initialize logging
logger = setup_logger()

# Initialize services
error_handler = ErrorHandler(config_manager)
performance_monitor = PerformanceMonitor()
workflow_manager = WorkflowManager(config_manager, socketio)

# Start performance monitoring
performance_monitor.start_monitoring()

# Display banner on startup
display_banner()

@app.route('/')
def index():
    """Main interface for teaching plan generation - MindGen v0.1.0"""
    logger.info("Main page accessed")
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_workflow():
    """Start the teaching plan generation workflow - MindGen v0.1.0"""
    logger.info("Workflow start request received")
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No data provided"}), 400
        
        subject = data.get('subject', '').strip()
        grade = data.get('grade', '').strip()
        objectives = data.get('objectives', '').strip()
        max_rounds = data.get('max_rounds', 3)
        
        # Enhanced validation
        if not subject:
            logger.warning("Missing subject in request")
            return jsonify({"error": "Subject is required"}), 400
        if not grade:
            logger.warning("Missing grade in request")
            return jsonify({"error": "Grade is required"}), 400
        if not objectives:
            logger.warning("Missing objectives in request")
            return jsonify({"error": "Learning objectives are required"}), 400
        
        # Validate max_rounds
        try:
            max_rounds = int(max_rounds)
            if max_rounds < 1 or max_rounds > 10:
                logger.warning(f"Invalid max_rounds value: {max_rounds}")
                return jsonify({"error": "max_rounds must be between 1 and 10"}), 400
        except (ValueError, TypeError):
            logger.warning(f"Invalid max_rounds type: {type(max_rounds)}")
            return jsonify({"error": "max_rounds must be a number"}), 400
        
        # Prepare teacher input
        teacher_input = {
            'subject': subject,
            'grade': grade,
            'objectives': objectives,
            'max_rounds': max_rounds
        }
        
        logger.info(f"Starting workflow with: {teacher_input}")
        
        # Start background task
        socketio.start_background_task(
            workflow_manager.run_workflow,
            teacher_input
        )
        
        return jsonify({
            "status": "started",
            "max_rounds": max_rounds,
            "message": "Teaching plan generation started"
        })
        
    except Exception as e:
        logger.error(f"Error in start_workflow: {str(e)}", exc_info=True)
        error_info = error_handler.handle_agent_error('workflow', e, {'route': '/api/start'})
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status - MindGen v0.1.0"""
    logger.debug("Status request received")
    try:
        status = workflow_manager.get_status()
        performance_report = performance_monitor.get_performance_report()
        health_status = performance_monitor.get_health_status()
        
        response_data = {
            "workflow_status": status,
            "performance": performance_report,
            "health": health_status,
            "timestamp": time.time()
        }
        
        logger.debug(f"Status response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/<component>', methods=['GET'])
def get_debug_info(component):
    """Get debug information for specific component - MindGen v0.1.0"""
    logger.info(f"Debug request for component: {component}")
    try:
        valid_components = [
            'workflow_manager', 'teaching_plan_agent', 
            'cross_analysis_agent', 'improvement_agent', 
            'knowledge_memory_agent', 'system'
        ]
        
        if component not in valid_components:
            logger.warning(f"Invalid debug component requested: {component}")
            return jsonify({"error": f"Invalid component: {component}"}), 400
        
        debug_info = workflow_manager.get_debug_info(component)
        
        # Add system info for system component
        if component == 'system':
            debug_info.update({
                'config': config_manager.get_all_config(),
                'api_keys_valid': config_manager.validate_api_keys(),
                'performance': performance_monitor.get_system_info()
            })
        
        logger.debug(f"Debug info for {component}: {debug_info}")
        return jsonify(debug_info)
        
    except Exception as e:
        logger.error(f"Error getting debug info for {component}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration (without sensitive data) - MindGen v0.1.0"""
    logger.debug("Config request received")
    try:
        config = {
            'system': config_manager.get_system_config(),
            'agents': config_manager.get_agent_configs(),
            'models': config_manager.get_model_configs(),
            'flask': config_manager.get_flask_config(),
            'logging': config_manager.get_logging_config()
        }
        
        # Remove sensitive data
        for model in config['models'].values():
            if 'api_key' in model:
                model['api_key'] = '***'
        
        logger.debug("Config response sent")
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test LLM API connections - MindGen v0.1.0"""
    logger.info("Connection test request received")
    try:
        data = request.get_json() or {}
        model_name = data.get('model', 'all')
        
        from services.llm_service import LangChainLLMService
        llm_service = LangChainLLMService(config_manager)
        
        if model_name == 'all':
            results = {}
            for model in ['qwen', 'deepseek', 'personal_chatgpt']:
                results[model] = llm_service.test_model_connection(model)
            return jsonify(results)
        else:
            result = llm_service.test_model_connection(model_name)
            return jsonify({model_name: result})
            
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_workflow():
    """Reset the workflow state - MindGen v0.1.0"""
    logger.info("Workflow reset request received")
    try:
        workflow_manager.reset_workflow()
        performance_monitor.reset_metrics()
        logger.info("Workflow reset completed")
        return jsonify({"status": "success", "message": "Workflow reset successfully"})
        
    except Exception as e:
        logger.error(f"Error resetting workflow: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection - MindGen v0.1.0"""
    logger.info('Client connected')
    socketio.emit('status', {'message': 'Connected to MindGen v0.1.0'})
    
    # Send initial status
    status = workflow_manager.get_status()
    socketio.emit('status_update', status)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection - MindGen v0.1.0"""
    logger.info('Client disconnected')

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client - MindGen v0.1.0"""
    logger.debug('Status request via WebSocket')
    status = workflow_manager.get_status()
    socketio.emit('status_update', status)

@socketio.on('start_workflow')
def handle_workflow_start(data):
    """Handle workflow start request via WebSocket - MindGen v0.1.0"""
    logger.info('Workflow start request via WebSocket')
    try:
        # Validate data
        required_fields = ['subject', 'grade', 'objectives']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.warning(error_msg)
            socketio.emit('error', {'message': error_msg})
            return
        
        # Validate data types and values
        subject = data.get('subject', '').strip()
        grade = data.get('grade', '').strip()
        objectives = data.get('objectives', '').strip()
        max_rounds = data.get('max_rounds', 3)
        
        if not all([subject, grade, objectives]):
            error_msg = "All fields must have non-empty values"
            logger.warning(error_msg)
            socketio.emit('error', {'message': error_msg})
            return
        
        # Validate max_rounds
        try:
            max_rounds = int(max_rounds)
            if max_rounds < 1 or max_rounds > 10:
                error_msg = "max_rounds must be between 1 and 10"
                logger.warning(error_msg)
                socketio.emit('error', {'message': error_msg})
                return
        except (ValueError, TypeError):
            error_msg = "max_rounds must be a number"
            logger.warning(error_msg)
            socketio.emit('error', {'message': error_msg})
            return
        
        # Start workflow
        teacher_input = {
            'subject': subject,
            'grade': grade,
            'objectives': objectives,
            'max_rounds': max_rounds
        }
        
        logger.info(f"Starting workflow via WebSocket: {teacher_input}")
        
        socketio.start_background_task(
            workflow_manager.run_workflow,
            teacher_input
        )
        
        socketio.emit('workflow_started', {
            'message': 'Workflow started successfully',
            'max_rounds': teacher_input['max_rounds']
        })
        
    except Exception as e:
        logger.error(f"Error in WebSocket workflow start: {str(e)}", exc_info=True)
        socketio.emit('error', {'message': f'Failed to start workflow: {str(e)}'})

@socketio.on('request_debug')
def handle_debug_request(data):
    """Handle debug request from client - MindGen v0.1.0"""
    logger.debug('Debug request via WebSocket')
    try:
        component = data.get('component', 'system')
        debug_info = workflow_manager.get_debug_info(component)
        socketio.emit('debug_info', {'component': component, 'data': debug_info})
        
    except Exception as e:
        logger.error(f"Error in WebSocket debug request: {str(e)}", exc_info=True)
        socketio.emit('error', {'message': f'Failed to get debug info: {str(e)}'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors - MindGen v0.1.0"""
    logger.warning(f"404 error: {request.url}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors - MindGen v0.1.0"""
    logger.error(f'Internal server error: {str(error)}', exc_info=True)
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle unhandled exceptions - MindGen v0.1.0"""
    logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint - MindGen v0.1.0"""
    logger.debug("Health check request")
    try:
        health_status = performance_monitor.get_health_status()
        return jsonify({
            "status": "healthy",
            "timestamp": time.time(),
            "version": "v0.1.0",
            "health": health_status
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time(),
            "version": "v0.1.0"
        }), 500

# Metrics endpoint
@app.route('/metrics')
def get_metrics():
    """Get system metrics - MindGen v0.1.0"""
    logger.debug("Metrics request")
    try:
        metrics = performance_monitor.get_performance_report()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info('Starting MindGen v0.1.0 application...')
    try:
        socketio.run(
            app,
            debug=config_manager.get_flask_config('debug', False),
            host=config_manager.get_flask_config('host', '0.0.0.0'),
            port=config_manager.get_flask_config('port', 5000)
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise 