# src/admin/system_monitor.py content
import platform
import redis
import psycopg2
from typing import Dict, Any, List, Tuple
from datetime import datetime
import time

class SystemMonitor:
    """Monitor system health and performance."""
    
    def __init__(self, redis_host: str = 'redis', redis_port: int = 6379,
                 pg_host: str = 'postgres', pg_port: int = 5432,
                 pg_user: str = 'postgres', pg_password: str = 'postgres',
                 pg_db: str = 'telegram_bot'):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.pg_db = pg_db
        
        # Performance history - store last 24 hours (at 5-minute intervals = 288 data points)
        self.history_max_size = 288
        self.history = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'redis': [],
            'postgres': []
        }
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect system metrics.
        
        Returns:
            Dictionary of system metrics
        """
        # Current time
        now = datetime.now().isoformat()
        
        # Collect metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Redis connection check
        redis_status, redis_latency = self._check_redis_connection()
        
        # Postgres connection check
        pg_status, pg_latency = self._check_postgres_connection()
        
        # Create metrics dictionary
        metrics = {
            'timestamp': now,
            'cpu': {
                'usage_percent': cpu_usage
            },
            'memory': {
                'usage_percent': memory_usage
            },
            'disk': {
                'usage_percent': disk_usage
            },
            'redis': {
                'status': redis_status,
                'latency_ms': redis_latency
            },
            'postgres': {
                'status': pg_status,
                'latency_ms': pg_latency
            }
        }
        
        # Update history
        self._update_history('cpu', now, cpu_usage)
        self._update_history('memory', now, memory_usage)
        self._update_history('disk', now, disk_usage)
        self._update_history('redis', now, redis_latency if redis_status == 'up' else -1)
        self._update_history('postgres', now, pg_latency if pg_status == 'up' else -1)
        
        return metrics
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dictionary of system information
        """
        return {
            'os': {
                'name': platform.system(),
                'version': platform.version(),
                'architecture': platform.architecture()[0]
            },
            'python': {
                'version': platform.python_version(),
                'implementation': platform.python_implementation()
            },
            'process': {
                'pid': os.getpid(),
                'start_time': datetime.fromtimestamp(psutil.Process().create_time()).isoformat()
            }
        }
    
    def get_performance_history(self, metric_type: str = None) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get performance history.
        
        Args:
            metric_type: Optional metric type to filter by
            
        Returns:
            Dictionary of performance history data
        """
        if metric_type and metric_type in self.history:
            return {metric_type: self.history[metric_type]}
        else:
            return self.history
    
    def _check_redis_connection(self) -> Tuple[str, float]:
        """Check Redis connection and measure latency."""
        try:
            # Connect to Redis
            start_time = time.time()
            client = redis.Redis(host=self.redis_host, port=self.redis_port)
            client.ping()
            end_time = time.time()
            
            # Calculate latency in milliseconds
            latency = (end_time - start_time) * 1000
            
            return 'up', latency
        except Exception:
            return 'down', -1
    
    def _check_postgres_connection(self) -> Tuple[str, float]:
        """Check Postgres connection and measure latency."""
        try:
            # Connect to Postgres
            start_time = time.time()
            conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                user=self.pg_user,
                password=self.pg_password,
                dbname=self.pg_db
            )
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.fetchone()
            cur.close()
            conn.close()
            end_time = time.time()
            
            # Calculate latency in milliseconds
            latency = (end_time - start_time) * 1000
            
            return 'up', latency
        except Exception:
            return 'down', -1
    
    def _update_history(self, metric_type: str, timestamp: str, value: float) -> None:
        """Update performance history."""
        self.history[metric_type].append((timestamp, value))
        
        # Limit history size
        if len(self.history[metric_type]) > self.history_max_size:
            self.history[metric_type] = self.history[metric_type][-self.history_max_size:]