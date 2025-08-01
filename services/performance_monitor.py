# services/performance_monitor.py
import time
import psutil
import logging
from typing import Dict, Any, List
from threading import Thread, Lock

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and resource usage"""
    
    def __init__(self):
        self.metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'response_times': {},
            'error_rates': {},
            'throughput': 0.0,
            'start_time': time.time()
        }
        
        self.lock = Lock()
        self.monitoring_thread = None
        self.is_monitoring = False
    
    def start_monitoring(self):
        """Start performance monitoring in background thread"""
        if self.is_monitoring:
            logger.warning("Performance monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def _monitor_resources(self):
        """Monitor system resources in background thread"""
        while self.is_monitoring:
            try:
                with self.lock:
                    self.metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
                    self.metrics['memory_usage'] = psutil.virtual_memory().percent
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {str(e)}")
                time.sleep(10)  # Wait longer on error
    
    def record_operation(self, operation_name: str, duration: float, success: bool):
        """Record operation performance"""
        with self.lock:
            if operation_name not in self.metrics['response_times']:
                self.metrics['response_times'][operation_name] = []
            
            self.metrics['response_times'][operation_name].append(duration)
            
            # Keep only last 100 measurements
            if len(self.metrics['response_times'][operation_name]) > 100:
                self.metrics['response_times'][operation_name] = self.metrics['response_times'][operation_name][-100:]
            
            if not success:
                if operation_name not in self.metrics['error_rates']:
                    self.metrics['error_rates'][operation_name] = 0
                self.metrics['error_rates'][operation_name] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        with self.lock:
            return {
                'system_metrics': {
                    'cpu_usage': self.metrics['cpu_usage'],
                    'memory_usage': self.metrics['memory_usage'],
                    'uptime': time.time() - self.metrics['start_time']
                },
                'performance_metrics': {
                    'average_response_time': self._calculate_average_response_time(),
                    'error_rate': self._calculate_error_rate(),
                    'throughput': self._calculate_throughput()
                },
                'operation_metrics': {
                    'response_times': self._get_operation_response_times(),
                    'error_rates': self.metrics['error_rates'].copy()
                }
            }
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time across all operations"""
        all_times = []
        for times in self.metrics['response_times'].values():
            all_times.extend(times)
        
        return sum(all_times) / len(all_times) if all_times else 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate overall error rate"""
        total_operations = sum(len(times) for times in self.metrics['response_times'].values())
        total_errors = sum(self.metrics['error_rates'].values())
        
        return total_errors / total_operations if total_operations > 0 else 0.0
    
    def _calculate_throughput(self) -> float:
        """Calculate operations per second"""
        uptime = time.time() - self.metrics['start_time']
        total_operations = sum(len(times) for times in self.metrics['response_times'].values())
        
        return total_operations / uptime if uptime > 0 else 0.0
    
    def _get_operation_response_times(self) -> Dict[str, Dict[str, float]]:
        """Get response time statistics for each operation"""
        operation_stats = {}
        
        for operation_name, times in self.metrics['response_times'].items():
            if times:
                operation_stats[operation_name] = {
                    'count': len(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'latest': times[-1] if times else 0.0
                }
        
        return operation_stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        with self.lock:
            cpu_usage = self.metrics['cpu_usage']
            memory_usage = self.metrics['memory_usage']
            error_rate = self._calculate_error_rate()
            
            # Determine health status
            if cpu_usage > 90 or memory_usage > 90 or error_rate > 0.1:
                health_status = 'critical'
            elif cpu_usage > 70 or memory_usage > 70 or error_rate > 0.05:
                health_status = 'warning'
            else:
                health_status = 'healthy'
            
            return {
                'status': health_status,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'error_rate': error_rate,
                'uptime': time.time() - self.metrics['start_time']
            }
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        with self.lock:
            self.metrics = {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_times': {},
                'error_rates': {},
                'throughput': 0.0,
                'start_time': time.time()
            }
        
        logger.info("Performance metrics reset")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        try:
            return {
                'cpu': {
                    'count': psutil.cpu_count(),
                    'percent': psutil.cpu_percent(interval=1),
                    'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent,
                    'used': psutil.virtual_memory().used
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'network': {
                    'connections': len(psutil.net_connections())
                }
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {'error': str(e)} 