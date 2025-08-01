# services/error_handler.py
import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the MindGen system"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
    
    def handle_agent_error(self, agent_name: str, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors from agent operations"""
        error_info = {
            'agent': agent_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': time.time()
        }
        
        self.logger.error(f"Agent error: {error_info}")
        
        # Determine retry strategy
        if self._should_retry(error):
            return self._retry_operation(agent_name, context)
        else:
            return self._handle_fatal_error(error_info)
    
    def handle_llm_error(self, model_name: str, error: Exception) -> Dict[str, Any]:
        """Handle errors from LLM API calls"""
        error_info = {
            'model': model_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': time.time()
        }
        
        self.logger.error(f"LLM error: {error_info}")
        
        # Implement fallback strategy
        return self._implement_fallback(model_name, error_info)
    
    def _should_retry(self, error: Exception) -> bool:
        """Determine if operation should be retried"""
        retryable_errors = [
            'TimeoutError',
            'ConnectionError',
            'RateLimitError',
            'requests.exceptions.Timeout',
            'requests.exceptions.ConnectionError',
            'requests.exceptions.RequestException'
        ]
        
        return type(error).__name__ in retryable_errors or any(
            retryable_error in str(type(error)) for retryable_error in retryable_errors
        )
    
    def _retry_operation(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry operation with exponential backoff"""
        max_retries = self.config_manager.get_agent_config(agent_name, 'retry_attempts', 3)
        
        for attempt in range(max_retries):
            try:
                # Implement retry logic here
                time.sleep(2 ** attempt)  # Exponential backoff
                return {'status': 'retry_success', 'attempt': attempt + 1}
            except Exception as e:
                if attempt == max_retries - 1:
                    return {'status': 'retry_failed', 'error': str(e)}
        
        return {'status': 'retry_failed'}
    
    def _handle_fatal_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fatal errors that cannot be retried"""
        return {
            'status': 'fatal_error',
            'error_info': error_info,
            'message': 'Operation failed and cannot be retried'
        }
    
    def _implement_fallback(self, model_name: str, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Implement fallback strategy for LLM failures"""
        fallback_models = {
            'qwen': 'gpt4o',
            'deepseek': 'qwen',
            'gpt4o': 'deepseek'
        }
        
        fallback_model = fallback_models.get(model_name, 'gpt4o')
        
        return {
            'status': 'fallback',
            'original_model': model_name,
            'fallback_model': fallback_model,
            'error_info': error_info
        }
    
    def retry_on_error(self, max_retries: int = 3, delay: float = 1.0):
        """Decorator for retrying operations on error"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        self.logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}"
                        )
                        
                        if attempt < max_retries - 1:
                            time.sleep(delay * (2 ** attempt))  # Exponential backoff
                
                # All retries failed
                self.logger.error(
                    f"All {max_retries} attempts failed for {func.__name__}: {str(last_exception)}"
                )
                raise last_exception
            
            return wrapper
        return decorator
    
    def handle_timeout(self, timeout_seconds: int = 60):
        """Decorator for handling timeouts"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
                
                # Set up timeout
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
                
                try:
                    result = func(*args, **kwargs)
                    signal.alarm(0)  # Cancel timeout
                    return result
                except TimeoutError:
                    self.logger.error(f"Timeout occurred in {func.__name__}")
                    raise
                finally:
                    signal.signal(signal.SIGALRM, old_handler)
            
            return wrapper
        return decorator
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with additional context"""
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': time.time()
        }
        
        self.logger.error(f"Error with context: {error_context}")
        return error_context 