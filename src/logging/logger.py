"""Verbose logger — step-by-step trace."""

import logging
from datetime import datetime
from typing import Any, Optional
from .formatters import format_step, format_error, format_success


class VerboseLogger:
    """Logger for verbose agent trace output."""
    
    def __init__(self, name: str = "agent", level: int = logging.INFO):
        """
        Initialize verbose logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Console handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log(self, message: str, level: str = "info", **kwargs):
        """
        Log a message.
        
        Args:
            message: Message to log
            level: Log level (info, debug, warning, error)
            **kwargs: Additional context
        """
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(message)
    
    def log_step(self, step_num: int, description: str):
        """Log an agent step."""
        self.log(format_step(step_num, description))
    
    def log_error(self, error: str):
        """Log an error."""
        self.log(format_error(error), level="error")
    
    def log_success(self, message: str):
        """Log a success message."""
        self.log(format_success(message))
    
    def log_tool_call(self, tool_name: str, inputs: dict):
        """Log a tool call."""
        self.log(f"🔧 Calling tool: {tool_name} with inputs: {inputs}")
    
    def log_tool_result(self, tool_name: str, result: Any):
        """Log tool result."""
        self.log(f"✓ Tool result: {result}")
