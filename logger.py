"""
📝 Система логирования для бота DianaLisa
Настройка логирования, ротация логов и мониторинг
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

class LoggerSetup:
    """Класс для настройки системы логирования"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Настройки логирования
        self.log_level = logging.INFO
        self.max_file_size = 10 * 1024 * 1024  # 10 MB
        self.backup_count = 5
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.date_format = '%Y-%m-%d %H:%M:%S'
    
    def setup_logging(self):
        """Настройка системы логирования"""
        try:
            # Отключаем логирование httpx (HTTP запросы)
            logging.getLogger("httpx").setLevel(logging.CRITICAL)
            logging.getLogger("httpx").disabled = True
            
            # Создаем основной логгер
            logger = logging.getLogger()
            logger.setLevel(self.log_level)
            
            # Очищаем существующие обработчики
            logger.handlers.clear()
            
            # Создаем форматтер
            formatter = logging.Formatter(
                self.log_format,
                datefmt=self.date_format
            )
            
            # Обработчик для консоли
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # Обработчик для файла общих логов
            general_log_file = self.log_dir / "dianalisa_bot.log"
            general_handler = logging.handlers.RotatingFileHandler(
                general_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            general_handler.setLevel(logging.DEBUG)
            general_handler.setFormatter(formatter)
            logger.addHandler(general_handler)
            
            # Обработчик для ошибок
            error_log_file = self.log_dir / "errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)
            
            # Обработчик для пользовательских действий
            user_log_file = self.log_dir / "user_actions.log"
            user_handler = logging.handlers.RotatingFileHandler(
                user_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            user_handler.setLevel(logging.INFO)
            user_handler.setFormatter(formatter)
            logger.addHandler(user_handler)
            
            # Обработчик для платежей
            payment_log_file = self.log_dir / "payments.log"
            payment_handler = logging.handlers.RotatingFileHandler(
                payment_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            payment_handler.setLevel(logging.INFO)
            payment_handler.setFormatter(formatter)
            logger.addHandler(payment_handler)
            
            # Обработчик для админских действий
            admin_log_file = self.log_dir / "admin_actions.log"
            admin_handler = logging.handlers.RotatingFileHandler(
                admin_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            admin_handler.setLevel(logging.INFO)
            admin_handler.setFormatter(formatter)
            logger.addHandler(admin_handler)
            
            # Настраиваем логгеры для конкретных модулей
            self.setup_module_loggers()
            
            logging.info("Система логирования настроена успешно")
            
        except Exception as e:
            print(f"Ошибка настройки логирования: {e}")
            sys.exit(1)
    
    def setup_module_loggers(self):
        """Настройка логгеров для конкретных модулей"""
        try:
            # Логгер для базы данных
            db_logger = logging.getLogger('database')
            db_logger.setLevel(logging.DEBUG)
            
            # Логгер для платежей
            payment_logger = logging.getLogger('payment')
            payment_logger.setLevel(logging.INFO)
            
            # Логгер для админки
            admin_logger = logging.getLogger('admin')
            admin_logger.setLevel(logging.INFO)
            
            # Логгер для тренировок
            training_logger = logging.getLogger('training')
            training_logger.setLevel(logging.INFO)
            
            # Логгер для планировщика
            scheduler_logger = logging.getLogger('scheduler')
            scheduler_logger.setLevel(logging.INFO)
            
            # Логгер для регистрации
            registration_logger = logging.getLogger('registration')
            registration_logger.setLevel(logging.INFO)
            
            # Логгер для callback-ов
            callback_logger = logging.getLogger('callbacks')
            callback_logger.setLevel(logging.INFO)
            
        except Exception as e:
            logging.error(f"Ошибка настройки модульных логгеров: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Получение логгера по имени"""
        return logging.getLogger(name)
    
    def log_user_action(self, user_id: int, action: str, details: str = None):
        """Логирование действий пользователя"""
        try:
            logger = logging.getLogger('user_actions')
            message = f"User {user_id}: {action}"
            if details:
                message += f" - {details}"
            logger.info(message)
        except Exception as e:
            logging.error(f"Ошибка логирования действия пользователя: {e}")
    
    def log_payment(self, user_id: int, amount: float, currency: str, status: str, transaction_id: str):
        """Логирование платежей"""
        try:
            logger = logging.getLogger('payments')
            message = f"Payment - User: {user_id}, Amount: {amount} {currency}, Status: {status}, Transaction: {transaction_id}"
            logger.info(message)
        except Exception as e:
            logging.error(f"Ошибка логирования платежа: {e}")
    
    def log_admin_action(self, admin_id: int, action: str, target: str = None):
        """Логирование админских действий"""
        try:
            logger = logging.getLogger('admin_actions')
            message = f"Admin {admin_id}: {action}"
            if target:
                message += f" - Target: {target}"
            logger.info(message)
        except Exception as e:
            logging.error(f"Ошибка логирования админского действия: {e}")
    
    def log_error(self, error: Exception, context: str = None):
        """Логирование ошибок"""
        try:
            logger = logging.getLogger('errors')
            message = f"Error: {str(error)}"
            if context:
                message += f" - Context: {context}"
            logger.error(message, exc_info=True)
        except Exception as e:
            print(f"Критическая ошибка логирования: {e}")
    
    def log_performance(self, operation: str, duration: float, details: str = None):
        """Логирование производительности"""
        try:
            logger = logging.getLogger('performance')
            message = f"Performance - {operation}: {duration:.3f}s"
            if details:
                message += f" - {details}"
            logger.info(message)
        except Exception as e:
            logging.error(f"Ошибка логирования производительности: {e}")
    
    def cleanup_old_logs(self, days: int = 30):
        """Очистка старых логов"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    logging.info(f"Удален старый лог файл: {log_file}")
            
        except Exception as e:
            logging.error(f"Ошибка очистки старых логов: {e}")
    
    def get_log_stats(self) -> dict:
        """Получение статистики логов"""
        try:
            stats = {}
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.name.endswith('.log'):
                    stats[log_file.name] = {
                        'size': log_file.stat().st_size,
                        'modified': datetime.fromtimestamp(log_file.stat().st_mtime),
                        'lines': self.count_lines(log_file)
                    }
            
            return stats
            
        except Exception as e:
            logging.error(f"Ошибка получения статистики логов: {e}")
            return {}
    
    def count_lines(self, file_path: Path) -> int:
        """Подсчет строк в файле"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception as e:
            logging.error(f"Ошибка подсчета строк в файле {file_path}: {e}")
            return 0
    
    def set_log_level(self, level: str):
        """Установка уровня логирования"""
        try:
            level_map = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            
            if level.upper() in level_map:
                self.log_level = level_map[level.upper()]
                logging.getLogger().setLevel(self.log_level)
                logging.info(f"Уровень логирования изменен на {level.upper()}")
            else:
                logging.warning(f"Неизвестный уровень логирования: {level}")
                
        except Exception as e:
            logging.error(f"Ошибка установки уровня логирования: {e}")

# Глобальный экземпляр системы логирования
logger_setup = LoggerSetup()

def setup_logging():
    """Функция для настройки логирования"""
    logger_setup.setup_logging()

def get_logger(name: str) -> logging.Logger:
    """Получение логгера по имени"""
    return logger_setup.get_logger(name)

def log_user_action(user_id: int, action: str, details: str = None):
    """Логирование действий пользователя"""
    logger_setup.log_user_action(user_id, action, details)

def log_payment(user_id: int, amount: float, currency: str, status: str, transaction_id: str):
    """Логирование платежей"""
    logger_setup.log_payment(user_id, amount, currency, status, transaction_id)

def log_admin_action(admin_id: int, action: str, target: str = None):
    """Логирование админских действий"""
    logger_setup.log_admin_action(admin_id, action, target)

def log_error(error: Exception, context: str = None):
    """Логирование ошибок"""
    logger_setup.log_error(error, context)

def log_performance(operation: str, duration: float, details: str = None):
    """Логирование производительности"""
    logger_setup.log_performance(operation, duration, details)
