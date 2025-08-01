# services/agents/teaching_plan_agent.py
import time
import logging
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from ..llm_service import LangChainLLMService

logger = logging.getLogger(__name__)

class TeachingPlan(BaseModel):
    """Structured output for teaching plans"""
    objectives: List[str] = Field(description="Learning objectives")
    activities: List[Dict[str, Any]] = Field(description="Teaching activities")
    assessment: Dict[str, Any] = Field(description="Assessment methods")
    differentiation: str = Field(description="Differentiation strategies")
    time_allocation: Dict[str, int] = Field(description="Time allocation in minutes")

class TeachingPlanAgent:
    """Agent responsible for generating teaching plans from multiple LLMs"""
    
    def __init__(self, config_manager, socketio):
        self.config_manager = config_manager
        self.socketio = socketio
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Initialize LLM service
        self.llm_service = LangChainLLMService(config_manager)
        
        # Define tools
        self.tools = [
            Tool(
                name="query_curriculum_standards",
                func=self._query_curriculum_standards,
                description="Query curriculum standards for the subject and grade"
            ),
            Tool(
                name="retrieve_best_practices",
                func=self._retrieve_best_practices,
                description="Retrieve best teaching practices for the subject"
            ),
            Tool(
                name="generate_qwen_plan",
                func=self._generate_qwen_plan,
                description="Generate teaching plan using Qwen LLM"
            ),
            Tool(
                name="generate_deepseek_plan",
                func=self._generate_deepseek_plan,
                description="Generate teaching plan using DeepSeek LLM"
            ),
            Tool(
                name="generate_personal_chatgpt_plan",
                func=self._generate_personal_chatgpt_plan,
                description="Generate teaching plan using Personal ChatGPT Server LLM"
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
    
    def generate_plans(self, teacher_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate teaching plans from all three LLMs"""
        plans = {}
        
        for model_name in ['qwen', 'deepseek', 'personal_chatgpt']:
            try:
                start_time = time.time()
                
                # Generate plan using LangChain
                plan = self.llm_service.generate_teaching_plan(
                    model_name,
                    teacher_input['subject'],
                    teacher_input['grade'],
                    teacher_input['objectives']
                )
                
                duration = time.time() - start_time
                
                plans[model_name] = {
                    'status': 'success',
                    'content': plan.json(),
                    'structured_data': plan,
                    'model': model_name,
                    'duration': duration
                }
                
                # Emit real-time update
                self.socketio.emit('plan_generated', {
                    'model': model_name,
                    'content': plan.json()[:200] + '...',
                    'duration': duration
                })
                
                logger.info(f"Generated plan for {model_name} in {duration:.2f}s")
                
            except Exception as e:
                logger.error(f"Error generating plan for {model_name}: {str(e)}")
                plans[model_name] = {
                    'status': 'error',
                    'message': str(e),
                    'model': model_name
                }
        
        return plans
    
    def _get_agent_prompt(self):
        """Get agent system prompt"""
        template = """
        You are an expert teaching plan generator. Your role is to:
        1. Generate comprehensive teaching plans using different LLMs
        2. Ensure plans meet curriculum standards
        3. Incorporate best teaching practices
        4. Create engaging and effective learning experiences
        5. Consider student needs and differentiation strategies
        
        Use the available tools to generate high-quality teaching plans.
        
        {agent_scratchpad}
        """
        return PromptTemplate(
            template=template,
            input_variables=["agent_scratchpad"]
        )
    
    # Tool implementations
    def _query_curriculum_standards(self, query: str) -> str:
        """Query curriculum standards"""
        # This would integrate with a knowledge base
        return f"Curriculum standards for: {query}"
    
    def _retrieve_best_practices(self, query: str) -> str:
        """Retrieve best practices"""
        # This would integrate with a knowledge base
        return f"Best practices for: {query}"
    
    def _generate_qwen_plan(self, input_data: str) -> str:
        """Generate plan using Qwen LLM"""
        try:
            # Parse input data
            data = eval(input_data) if isinstance(input_data, str) else input_data
            subject = data.get('subject', '')
            grade = data.get('grade', '')
            objectives = data.get('objectives', '')
            
            plan = self.llm_service.generate_teaching_plan('qwen', subject, grade, objectives)
            return plan.json()
        except Exception as e:
            return f"Error generating Qwen plan: {str(e)}"
    
    def _generate_deepseek_plan(self, input_data: str) -> str:
        """Generate plan using DeepSeek LLM"""
        try:
            # Parse input data
            data = eval(input_data) if isinstance(input_data, str) else input_data
            subject = data.get('subject', '')
            grade = data.get('grade', '')
            objectives = data.get('objectives', '')
            
            plan = self.llm_service.generate_teaching_plan('deepseek', subject, grade, objectives)
            return plan.json()
        except Exception as e:
            return f"Error generating DeepSeek plan: {str(e)}"
    
    def _generate_personal_chatgpt_plan(self, input_data: str) -> str:
        """Generate plan using Personal ChatGPT Server LLM"""
        try:
            # Parse input data
            data = eval(input_data) if isinstance(input_data, str) else input_data
            subject = data.get('subject', '')
            grade = data.get('grade', '')
            objectives = data.get('objectives', '')
            
            plan = self.llm_service.generate_teaching_plan('personal_chatgpt', subject, grade, objectives)
            return plan.json()
        except Exception as e:
            return f"Error generating Personal ChatGPT plan: {str(e)}" 