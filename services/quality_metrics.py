# services/quality_metrics.py
from typing import Dict, Any, List
import numpy as np
import logging

logger = logging.getLogger(__name__)

class QualityMetrics:
    """Quality assessment and metrics calculation"""
    
    def __init__(self):
        self.metrics = {
            'curriculum_alignment': 0.0,
            'engagement_factor': 0.0,
            'assessment_quality': 0.0,
            'innovation_score': 0.0,
            'practicality': 0.0
        }
        
        # Quality weights for different aspects
        self.weights = {
            'curriculum_alignment': 0.25,
            'engagement_factor': 0.20,
            'assessment_quality': 0.20,
            'innovation_score': 0.15,
            'practicality': 0.20
        }
    
    def calculate_quality_score(self, analysis_reports: Dict[str, Any]) -> float:
        """Calculate overall quality score from analysis reports"""
        scores = []
        
        for report in analysis_reports.values():
            if report.get('status') == 'success':
                # Extract quality metrics from report
                quality_metrics = report.get('quality_metrics', {})
                
                # Calculate weighted average
                weighted_score = self._calculate_weighted_score(quality_metrics)
                scores.append(weighted_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_weighted_score(self, metrics: Dict[str, float]) -> float:
        """Calculate weighted quality score"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, weight in self.weights.items():
            if metric in metrics:
                weighted_sum += metrics[metric] * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def detect_convergence(self, quality_history: List[float], threshold: float = 0.01) -> bool:
        """Detect if quality has converged"""
        if len(quality_history) < 3:
            return False
        
        # Check if recent improvements are below threshold
        recent_improvements = [
            abs(quality_history[i] - quality_history[i-1])
            for i in range(1, len(quality_history))
        ]
        
        return all(improvement < threshold for improvement in recent_improvements[-2:])
    
    def extract_quality_metrics(self, analysis_report: Dict[str, Any]) -> Dict[str, float]:
        """Extract quality metrics from analysis report"""
        metrics = {}
        
        # Extract metrics from different analysis components
        if 'strengths' in analysis_report:
            metrics['engagement_factor'] = self._calculate_engagement_score(analysis_report['strengths'])
        
        if 'weaknesses' in analysis_report:
            metrics['practicality'] = self._calculate_practicality_score(analysis_report['weaknesses'])
        
        if 'suggestions' in analysis_report:
            metrics['innovation_score'] = self._calculate_innovation_score(analysis_report['suggestions'])
        
        if 'overall_score' in analysis_report:
            metrics['assessment_quality'] = analysis_report['overall_score'] / 10.0
        
        # Default values for missing metrics
        for metric in self.weights.keys():
            if metric not in metrics:
                metrics[metric] = 0.5  # Default neutral score
        
        return metrics
    
    def _calculate_engagement_score(self, strengths: List[str]) -> float:
        """Calculate engagement factor from strengths"""
        engagement_keywords = [
            'interactive', 'engaging', 'hands-on', 'collaborative', 'student-centered',
            'active', 'participatory', 'inquiry-based', 'project-based', 'experiential'
        ]
        
        score = 0.0
        for strength in strengths:
            for keyword in engagement_keywords:
                if keyword.lower() in strength.lower():
                    score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_practicality_score(self, weaknesses: List[str]) -> float:
        """Calculate practicality score from weaknesses"""
        practicality_keywords = [
            'time', 'resources', 'complex', 'difficult', 'expensive', 'unrealistic',
            'overwhelming', 'complicated', 'impractical'
        ]
        
        score = 1.0  # Start with perfect score
        for weakness in weaknesses:
            for keyword in practicality_keywords:
                if keyword.lower() in weakness.lower():
                    score -= 0.1
        
        return max(score, 0.0)
    
    def _calculate_innovation_score(self, suggestions: List[str]) -> float:
        """Calculate innovation score from suggestions"""
        innovation_keywords = [
            'creative', 'innovative', 'novel', 'unique', 'original', 'cutting-edge',
            'modern', 'technology', 'digital', 'multimedia', 'interactive'
        ]
        
        score = 0.0
        for suggestion in suggestions:
            for keyword in innovation_keywords:
                if keyword.lower() in suggestion.lower():
                    score += 0.1
        
        return min(score, 1.0)
    
    def calculate_plan_similarity(self, plan1: Dict[str, Any], plan2: Dict[str, Any]) -> float:
        """Calculate similarity between two teaching plans"""
        # Simple similarity calculation based on content overlap
        content1 = plan1.get('content', '').lower()
        content2 = plan2.get('content', '').lower()
        
        # Extract key terms
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def assess_improvement(self, original_plans: Dict[str, Any], improved_plans: Dict[str, Any]) -> Dict[str, float]:
        """Assess improvement between original and improved plans"""
        improvements = {}
        
        for model_name in original_plans.keys():
            if model_name in improved_plans:
                original_plan = original_plans[model_name]
                improved_plan = improved_plans[model_name]
                
                if original_plan.get('status') == 'success' and improved_plan.get('status') == 'success':
                    # Calculate improvement metrics
                    similarity = self.calculate_plan_similarity(original_plan, improved_plan)
                    improvements[model_name] = {
                        'similarity': similarity,
                        'improvement_detected': similarity < 0.8  # Significant change
                    }
        
        return improvements
    
    def generate_quality_report(self, analysis_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        report = {
            'overall_score': self.calculate_quality_score(analysis_reports),
            'component_scores': {},
            'recommendations': [],
            'trends': {}
        }
        
        # Calculate component scores
        for model_name, report_data in analysis_reports.items():
            if report_data.get('status') == 'success':
                metrics = self.extract_quality_metrics(report_data)
                report['component_scores'][model_name] = metrics
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(analysis_reports)
        
        return report
    
    def _generate_recommendations(self, analysis_reports: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Analyze common weaknesses
        all_weaknesses = []
        for report in analysis_reports.values():
            if report.get('status') == 'success':
                all_weaknesses.extend(report.get('weaknesses', []))
        
        # Count weakness frequency
        weakness_counts = {}
        for weakness in all_weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        # Generate recommendations based on common weaknesses
        for weakness, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:  # Mentioned by multiple models
                recommendations.append(f"Address: {weakness}")
        
        return recommendations[:5]  # Top 5 recommendations 