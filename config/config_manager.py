# config/config_manager.py
import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """Manages configuration loading and access for MindGen"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        load_dotenv()  # Load environment variables
        
        # Load configuration files
        self.system_config = self._load_yaml("system.yaml")
        self.models_config = self._load_yaml("models.yaml")
        
        # Validate configuration
        self._validate_config()
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file with environment variable substitution"""
        filepath = os.path.join(self.config_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Substitute environment variables
        content = self._substitute_env_vars(content)
        
        # Parse YAML
        config = yaml.safe_load(content)
        
        if config is None:
            raise ValueError(f"Invalid YAML in configuration file: {filepath}")
        
        return config
    
    def _substitute_env_vars(self, content: str) -> str:
        """Substitute environment variables in configuration content"""
        import re
        
        def replace_env_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        # Replace ${VAR_NAME} patterns with environment variable values
        content = re.sub(r'\$\{([^}]+)\}', replace_env_var, content)
        
        return content
    
    def _validate_config(self):
        """Validate configuration structure and required fields"""
        required_system_fields = ['max_iterations', 'quality_threshold', 'timeout_per_round']
        required_model_fields = ['api_url', 'api_key', 'model_name', 'timeout']
        
        # Validate system configuration
        system = self.system_config.get('system', {})
        for field in required_system_fields:
            if field not in system:
                raise ValueError(f"Missing required system configuration field: {field}")
        
        # Validate model configurations
        models = self.models_config.get('models', {})
        if not models:
            raise ValueError("No models configured")
        
        for model_name, model_config in models.items():
            for field in required_model_fields:
                if field not in model_config:
                    raise ValueError(f"Missing required field '{field}' for model '{model_name}'")
    
    def get_system_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """Get system configuration value"""
        system = self.system_config.get('system', {})
        
        if key is None:
            return system
        
        return system.get(key, default)
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        models = self.models_config.get('models', {})
        
        if model_name not in models:
            raise ValueError(f"Model '{model_name}' not found in configuration")
        
        return models[model_name]
    
    def get_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all model configurations"""
        return self.models_config.get('models', {})
    
    def get_agent_config(self, agent_name: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get agent configuration value"""
        agents = self.system_config.get('agents', {})
        
        if agent_name not in agents:
            return default
        
        agent_config = agents[agent_name]
        
        if key is None:
            return agent_config
        
        return agent_config.get(key, default)
    
    def get_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent configurations"""
        return self.system_config.get('agents', {})
    
    def get_flask_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """Get Flask configuration value"""
        flask_config = self.system_config.get('flask', {})
        
        if key is None:
            return flask_config
        
        return flask_config.get(key, default)
    
    def get_logging_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """Get logging configuration value"""
        logging_config = self.system_config.get('logging', {})
        
        if key is None:
            return logging_config
        
        return logging_config.get(key, default)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration (excluding sensitive data)"""
        config = {
            'system': self.get_system_config(),
            'agents': self.get_agent_configs(),
            'flask': self.get_flask_config(),
            'logging': self.get_logging_config(),
            'models': self.get_model_configs()
        }
        
        # Remove sensitive data
        for model in config['models'].values():
            if 'api_key' in model:
                model['api_key'] = '***'
        
        return config
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that all required API keys are set"""
        models = self.get_model_configs()
        validation_results = {}
        
        for model_name, model_config in models.items():
            api_key = model_config.get('api_key', '')
            validation_results[model_name] = bool(api_key and api_key != '***')
        
        return validation_results
    
    def get_timeout_config(self, component: str) -> Dict[str, Any]:
        """Get timeout configuration for a component"""
        timeouts = {
            'workflow': self.get_system_config('timeout_per_round', 300),
            'teaching_plan': self.get_agent_config('teaching_plan', 'timeout', 60),
            'cross_analysis': self.get_agent_config('cross_analysis', 'timeout', 90),
            'improvement': self.get_agent_config('improvement', 'timeout', 60),
            'knowledge_memory': self.get_agent_config('knowledge_memory', 'timeout', 30)
        }
        
        return {
            'timeout': timeouts.get(component, 60),
            'retry_attempts': self.get_agent_config(component, 'retry_attempts', 3)
        } 