"""
🔍 Улучшенная система логирования для DianaLisaBot
Детальное логирование всех операций с цветным выводом и структурированными данными
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import json
import traceback
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    """Форматтер с цветным выводом для консоли"""
    
    # Цвета для разных уровней логирования
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Добавляем цвет к уровню логирования
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class StructuredLogger:
    """Структурированный логгер с детальным выводом"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Создаем логгер
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Настраиваем обработчики
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков логирования"""
        
        # 1. Консольный обработчик с цветами
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 2. Файловый обработчик для всех логов
        file_handler = logging.FileHandler(
            self.log_dir / f"{self.name}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 3. Обработчик для ошибок
        error_handler = logging.FileHandler(
            self.log_dir / "errors.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # 4. Обработчик для аналитики
        analytics_handler = logging.FileHandler(
            self.log_dir / "analytics.log",
            encoding='utf-8'
        )
        analytics_handler.setLevel(logging.INFO)
        analytics_formatter = logging.Formatter(
            '%(asctime)s - ANALYTICS - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        analytics_handler.setFormatter(analytics_formatter)
        self.logger.addHandler(analytics_handler)
    
    def log_user_action(self, user_id: int, action: str, details: Dict[str, Any] = None):
        """Логирование действий пользователя"""
        log_data = {
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(f"USER_ACTION: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_database_operation(self, operation: str, table: str, data: Dict[str, Any] = None):
        """Логирование операций с базой данных"""
        log_data = {
            'operation': operation,
            'table': table,
            'timestamp': datetime.now().isoformat(),
            'data': data or {}
        }
        
        self.logger.debug(f"DB_OPERATION: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, response_time: float = None):
        """Логирование API запросов"""
        log_data = {
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': response_time,
            'timestamp': datetime.now().isoformat()
        }
        
        level = logging.INFO if status_code < 400 else logging.WARNING
        self.logger.log(level, f"API_REQUEST: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Логирование производительности"""
        log_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        level = logging.INFO if duration < 1.0 else logging.WARNING
        self.logger.log(level, f"PERFORMANCE: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Детальное логирование ошибок"""
        log_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        self.logger.error(f"ERROR: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_analytics_event(self, user_id: int, event_type: str, event_data: Dict[str, Any] = None):
        """Логирование событий аналитики"""
        log_data = {
            'user_id': user_id,
            'event_type': event_type,
            'event_data': event_data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Отправляем в отдельный файл аналитики
        analytics_logger = logging.getLogger('analytics')
        analytics_logger.info(json.dumps(log_data, ensure_ascii=False))

class TestLogger:
    """Специальный логгер для тестов"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.logger = logging.getLogger(f"test_{test_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Очищаем обработчики
        self.logger.handlers.clear()
        
        # Добавляем обработчик для тестов
        handler = logging.FileHandler(f"logs/test_{test_name}.log", encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_test_start(self, test_description: str):
        """Логирование начала теста"""
        self.logger.info(f"=== НАЧАЛО ТЕСТА: {test_description} ===")
    
    def log_test_end(self, test_description: str, success: bool):
        """Логирование окончания теста"""
        status = "УСПЕШНО" if success else "ПРОВАЛЕН"
        self.logger.info(f"=== КОНЕЦ ТЕСТА: {test_description} - {status} ===")
    
    def log_test_step(self, step: str, details: Dict[str, Any] = None):
        """Логирование шага теста"""
        log_data = {
            'step': step,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(f"ШАГ: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_assertion(self, assertion: str, result: bool, expected: Any = None, actual: Any = None):
        """Логирование проверок"""
        log_data = {
            'assertion': assertion,
            'result': result,
            'expected': expected,
            'actual': actual,
            'timestamp': datetime.now().isoformat()
        }
        
        level = logging.INFO if result else logging.ERROR
        self.logger.log(level, f"ПРОВЕРКА: {json.dumps(log_data, ensure_ascii=False)}")

# Глобальные логгеры
main_logger = StructuredLogger("diana_lisa_bot")

def get_logger(name: str) -> StructuredLogger:
    """Получение логгера по имени"""
    return StructuredLogger(name)

def log_function_call(func_name: str, args: tuple = None, kwargs: dict = None):
    """Декоратор для логирования вызовов функций"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.logger.debug(f"Вызов функции {func_name} с аргументами: args={args}, kwargs={kwargs}")
            
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(f"function_{func_name}", duration)
                return result
            except Exception as e:
                logger.log_error(e, {'function': func_name, 'args': args, 'kwargs': kwargs})
                raise
        return wrapper
    return decorator
