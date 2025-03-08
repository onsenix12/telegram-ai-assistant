# src/monitoring/alerts.py content
from typing import Dict, Any, List, Optional, Callable
import threading
import time
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from src.monitoring.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class AlertManager:
    """Manage performance alerts."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        
        # Alert thresholds
        self.thresholds = {
            'response_time_ms': 1000,  # 1 second
            'error_rate': 0.05,        # 5%
            'api_failure_count': 5     # 5 failed API calls
        }
        
        # Alert handlers
        self.alert_handlers = {
            'log': self._log_alert,
            'email': self._email_alert
        }
        
        # Alert history
        self.alert_history = []
        
        # Alert status (to avoid repeated alerts)
        self.alert_status = {
            'response_time': False,
            'error_rate': False,
            'api_failure': False
        }
        
        # Start monitoring thread
        self.running = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval_seconds: int = 60) -> None:
        """
        Start monitoring for alerts.
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(interval_seconds,)
            )
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info(f"Alert monitoring started with {interval_seconds}s interval")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring for alerts."""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
            logger.info("Alert monitoring stopped")
    
    def set_threshold(self, alert_type: str, threshold: float) -> None:
        """
        Set an alert threshold.
        
        Args:
            alert_type: The type of alert
            threshold: The threshold value
        """
        self.thresholds[alert_type] = threshold
        logger.info(f"Alert threshold set: {alert_type} = {threshold}")
    
    def add_alert_handler(self, handler_name: str, handler_func: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Add a custom alert handler.
        
        Args:
            handler_name: The name of the handler
            handler_func: The handler function
        """
        self.alert_handlers[handler_name] = handler_func
        logger.info(f"Alert handler added: {handler_name}")
    
    def trigger_alert(self, alert_type: str, details: Dict[str, Any], 
                      handlers: Optional[List[str]] = None) -> None:
        """
        Trigger an alert.
        
        Args:
            alert_type: The type of alert
            details: Alert details
            handlers: Optional list of handlers to use
        """
        # Add timestamp to details
        details['timestamp'] = datetime.now().isoformat()
        
        # Create alert
        alert = {
            'type': alert_type,
            'details': details
        }
        
        # Add to history
        self.alert_history.append(alert)
        
        # Limit history size
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # Use specified handlers or all handlers
        handler_list = handlers if handlers else list(self.alert_handlers.keys())
        
        # Process alert with handlers
        for handler_name in handler_list:
            if handler_name in self.alert_handlers:
                try:
                    self.alert_handlers[handler_name](alert_type, details)
                except Exception as e:
                    logger.error(f"Error in alert handler {handler_name}: {str(e)}")
    
    def get_alert_history(self, alert_type: Optional[str] = None, 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get alert history.
        
        Args:
            alert_type: Optional alert type to filter by
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        # Filter by alert type if specified
        filtered_alerts = self.alert_history
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a['type'] == alert_type]
        
        # Return limited number of alerts
        return filtered_alerts[-limit:]
    
    def _monitor_loop(self, interval_seconds: int) -> None:
        """Monitor metrics for alerts."""
        while self.running:
            try:
                # Check response time
                avg_response_time = self.metrics_collector.get_average_response_time()
                if avg_response_time > self.thresholds['response_time_ms']:
                    if not self.alert_status['response_time']:
                        self.trigger_alert(
                            'response_time',
                            {
                                'value': avg_response_time,
                                'threshold': self.thresholds['response_time_ms']
                            }
                        )
                        self.alert_status['response_time'] = True
                else:
                    # Reset alert status
                    self.alert_status['response_time'] = False
                
                # Check error rate
                error_rate = self.metrics_collector.get_error_rate()['total_rate']
                if error_rate > self.thresholds['error_rate']:
                    if not self.alert_status['error_rate']:
                        self.trigger_alert(
                            'error_rate',
                            {
                                'value': error_rate,
                                'threshold': self.thresholds['error_rate']
                            }
                        )
                        self.alert_status['error_rate'] = True
                else:
                    # Reset alert status
                    self.alert_status['error_rate'] = False
            except Exception as e:
                logger.error(f"Error in alert monitoring: {str(e)}")
            
            # Sleep for the interval
            time.sleep(interval_seconds)
    
    def _log_alert(self, alert_type: str, details: Dict[str, Any]) -> None:
        """Log an alert."""
        logger.warning(f"ALERT [{alert_type}]: {details}")
    
    def _email_alert(self, alert_type: str, details: Dict[str, Any]) -> None:
        """Send an email alert."""
        # This is a placeholder implementation that logs the action
        # In a real implementation, this would send an email
        logger.info(f"Would send email for alert: {alert_type} - {details}")