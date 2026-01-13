"""
Système de logging détaillé pour le débogage
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class DetailedLogger:
    """Logger détaillé avec fichiers et console"""
    
    def __init__(self, name: str, log_dir: str = "./logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Créer le logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Formatter détaillé
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler fichier avec rotation
        file_handler = logging.FileHandler(
            self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(detailed_formatter)
        
        # Ajouter les handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str, extra_data: Optional[dict] = None):
        """Log niveau debug"""
        if extra_data:
            message += f" | Data: {extra_data}"
        self.logger.debug(message)
    
    def info(self, message: str, extra_data: Optional[dict] = None):
        """Log niveau info"""
        if extra_data:
            message += f" | Data: {extra_data}"
        self.logger.info(message)
    
    def warning(self, message: str, extra_data: Optional[dict] = None):
        """Log niveau warning"""
        if extra_data:
            message += f" | Data: {extra_data}"
        self.logger.warning(message)
    
    def error(self, message: str, error: Optional[Exception] = None, extra_data: Optional[dict] = None):
        """Log niveau error avec exception"""
        if error:
            message += f" | Exception: {type(error).__name__}: {str(error)}"
        if extra_data:
            message += f" | Data: {extra_data}"
        self.logger.error(message, exc_info=error is not None)
    
    def critical(self, message: str, error: Optional[Exception] = None, extra_data: Optional[dict] = None):
        """Log niveau critical"""
        if error:
            message += f" | Exception: {type(error).__name__}: {str(error)}"
        if extra_data:
            message += f" | Data: {extra_data}"
        self.logger.critical(message, exc_info=error is not None)

# Loggers globaux
app_logger = DetailedLogger("app")
api_logger = DetailedLogger("api")
startup_logger = DetailedLogger("startup")
