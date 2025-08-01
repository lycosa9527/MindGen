# services/llm_service.py
import os
import logging
import json
from typing import Dict, Any, List
from langchain_community.chat_models import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
import dashscope
from dashscope import Generation

logger = logging.getLogger(__name__)

class QwenLLM:
    """Custom Qwen LLM wrapper for Alibaba Cloud DashScope"""
    
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 4000, timeout: int = 45):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.api_key = os.getenv("QWEN_API_KEY")
        
        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is required")
        
        # Set the API key for dashscope
        dashscope.api_key = self.api_key
    
    def invoke(self, prompt: str) -> str:
        """Invoke the Qwen model with a prompt"""
        try:
            response = Generation.call(
                model=self.model_name,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                raise Exception(f"Qwen API error: {response.message}")
                
        except Exception as e:
            logger.error(f"Error calling Qwen API: {str(e)}")
            raise e
    
    def bind(self, **kwargs):
        """Bind additional parameters to the LLM (required for function calling)"""
        # Create a new instance with bound parameters
        bound_llm = QwenLLM(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout
        )
        # Store bound parameters for later use
        bound_llm._bound_kwargs = kwargs
        return bound_llm
    
    def __call__(self, messages, **kwargs):
        """Call the LLM with messages (required for function calling)"""
        # Convert messages to prompt
        if isinstance(messages, list):
            # Extract content from messages
            prompt = "\n".join([msg.get('content', '') for msg in messages if msg.get('content')])
        else:
            prompt = str(messages)
        
        # Call the invoke method
        return self.invoke(prompt)

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
            # Initialize Qwen (Alibaba Cloud)
            qwen_config = self.config_manager.get_model_config('qwen')
            llms['qwen'] = QwenLLM(
                model_name=qwen_config.get('model_name', 'qwen-plus'),
                temperature=qwen_config.get('temperature', 0.7),
                max_tokens=qwen_config.get('max_tokens', 16000),
                timeout=qwen_config.get('timeout', 45)
            )
            logger.info("Qwen LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Qwen LLM: {str(e)}")
            llms['qwen'] = None
        
        try:
            # Initialize Qwen Fallback (Alibaba Cloud) - for agent fallback
            qwen_fallback_config = self.config_manager.get_model_config('qwen_fallback')
            llms['qwen_fallback'] = QwenLLM(
                model_name=qwen_fallback_config.get('model_name', 'qwen3-235b-a22b'),
                temperature=qwen_fallback_config.get('temperature', 0.7),
                max_tokens=qwen_fallback_config.get('max_tokens', 16000),
                timeout=qwen_fallback_config.get('timeout', 45)
            )
            logger.info("Qwen Fallback LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Qwen Fallback LLM: {str(e)}")
            llms['qwen_fallback'] = None
        
        try:
            # Initialize DeepSeek
            deepseek_config = self.config_manager.get_model_config('deepseek')
            llms['deepseek'] = ChatDeepSeek(
                model=deepseek_config.get('model_name', 'deepseek-reasoner'),
                temperature=deepseek_config.get('temperature', 0.7),
                max_tokens=deepseek_config.get('max_tokens', 32000),
                timeout=deepseek_config.get('timeout', 30),
                deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
            )
            logger.info("DeepSeek LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek LLM: {str(e)}")
            llms['deepseek'] = None
        
        try:
            # Initialize Personal ChatGPT Server (Primary - for China users)
            personal_chatgpt_config = self.config_manager.get_model_config('personal_chatgpt')
            personal_chatgpt_url = os.getenv("PERSONAL_CHATGPT_URL")
            personal_chatgpt_key = os.getenv("PERSONAL_CHATGPT_API_KEY")
            
            if personal_chatgpt_url and personal_chatgpt_key:
                llms['personal_chatgpt'] = ChatOpenAI(
                    model=personal_chatgpt_config.get('model_name', 'gpt-4o'),
                    temperature=personal_chatgpt_config.get('temperature', 0.7),
                    max_tokens=personal_chatgpt_config.get('max_tokens', 32000),
                    timeout=personal_chatgpt_config.get('timeout', 60),
                    openai_api_key=personal_chatgpt_key,
                    base_url=personal_chatgpt_url
                )
                logger.info("Personal ChatGPT Server LLM initialized successfully")
            else:
                logger.warning("Personal ChatGPT Server not configured - skipping initialization")
                llms['personal_chatgpt'] = None
        except Exception as e:
            logger.error(f"Failed to initialize Personal ChatGPT Server LLM: {str(e)}")
            llms['personal_chatgpt'] = None
        
        # OpenAI GPT-4o initialization removed - using Personal ChatGPT Server only
        # try:
        #     # Initialize GPT-4o (Optional - for users outside China)
        #     gpt4o_config = self.config_manager.get_model_config('gpt4o')
        #     gpt4o_api_key = os.getenv("GPT4O_API_KEY")
        #     
        #     if gpt4o_api_key:
        #         llms['gpt4o'] = ChatOpenAI(
        #             model=gpt4o_config.get('model_name', 'gpt-4o'),
        #             temperature=gpt4o_config.get('temperature', 0.7),
        #             max_tokens=gpt4o_config.get('max_tokens', 32000),
        #             timeout=gpt4o_config.get('timeout', 60),
        #             openai_api_key=gpt4o_api_key
        #         )
        #         logger.info("GPT-4o LLM initialized successfully")
        #     else:
        #         logger.warning("GPT-4o API key not configured - skipping initialization")
        #         llms['gpt4o'] = None
        # except Exception as e:
        #     logger.error(f"Failed to initialize GPT-4o LLM: {str(e)}")
        #     llms['gpt4o'] = None
        
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
    
    def get_agent_llm(self) -> Any:
        """Get the appropriate LLM for agents based on fallback configuration"""
        try:
            # Get fallback configuration
            fallback_config = self.config_manager.get_system_config().get('llm_fallback', {})
            primary_model = fallback_config.get('primary', 'personal_chatgpt')
            fallback_sequence = fallback_config.get('fallback_sequence', ['qwen_fallback', 'deepseek'])
            
            # Try primary model first
            if primary_model in self.llms and self.llms[primary_model] is not None:
                logger.info(f"Using primary LLM: {primary_model}")
                return self.llms[primary_model]
            
            # Try fallback sequence
            for fallback_model in fallback_sequence:
                if fallback_model in self.llms and self.llms[fallback_model] is not None:
                    logger.info(f"Using fallback LLM: {fallback_model}")
                    return self.llms[fallback_model]
            
            # If no fallback available, raise exception
            raise Exception("No LLM available for agent initialization")
            
        except Exception as e:
            logger.error(f"Error getting agent LLM: {str(e)}")
            raise 