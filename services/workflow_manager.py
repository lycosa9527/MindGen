# services/workflow_manager.py
import time
import logging
from typing import Dict, Any, List
from threading import Lock
from .agents.teaching_plan_agent import TeachingPlanAgent
from .agents.cross_analysis_agent import CrossAnalysisAgent
from .agents.improvement_agent import ImprovementAgent
from .agents.knowledge_memory_agent import KnowledgeMemoryAgent
from .quality_metrics import QualityMetrics
from .error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class WorkflowManager:
    """Coordinates the entire teaching plan improvement workflow"""
    
    def __init__(self, config_manager, socketio):
        self.config_manager = config_manager
        self.socketio = socketio
        self.lock = Lock()
        
        # Initialize agents
        self.teaching_plan_agent = TeachingPlanAgent(config_manager, socketio)
        self.cross_analysis_agent = CrossAnalysisAgent(config_manager, socketio)
        self.improvement_agent = ImprovementAgent(config_manager, socketio)
        self.knowledge_memory_agent = KnowledgeMemoryAgent(config_manager, socketio)
        
        # Initialize services
        self.quality_metrics = QualityMetrics()
        self.error_handler = ErrorHandler(config_manager)
        
        # Workflow configuration
        self.max_iterations = config_manager.get_system_config('max_iterations', 3)
        self.quality_threshold = config_manager.get_system_config('quality_threshold', 0.8)
        self.timeout_per_round = config_manager.get_system_config('timeout_per_round', 300)
        
        # Workflow state
        self.status = {
            "current_iteration": 0,
            "max_iterations": self.max_iterations,
            "is_running": False,
            "current_quality_score": 0.0,
            "plans": {},
            "analysis_reports": {},
            "final_plan": None,
            "error": None
        }
        
        # Debug data storage
        self.debug_data = {
            "teaching_plan_agent": [],
            "cross_analysis_agent": [],
            "improvement_agent": [],
            "knowledge_memory_agent": []
        }
    
    def run_workflow(self, teacher_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete teaching plan improvement workflow"""
        with self.lock:
            if self.status["is_running"]:
                logger.warning("Workflow already running")
                return {"status": "error", "message": "Workflow already running"}
            
            # Initialize workflow state
            self.status.update({
                "current_iteration": 0,
                "is_running": True,
                "current_quality_score": 0.0,
                "plans": {},
                "analysis_reports": {},
                "final_plan": None,
                "error": None
            })
        
        try:
            # Notify workflow start
            self.socketio.emit('workflow_start', {
                'message': 'Starting teaching plan generation workflow...',
                'max_iterations': self.max_iterations
            })
            
            # Step 1: Generate initial plans
            logger.info("Generating initial teaching plans")
            self._update_status("current_iteration", 0)
            self.socketio.emit('iteration_start', {
                'iteration': 0,
                'step': 'initial_generation'
            })
            
            initial_plans = self.teaching_plan_agent.generate_plans(teacher_input)
            self._update_status("plans", initial_plans)
            self._store_debug("teaching_plan_agent", initial_plans)
            
            # Check for errors in initial generation
            if self._has_critical_errors(initial_plans):
                error_msg = "Failed to generate initial plans from all models"
                self._handle_workflow_error(error_msg)
                return {"status": "error", "message": error_msg}
            
            current_plans = initial_plans
            quality_history = []
            
            # Step 2: Iterative improvement loop
            for iteration in range(1, self.max_iterations + 1):
                logger.info(f"Starting iteration {iteration} of {self.max_iterations}")
                self._update_status("current_iteration", iteration)
                self.socketio.emit('iteration_start', {
                    'iteration': iteration,
                    'max_iterations': self.max_iterations,
                    'step': 'iteration_start'
                })
                
                # Cross-analysis
                logger.info(f"Iteration {iteration}: Performing cross-analysis")
                self.socketio.emit('status_update', {
                    'message': f'Iteration {iteration}: Performing cross-analysis...',
                    'iteration': iteration,
                    'step': 'cross_analysis'
                })
                
                analysis_reports = self.cross_analysis_agent.analyze_plans(current_plans)
                self._update_status("analysis_reports", analysis_reports)
                self._store_debug("cross_analysis_agent", analysis_reports)
                
                # Calculate quality score
                quality_score = self.quality_metrics.calculate_quality_score(analysis_reports)
                quality_history.append(quality_score)
                self._update_status("current_quality_score", quality_score)
                
                self.socketio.emit('quality_update', {
                    'iteration': iteration,
                    'quality_score': quality_score,
                    'threshold': self.quality_threshold
                })
                
                # Check quality threshold
                if quality_score >= self.quality_threshold:
                    logger.info(f"Quality threshold met: {quality_score} >= {self.quality_threshold}")
                    self.socketio.emit('quality_threshold_met', {
                        'quality_score': quality_score,
                        'threshold': self.quality_threshold,
                        'iteration': iteration
                    })
                    break
                
                # Check for convergence
                if self.quality_metrics.detect_convergence(quality_history):
                    logger.info("Quality has converged, stopping iterations")
                    self.socketio.emit('convergence_detected', {
                        'iteration': iteration,
                        'quality_history': quality_history
                    })
                    break
                
                # Improve plans based on analysis
                logger.info(f"Iteration {iteration}: Improving plans")
                self.socketio.emit('status_update', {
                    'message': f'Iteration {iteration}: Improving plans...',
                    'iteration': iteration,
                    'step': 'improvement'
                })
                
                improved_plans = self.improvement_agent.improve_plans(current_plans, analysis_reports)
                self._update_status("plans", improved_plans)
                self._store_debug("improvement_agent", improved_plans)
                
                # Check for errors in improvement
                if self._has_critical_errors(improved_plans):
                    logger.warning("Errors in plan improvement, using previous plans")
                    # Continue with previous plans if improvement failed
                
                current_plans = improved_plans
                
                # Iteration completion
                self.socketio.emit('iteration_complete', {
                    'iteration': iteration,
                    'quality_score': quality_score,
                    'message': f'Iteration {iteration} completed'
                })
            
            # Step 3: Generate final plan
            logger.info("Generating final teaching plan")
            self.socketio.emit('status_update', {
                'message': 'Generating final teaching plan...',
                'step': 'final_generation'
            })
            
            final_plan = self._generate_final_plan(current_plans, analysis_reports)
            self._update_status("final_plan", final_plan)
            
            # Workflow completion
            self.socketio.emit('workflow_complete', {
                'final_plan': final_plan,
                'iterations_completed': self.status["current_iteration"],
                'final_quality_score': self.status["current_quality_score"],
                'message': 'Teaching plan generation completed successfully'
            })
            
            logger.info("Workflow completed successfully")
            return {
                'status': 'success',
                'final_plan': final_plan,
                'iterations_completed': self.status["current_iteration"],
                'final_quality_score': self.status["current_quality_score"]
            }
            
        except Exception as e:
            logger.error(f"Error in workflow: {str(e)}")
            self._handle_workflow_error(str(e))
            return {"status": "error", "message": str(e)}
        
        finally:
            with self.lock:
                self.status["is_running"] = False
    
    def _update_status(self, key: str, value):
        """Update workflow status with thread safety"""
        with self.lock:
            self.status[key] = value
    
    def _store_debug(self, component: str, data):
        """Store debug data for component"""
        self.debug_data[component].append({
            "timestamp": time.time(),
            "data": data
        })
    
    def _has_critical_errors(self, plans: Dict[str, Any]) -> bool:
        """Check if there are critical errors in plans"""
        successful_plans = sum(1 for plan in plans.values() if plan.get('status') == 'success')
        return successful_plans < 2  # Need at least 2 successful plans
    
    def _generate_final_plan(self, plans: Dict[str, Any], analysis_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final teaching plan from best elements"""
        # Simple consensus: select the plan with highest quality score
        best_plan = None
        best_score = 0.0
        
        for model_name, plan in plans.items():
            if plan.get('status') == 'success':
                # Get quality score for this plan from analysis
                plan_score = 0.0
                for report in analysis_reports.values():
                    if report.get('status') == 'success':
                        # Extract score for this specific plan
                        plan_analysis = report.get('plan_analysis', {}).get(model_name, {})
                        plan_score = max(plan_score, plan_analysis.get('quality_score', 0.0))
                
                if plan_score > best_score:
                    best_score = plan_score
                    best_plan = plan
        
        if best_plan:
            return {
                'status': 'success',
                'content': best_plan['content'],
                'model': best_plan['model'],
                'quality_score': best_score,
                'summary': f'Final plan generated from {best_plan["model"]} with quality score {best_score:.2f}'
            }
        else:
            return {
                'status': 'error',
                'message': 'No valid plans available for final generation'
            }
    
    def _handle_workflow_error(self, error_message: str):
        """Handle workflow errors"""
        with self.lock:
            self.status["error"] = error_message
            self.status["is_running"] = False
        
        self.socketio.emit('workflow_error', {
            'message': error_message
        })
    
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        with self.lock:
            return self.status.copy()
    
    def get_debug_info(self, component: str) -> List[Dict[str, Any]]:
        """Get debug information for specific component"""
        return self.debug_data.get(component, [])
    
    def reset_workflow(self):
        """Reset workflow state"""
        with self.lock:
            self.status = {
                "current_iteration": 0,
                "max_iterations": self.max_iterations,
                "is_running": False,
                "current_quality_score": 0.0,
                "plans": {},
                "analysis_reports": {},
                "final_plan": None,
                "error": None
            }
            
            # Clear debug data
            for component in self.debug_data:
                self.debug_data[component] = [] 