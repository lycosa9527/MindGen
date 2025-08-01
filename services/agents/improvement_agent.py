# services/agents/improvement_agent.py
import time
import logging
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from ..llm_service import LangChainLLMService

logger = logging.getLogger(__name__)

class ImprovementAgent:
    """Agent responsible for improving teaching plans based on feedback"""
    
    def __init__(self, config_manager, socketio):
        self.config_manager = config_manager
        self.socketio = socketio
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Initialize LLM service
        self.llm_service = LangChainLLMService(config_manager)
        
        # Define improvement tools
        self.tools = [
            Tool(
                name="improve_plan",
                func=self._improve_plan,
                description="Improve a teaching plan based on feedback"
            ),
            Tool(
                name="enhance_objectives",
                func=self._enhance_objectives,
                description="Enhance learning objectives"
            ),
            Tool(
                name="optimize_activities",
                func=self._optimize_activities,
                description="Optimize teaching activities"
            ),
            Tool(
                name="strengthen_assessment",
                func=self._strengthen_assessment,
                description="Strengthen assessment methods"
            )
        ]
        
        # Create agent with configurable fallback LLM
        agent_llm = self.llm_service.get_agent_llm()
        
        self.agent = create_openai_functions_agent(
            llm=agent_llm,
            tools=self.tools,
            prompt=self._get_agent_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
    
    def improve_plans(self, plans: Dict[str, Any], analysis_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Improve teaching plans based on analysis feedback"""
        improved_plans = {}
        
        for model_name in ['qwen', 'deepseek', 'personal_chatgpt']:
            try:
                start_time = time.time()
                
                # Get feedback for this model
                feedback = self._extract_feedback_for_model(model_name, analysis_reports)
                
                if feedback and plans[model_name]['status'] == 'success':
                    # Improve plan using LangChain
                    improved_plan = self.llm_service.improve_teaching_plan(
                        model_name,
                        plans[model_name]['structured_data'],
                        feedback
                    )
                    
                    duration = time.time() - start_time
                    
                    improved_plans[model_name] = {
                        'status': 'success',
                        'content': improved_plan.json(),
                        'structured_data': improved_plan,
                        'model': model_name,
                        'improvement_applied': True,
                        'duration': duration
                    }
                else:
                    # Keep original plan if no feedback or error
                    improved_plans[model_name] = plans[model_name]
                    improved_plans[model_name]['improvement_applied'] = False
                
                # Emit real-time update
                self.socketio.emit('plan_improved', {
                    'model': model_name,
                    'improvement_applied': improved_plans[model_name]['improvement_applied'],
                    'duration': improved_plans[model_name].get('duration', 0)
                })
                
                logger.info(f"Plan improvement completed for {model_name}")
                
            except Exception as e:
                logger.error(f"Error improving plan for {model_name}: {str(e)}")
                improved_plans[model_name] = {
                    'status': 'error',
                    'message': str(e),
                    'model': model_name
                }
        
        return improved_plans
    
    def _extract_feedback_for_model(self, model_name: str, analysis_reports: Dict[str, Any]) -> str:
        """Extract feedback for a specific model from analysis reports"""
        feedback_parts = []
        
        for analyst_model, report in analysis_reports.items():
            if report.get('status') == 'success' and analyst_model != model_name:
                # Extract feedback relevant to this model
                if 'suggestions' in report:
                    feedback_parts.extend(report['suggestions'])
                
                if 'weaknesses' in report:
                    feedback_parts.extend([f"Address: {weakness}" for weakness in report['weaknesses']])
        
        return "\n\n".join(feedback_parts) if feedback_parts else ""
    
    def _get_agent_prompt(self):
        """Get agent system prompt"""
        template = """
        You are an expert teaching plan improver. Your role is to:
        1. Improve teaching plans based on constructive feedback
        2. Enhance learning objectives and activities
        3. Strengthen assessment methods
        4. Maintain the original plan's strengths while addressing weaknesses
        5. Ensure improvements align with educational best practices
        
        Use the available tools to enhance teaching plans effectively.
        
        {agent_scratchpad}
        """
        return PromptTemplate(
            template=template,
            input_variables=["agent_scratchpad"]
        )
    
    # Tool implementations
    def _improve_plan(self, plan_data: str) -> str:
        """Improve a teaching plan"""
        return f"Plan improvement completed: {plan_data[:50]}..."
    
    def _enhance_objectives(self, objectives: str) -> str:
        """Enhance learning objectives"""
        return f"Objectives enhanced: {objectives[:50]}..."
    
    def _optimize_activities(self, activities: str) -> str:
        """Optimize teaching activities"""
        return f"Activities optimized: {activities[:50]}..."
    
    def _strengthen_assessment(self, assessment: str) -> str:
        """Strengthen assessment methods"""
        return f"Assessment strengthened: {assessment[:50]}..." 