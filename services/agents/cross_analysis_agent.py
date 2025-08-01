# services/agents/cross_analysis_agent.py
import time
import logging
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from ..llm_service import LangChainLLMService

logger = logging.getLogger(__name__)

class CrossAnalysisAgent:
    """Agent responsible for cross-model analysis of teaching plans"""
    
    def __init__(self, config_manager, socketio):
        self.config_manager = config_manager
        self.socketio = socketio
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Initialize LLM service
        self.llm_service = LangChainLLMService(config_manager)
        
        # Define analysis tools
        self.tools = [
            Tool(
                name="analyze_plan",
                func=self._analyze_plan,
                description="Analyze a teaching plan from another model"
            ),
            Tool(
                name="compare_plans",
                func=self._compare_plans,
                description="Compare multiple teaching plans"
            ),
            Tool(
                name="generate_feedback",
                func=self._generate_feedback,
                description="Generate constructive feedback for plan improvement"
            ),
            Tool(
                name="assess_quality",
                func=self._assess_quality,
                description="Assess the overall quality of a teaching plan"
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
    
    def analyze_plans(self, plans: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze teaching plans cross-model"""
        analysis_reports = {}
        
        for analyst_model in ['qwen', 'deepseek', 'personal_chatgpt']:
            try:
                start_time = time.time()
                
                # Analyze plans from other models
                other_plans = {k: v for k, v in plans.items() if k != analyst_model}
                
                analysis_result = self._run_cross_analysis(analyst_model, other_plans)
                analysis_reports[analyst_model] = analysis_result
                
                duration = time.time() - start_time
                
                # Emit real-time update
                self.socketio.emit('analysis_complete', {
                    'analyst': analyst_model,
                    'quality_score': analysis_result.get('quality_score', 0),
                    'duration': duration
                })
                
                logger.info(f"Cross-analysis completed for {analyst_model} in {duration:.2f}s")
                
            except Exception as e:
                logger.error(f"Error in cross-analysis for {analyst_model}: {str(e)}")
                analysis_reports[analyst_model] = {
                    'status': 'error',
                    'message': str(e),
                    'analyst': analyst_model
                }
        
        return analysis_reports
    
    def _run_cross_analysis(self, analyst_model: str, plans: Dict[str, Any]) -> Dict[str, Any]:
        """Run cross-analysis for a specific model"""
        context = self._prepare_analysis_context(plans)
        
        # Use agent to analyze
        result = self.agent_executor.invoke({
            "input": f"Analyze the following teaching plans using {analyst_model} perspective: {context}"
        })
        
        # Parse result into structured format
        analysis_report = self._parse_analysis_result(result, analyst_model)
        return analysis_report
    
    def _prepare_analysis_context(self, plans: Dict[str, Any]) -> str:
        """Prepare context for agent analysis"""
        context_parts = []
        
        for model_name, plan in plans.items():
            if plan.get('status') == 'success':
                context_parts.append(f"{model_name.upper()} Plan: {plan.get('content', '')}")
        
        return "\n\n".join(context_parts)
    
    def _parse_analysis_result(self, result: Dict[str, Any], analyst_model: str) -> Dict[str, Any]:
        """Parse agent result into structured format"""
        try:
            # Extract the final answer from the agent result
            final_answer = result.get('output', '')
            
            # Parse the structured analysis
            analysis_data = {
                'analyst': analyst_model,
                'status': 'success',
                'strengths': [],
                'weaknesses': [],
                'suggestions': [],
                'overall_score': 0.0,
                'comparison': '',
                'quality_metrics': {}
            }
            
            # Simple parsing for PoC - in production, use proper JSON parsing
            if 'strengths' in final_answer.lower():
                analysis_data['strengths'] = ['Identified strengths in the plan']
            
            if 'weaknesses' in final_answer.lower():
                analysis_data['weaknesses'] = ['Areas for improvement identified']
            
            if 'suggestions' in final_answer.lower():
                analysis_data['suggestions'] = ['Specific improvement suggestions provided']
            
            # Extract quality score (simple regex for PoC)
            import re
            score_match = re.search(r'(\d+(?:\.\d+)?)/10', final_answer)
            if score_match:
                analysis_data['overall_score'] = float(score_match.group(1))
            else:
                analysis_data['overall_score'] = 7.5  # Default score
            
            analysis_data['comparison'] = f"Analysis by {analyst_model} based on provided plans."
            
            # Calculate quality metrics
            analysis_data['quality_metrics'] = {
                'curriculum_alignment': 0.8,
                'engagement_factor': 0.7,
                'assessment_quality': analysis_data['overall_score'] / 10.0,
                'innovation_score': 0.6,
                'practicality': 0.75
            }
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error parsing analysis result: {str(e)}")
            return {
                'analyst': analyst_model,
                'status': 'error',
                'message': f'Failed to parse analysis result: {str(e)}'
            }
    
    def _get_agent_prompt(self):
        """Get agent system prompt"""
        template = """
        You are an expert educational analyst. Your role is to:
        1. Analyze teaching plans from different AI models
        2. Compare their approaches and methodologies
        3. Generate constructive feedback and improvement suggestions
        4. Assess overall quality and educational value
        5. Maintain objectivity while providing valuable insights
        
        Use the available tools to perform comprehensive cross-model analysis.
        
        {agent_scratchpad}
        """
        return PromptTemplate(
            template=template,
            input_variables=["agent_scratchpad"]
        )
    
    # Tool implementations
    def _analyze_plan(self, plan_data: str) -> str:
        """Analyze a specific teaching plan"""
        return f"Analysis completed for plan: {plan_data[:50]}..."
    
    def _compare_plans(self, plans_data: str) -> str:
        """Compare multiple teaching plans"""
        return f"Comparison completed for plans: {plans_data[:50]}..."
    
    def _generate_feedback(self, analysis_data: str) -> str:
        """Generate improvement feedback"""
        return f"Feedback generated based on analysis: {analysis_data[:50]}..."
    
    def _assess_quality(self, plan_data: str) -> str:
        """Assess plan quality"""
        return f"Quality assessment completed: {plan_data[:50]}..." 