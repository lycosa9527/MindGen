# services/llm_service.py
import os
import logging
from typing import Dict, Any, List
from langchain_community.chat_models import ChatOpenAI
from langchain_qianfan import QianfanLLM
from langchain_deepseek import DeepSeekLLM
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class TeachingPlan(BaseModel):
    """Structured output for teaching plans"""
    objectives: List[str] = Field(description="Learning objectives")
    activities: List[Dict[str, Any]] = Field(description="Teaching activities")
    assessment: Dict[str, Any] = Field(description="Assessment methods")
    differentiation: str = Field(description="Differentiation strategies")
    time_allocation: Dict[str, int] = Field(description="Time allocation in minutes")

class AnalysisReport(BaseModel):
    """Structured output for analysis reports"""
    strengths: List[str] = Field(description="Identified strengths")
    weaknesses: List[str] = Field(description="Areas for improvement")
    suggestions: List[str] = Field(description="Specific improvement suggestions")
    overall_score: float = Field(description="Overall quality score (1-10)")
    comparison: str = Field(description="Comparison with own approach")

class LangChainLLMService:
    """Service for managing LangChain LLM integrations"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.llms = self._initialize_llms()
        self.output_parser = PydanticOutputParser(pydantic_object=TeachingPlan)
        self.analysis_parser = PydanticOutputParser(pydantic_object=AnalysisReport)
    
    def _initialize_llms(self) -> Dict[str, Any]:
        """Initialize LangChain LLM wrappers"""
        llms = {}
        
        try:
            # Initialize Qwen (Qianfan)
            qwen_config = self.config_manager.get_model_config('qwen')
            llms['qwen'] = QianfanLLM(
                model="qwen-turbo",
                temperature=qwen_config.get('temperature', 0.7),
                max_tokens=qwen_config.get('max_tokens', 4000),
                timeout=qwen_config.get('timeout', 45),
                qianfan_ak=os.getenv("QIANFAN_ACCESS_KEY"),
                qianfan_sk=os.getenv("QIANFAN_SECRET_KEY")
            )
            logger.info("Qwen LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Qwen LLM: {str(e)}")
            llms['qwen'] = None
        
        try:
            # Initialize DeepSeek
            deepseek_config = self.config_manager.get_model_config('deepseek')
            llms['deepseek'] = DeepSeekLLM(
                model="deepseek-chat",
                temperature=deepseek_config.get('temperature', 0.7),
                max_tokens=deepseek_config.get('max_tokens', 4000),
                timeout=deepseek_config.get('timeout', 30),
                deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
            )
            logger.info("DeepSeek LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek LLM: {str(e)}")
            llms['deepseek'] = None
        
        try:
            # Initialize GPT-4o
            gpt4o_config = self.config_manager.get_model_config('gpt4o')
            llms['gpt4o'] = ChatOpenAI(
                model="gpt-4o",
                temperature=gpt4o_config.get('temperature', 0.7),
                max_tokens=gpt4o_config.get('max_tokens', 4000),
                timeout=gpt4o_config.get('timeout', 60),
                openai_api_key=os.getenv("GPT4O_API_KEY")
            )
            logger.info("GPT-4o LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GPT-4o LLM: {str(e)}")
            llms['gpt4o'] = None
        
        return llms
    
    def get_teaching_plan_prompt(self) -> PromptTemplate:
        """Get LangChain prompt template for teaching plan generation"""
        template = """
        As an expert {model_name} teaching designer, create a comprehensive teaching plan.
        
        Subject: {subject}
        Grade Level: {grade}
        Learning Objectives: {objectives}
        
        Please create a detailed teaching plan that includes:
        1. Clear learning objectives
        2. Engaging activities with time allocation
        3. Assessment methods
        4. Differentiation strategies
        5. Time allocation for each activity
        
        {format_instructions}
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["model_name", "subject", "grade", "objectives"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
    
    def get_analysis_prompt(self) -> PromptTemplate:
        """Get LangChain prompt template for cross-model analysis"""
        template = """
        As an expert {analyst_model} educational analyst, evaluate the following teaching plan 
        created by {design_model}:
        
        Teaching Plan:
        {teaching_plan}
        
        Please provide a comprehensive analysis including:
        1. Strengths of the plan
        2. Areas for improvement
        3. Specific suggestions
        4. Overall quality score (1-10)
        5. Comparison with your own approach
        
        {format_instructions}
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["analyst_model", "design_model", "teaching_plan"],
            partial_variables={"format_instructions": self.analysis_parser.get_format_instructions()}
        )
    
    def get_improvement_prompt(self) -> PromptTemplate:
        """Get LangChain prompt template for plan improvement"""
        template = """
        As an expert {model_name} educational designer, improve the following teaching plan 
        based on the feedback provided:
        
        Current Teaching Plan:
        {current_plan}
        
        Feedback for Improvement:
        {feedback}
        
        Please improve the plan by:
        1. Addressing the specific feedback points
        2. Enhancing areas that need improvement
        3. Maintaining the strengths of the original plan
        4. Making the plan more comprehensive and effective
        
        {format_instructions}
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["model_name", "current_plan", "feedback"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
    
    def generate_teaching_plan(self, model_name: str, subject: str, grade: str, objectives: str) -> TeachingPlan:
        """Generate teaching plan using LangChain"""
        if model_name not in self.llms or self.llms[model_name] is None:
            raise Exception(f"LLM {model_name} not available")
        
        llm = self.llms[model_name]
        prompt = self.get_teaching_plan_prompt()
        
        chain = prompt | llm | self.output_parser
        
        try:
            result = chain.invoke({
                "model_name": model_name.upper(),
                "subject": subject,
                "grade": grade,
                "objectives": objectives
            })
            return result
        except Exception as e:
            raise Exception(f"Error generating plan with {model_name}: {str(e)}")
    
    def analyze_teaching_plan(self, analyst_model: str, design_model: str, teaching_plan: TeachingPlan) -> AnalysisReport:
        """Analyze teaching plan using LangChain"""
        if analyst_model not in self.llms or self.llms[analyst_model] is None:
            raise Exception(f"LLM {analyst_model} not available")
        
        llm = self.llms[analyst_model]
        prompt = self.get_analysis_prompt()
        
        chain = prompt | llm | self.analysis_parser
        
        try:
            result = chain.invoke({
                "analyst_model": analyst_model.upper(),
                "design_model": design_model.upper(),
                "teaching_plan": teaching_plan.json()
            })
            return result
        except Exception as e:
            raise Exception(f"Error analyzing plan with {analyst_model}: {str(e)}")
    
    def improve_teaching_plan(self, model_name: str, current_plan: TeachingPlan, feedback: str) -> TeachingPlan:
        """Improve teaching plan using LangChain"""
        if model_name not in self.llms or self.llms[model_name] is None:
            raise Exception(f"LLM {model_name} not available")
        
        llm = self.llms[model_name]
        prompt = self.get_improvement_prompt()
        
        chain = prompt | llm | self.output_parser
        
        try:
            result = chain.invoke({
                "model_name": model_name.upper(),
                "current_plan": current_plan.json(),
                "feedback": feedback
            })
            return result
        except Exception as e:
            raise Exception(f"Error improving plan with {model_name}: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available LLM models"""
        return [name for name, llm in self.llms.items() if llm is not None]
    
    def test_model_connection(self, model_name: str) -> Dict[str, Any]:
        """Test connection to a specific model"""
        if model_name not in self.llms or self.llms[model_name] is None:
            return {
                'status': 'error',
                'message': f'Model {model_name} not available'
            }
        
        try:
            # Simple test prompt
            test_prompt = "Hello, this is a test message."
            llm = self.llms[model_name]
            
            # Test the connection
            response = llm.invoke(test_prompt)
            
            return {
                'status': 'success',
                'message': 'Connection successful',
                'response': str(response)[:100] + '...'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection failed: {str(e)}'
            } 