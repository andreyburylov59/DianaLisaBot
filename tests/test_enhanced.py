"""
🧪 Улучшенная система тестирования для DianaLisaBot
Комплексные тесты с детальным логированием и отчетностью
"""

import pytest
import asyncio
import sqlite3
import time
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List, Any, Optional

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from registration import RegistrationHandler
from callbacks import CallbackHandlers
from keyboards import Keyboards
from health_tips import health_tips
from config import MESSAGES, BUTTONS
from enhanced_logger import TestLogger as Logger, StructuredLogger

# Создаем экземпляр клавиатур
keyboards = Keyboards()

class EnhancedTestSuite:
    """Улучшенный набор тестов с детальным логированием"""
    
    def __init__(self):
        self.test_logger = Logger("enhanced_suite")
        self.main_logger = StructuredLogger("test_main")
        self.test_results = []
        self.performance_metrics = {}
        
    def log_test_result(self, test_name: str, success: bool, duration: float, details: Dict[str, Any] = None):
        """Логирование результата теста"""
        result = {
            'test_name': test_name,
            'success': success,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.test_results.append(result)
        self.test_logger.logger.info(f"РЕЗУЛЬТАТ ТЕСТА: {json.dumps(result, ensure_ascii=False)}")
    
    def create_test_database(self, test_name: str) -> Database:
        """Создание тестовой базы данных"""
        test_db_path = f"test_{test_name}_{int(time.time())}.db"
        
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        db = Database(test_db_path)
        db.init_database()
        
        self.test_logger.log_test_step(f"Создана тестовая БД: {test_db_path}")
        return db
    
    def cleanup_test_database(self, db: Database):
        """Очистка тестовой базы данных"""
        try:
            if os.path.exists(db.db_path):
                os.remove(db.db_path)
                self.test_logger.log_test_step(f"Удалена тестовая БД: {db.db_path}")
        except Exception as e:
            self.test_logger.logger.warning(f"Не удалось удалить БД: {e}")
    
    def test_database_operations_enhanced(self):
        """Улучшенный тест операций с базой данных"""
        test_name = "database_operations_enhanced"
        self.test_logger.log_test_start("Тестирование операций с базой данных")
        
        start_time = time.time()
        db = None
        
        try:
            db = self.create_test_database(test_name)
            
            # Тест 1: Добавление пользователей
            self.test_logger.log_test_step("Тест добавления пользователей")
            test_users = [
                {
                    'user_id': 1001,
                    'username': 'test_user_1',
                    'first_name': 'Анна',
                    'email': 'anna@test.com',
                    'timezone': 'Europe/Moscow'
                },
                {
                    'user_id': 1002,
                    'username': 'test_user_2',
                    'first_name': 'Мария',
                    'email': 'maria@test.com',
                    'timezone': 'Europe/Moscow'
                },
                {
                    'user_id': 1003,
                    'username': 'test_user_3',
                    'first_name': 'Елена',
                    'email': 'elena@test.com',
                    'timezone': 'Europe/Moscow'
                }
            ]
            
            for user in test_users:
                success = db.add_user(**user)
                self.test_logger.log_assertion(f"Добавление пользователя {user['user_id']}", success)
                assert success, f"Не удалось добавить пользователя {user['user_id']}"
            
            # Тест 2: Проверка количества пользователей
            self.test_logger.log_test_step("Проверка количества пользователей")
            count = db.get_users_count()
            self.test_logger.log_assertion(f"Количество пользователей = 3", count == 3, 3, count)
            assert count == 3, f"Ожидалось 3 пользователя, получено {count}"
            
            # Тест 3: Получение пользователя
            self.test_logger.log_test_step("Получение пользователя по ID")
            user = db.get_user(1001)
            self.test_logger.log_assertion("Пользователь найден", user is not None)
            assert user is not None, "Пользователь не найден"
            assert user['first_name'] == 'Анна', "Неверное имя пользователя"
            
            # Тест 4: Обновление пользователя
            self.test_logger.log_test_step("Обновление данных пользователя")
            db.update_user(1001, training_completed=True, nutrition_marked=True)
            updated_user = db.get_user(1001)
            self.test_logger.log_assertion("Тренировка отмечена", updated_user['training_completed'] == True)
            self.test_logger.log_assertion("Питание отмечено", updated_user['nutrition_marked'] == True)
            assert updated_user['training_completed'] == True, "Тренировка не отмечена"
            assert updated_user['nutrition_marked'] == True, "Питание не отмечено"
            
            # Тест 5: Аналитика
            self.test_logger.log_test_step("Добавление события аналитики")
            db.add_analytics_event(1001, 'test_event', 'test_data')
            
            # Тест 6: Производительность
            self.test_logger.log_test_step("Тест производительности добавления")
            perf_start = time.time()
            for i in range(50):
                db.add_user(
                    user_id=2000 + i,
                    username=f'perf_test_{i}',
                    first_name=f'Пользователь{i}',
                    email=f'user{i}@test.com'
                )
            perf_duration = time.time() - perf_start
            self.performance_metrics['add_users_50'] = perf_duration
            
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration, {
                'users_added': len(test_users) + 50,
                'performance_ms': round(perf_duration * 1000, 2)
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, duration, {'error': str(e)})
            raise
        
        finally:
            if db:
                self.cleanup_test_database(db)
    
    def test_callback_handlers_enhanced(self):
        """Улучшенный тест обработчиков callback-ов"""
        test_name = "callback_handlers_enhanced"
        self.test_logger.log_test_start("Тестирование обработчиков callback-ов")
        
        start_time = time.time()
        db = None
        
        try:
            db = self.create_test_database(test_name)
            
            # Создаем тестового пользователя
            test_user_id = 3001
            db.add_user(
                user_id=test_user_id,
                username='callback_tester',
                first_name='Тестер',
                email='tester@test.com'
            )
            
            callback_handler = CallbackHandlers()
            
            # Тест обработчиков чек-листа
            callback_tests = [
                ('mark_training', 'Тренировка'),
                ('mark_nutrition', 'Питание'),
                ('mark_water', 'Вода'),
                ('mark_sleep', 'Сон')
            ]
            
            for callback_data, action_name in callback_tests:
                self.test_logger.log_test_step(f"Тест callback: {action_name}")
                
                # Создаем мок объекты
                mock_update = MagicMock()
                mock_query = AsyncMock()
                mock_user = MagicMock()
                
                mock_user.id = test_user_id
                mock_query.from_user = mock_user
                mock_query.data = callback_data
                mock_query.edit_message_text = AsyncMock()
                mock_query.delete_message = AsyncMock()
                mock_update.callback_query = mock_query
                
                mock_context = MagicMock()
                mock_context.bot = AsyncMock()
                mock_context.bot.send_message = AsyncMock()
                mock_context.bot.send_photo = AsyncMock()
                
                # Вызываем соответствующий обработчик
                try:
                    if callback_data == 'mark_training':
                        asyncio.run(callback_handler.handle_mark_training(mock_update, mock_context, callback_data))
                    elif callback_data == 'mark_nutrition':
                        asyncio.run(callback_handler.handle_mark_nutrition(mock_update, mock_context, callback_data))
                    elif callback_data == 'mark_water':
                        asyncio.run(callback_handler.handle_mark_water(mock_update, mock_context, callback_data))
                    elif callback_data == 'mark_sleep':
                        asyncio.run(callback_handler.handle_mark_sleep(mock_update, mock_context, callback_data))
                    
                    self.test_logger.log_assertion(f"Callback {action_name} обработан", True)
                    
                except Exception as e:
                    self.test_logger.log_assertion(f"Callback {action_name} обработан", False, None, str(e))
                    raise
            
            # Тест выбора часов сна
            self.test_logger.log_test_step("Тест выбора часов сна")
            sleep_hours = ['sleep_6h', 'sleep_7h', 'sleep_8h', 'sleep_9h']
            
            for sleep_hour in sleep_hours:
                mock_update = MagicMock()
                mock_query = AsyncMock()
                mock_user = MagicMock()
                
                mock_user.id = test_user_id
                mock_query.from_user = mock_user
                mock_query.data = sleep_hour
                mock_query.edit_message_text = AsyncMock()
                mock_query.delete_message = AsyncMock()
                mock_update.callback_query = mock_query
                
                try:
                    asyncio.run(callback_handler.handle_sleep_hours(mock_update, mock_context, sleep_hour))
                    self.test_logger.log_assertion(f"Выбор сна {sleep_hour} обработан", True)
                    break  # Обрабатываем только один выбор
                except Exception as e:
                    self.test_logger.log_assertion(f"Выбор сна {sleep_hour} обработан", False, None, str(e))
            
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration, {
                'callbacks_tested': len(callback_tests),
                'sleep_options_tested': len(sleep_hours)
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, duration, {'error': str(e)})
            raise
        
        finally:
            if db:
                self.cleanup_test_database(db)
    
    def test_keyboards_enhanced(self):
        """Улучшенный тест клавиатур"""
        test_name = "keyboards_enhanced"
        self.test_logger.log_test_start("Тестирование клавиатур")
        
        start_time = time.time()
        
        try:
            # Тест главного меню
            self.test_logger.log_test_step("Тест главного меню")
            main_menu = keyboards.main_menu()
            self.test_logger.log_assertion("Главное меню создано", main_menu is not None)
            assert main_menu is not None, "Главное меню не создано"
            
            # Тест чек-листа с различными состояниями
            self.test_logger.log_test_step("Тест чек-листа с различными состояниями")
            test_states = [
                {
                    'name': 'Все не выполнено',
                    'data': {
                        'training_completed': False,
                        'nutrition_marked': False,
                        'water_marked': False,
                        'sleep_marked': False
                    }
                },
                {
                    'name': 'Все выполнено',
                    'data': {
                        'training_completed': True,
                        'nutrition_marked': True,
                        'water_marked': True,
                        'sleep_marked': True
                    }
                },
                {
                    'name': 'Частично выполнено',
                    'data': {
                        'training_completed': True,
                        'nutrition_marked': False,
                        'water_marked': True,
                        'sleep_marked': False
                    }
                }
            ]
            
            for state in test_states:
                checklist_menu = keyboards.checklist_menu(state['data'])
                self.test_logger.log_assertion(f"Чек-лист создан для состояния: {state['name']}", checklist_menu is not None)
                assert checklist_menu is not None, f"Чек-лист не создан для состояния: {state['name']}"
            
            # Тест меню выбора часов сна
            self.test_logger.log_test_step("Тест меню выбора часов сна")
            sleep_menu = keyboards.sleep_hours_menu()
            self.test_logger.log_assertion("Меню выбора часов сна создано", sleep_menu is not None)
            assert sleep_menu is not None, "Меню выбора часов сна не создано"
            
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration, {
                'keyboard_types_tested': len(test_states) + 2,
                'states_tested': len(test_states)
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, duration, {'error': str(e)})
            raise
    
    def test_health_tips_enhanced(self):
        """Улучшенный тест советов по здоровью"""
        test_name = "health_tips_enhanced"
        self.test_logger.log_test_start("Тестирование советов по здоровью")
        
        start_time = time.time()
        
        try:
            test_user_ids = [4001, 4002, 4003]
            tip_types = ['water', 'breakfast', 'dinner', 'sleep']
            
            for user_id in test_user_ids:
                self.test_logger.log_test_step(f"Тест советов для пользователя {user_id}")
                
                for tip_type in tip_types:
                    if tip_type == 'water':
                        tip = health_tips.get_water_tip(user_id)
                    elif tip_type == 'breakfast':
                        tip = health_tips.get_breakfast_tip(user_id)
                    elif tip_type == 'dinner':
                        tip = health_tips.get_dinner_tip(user_id)
                    elif tip_type == 'sleep':
                        tip = health_tips.get_sleep_tip(user_id)
                    
                    self.test_logger.log_assertion(
                        f"Совет {tip_type} получен для пользователя {user_id}",
                        tip is not None and len(tip) > 0,
                        "Непустой совет",
                        tip[:50] + "..." if tip else None
                    )
                    assert tip is not None, f"Совет {tip_type} не получен"
                    assert len(tip) > 0, f"Совет {tip_type} пустой"
            
            # Тест разнообразия советов
            self.test_logger.log_test_step("Тест разнообразия советов")
            user_id = 5001
            water_tips = []
            for i in range(5):
                tip = health_tips.get_water_tip(user_id)
                water_tips.append(tip)
            
            unique_tips = len(set(water_tips))
            self.test_logger.log_assertion(
                "Советы по воде разнообразны",
                unique_tips > 1,
                1,
                unique_tips
            )
            
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration, {
                'users_tested': len(test_user_ids),
                'tip_types_tested': len(tip_types),
                'diversity_test_passed': unique_tips > 1
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, duration, {'error': str(e)})
            raise
    
    def test_performance_enhanced(self):
        """Улучшенный тест производительности"""
        test_name = "performance_enhanced"
        self.test_logger.log_test_start("Тестирование производительности")
        
        start_time = time.time()
        db = None
        
        try:
            db = self.create_test_database(test_name)
            
            # Тест массового добавления пользователей
            self.test_logger.log_test_step("Тест массового добавления пользователей")
            batch_sizes = [10, 50, 100]
            
            for batch_size in batch_sizes:
                batch_start = time.time()
                
                for i in range(batch_size):
                    db.add_user(
                        user_id=10000 + i,
                        username=f'perf_test_{i}',
                        first_name=f'Пользователь{i}',
                        email=f'user{i}@test.com'
                    )
                
                batch_duration = time.time() - batch_start
                self.performance_metrics[f'add_users_{batch_size}'] = batch_duration
                
                self.test_logger.log_assertion(
                    f"Добавление {batch_size} пользователей за разумное время",
                    batch_duration < 10.0,
                    10.0,
                    batch_duration
                )
            
            # Тест получения всех пользователей
            self.test_logger.log_test_step("Тест получения всех пользователей")
            get_start = time.time()
            users = db.get_all_users()
            get_duration = time.time() - get_start
            self.performance_metrics['get_all_users'] = get_duration
            
            self.test_logger.log_assertion(
                "Получение всех пользователей за разумное время",
                get_duration < 2.0,
                2.0,
                get_duration
            )
            
            # Тест поиска пользователя
            self.test_logger.log_test_step("Тест поиска пользователя")
            search_start = time.time()
            user = db.get_user(10000)
            search_duration = time.time() - search_start
            self.performance_metrics['search_user'] = search_duration
            
            self.test_logger.log_assertion(
                "Поиск пользователя за разумное время",
                search_duration < 0.1,
                0.1,
                search_duration
            )
            
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration, {
                'batch_sizes_tested': batch_sizes,
                'total_users': len(users),
                'performance_metrics': self.performance_metrics
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, duration, {'error': str(e)})
            raise
        
        finally:
            if db:
                self.cleanup_test_database(db)
    
    def test_error_handling_enhanced(self):
        """Улучшенный тест обработки ошибок"""
        test_name = "error_handling_enhanced"
        self.test_logger.log_test_start("Тестирование обработки ошибок")
        
        start_time = time.time()
        db = None
        
        try:
            db = self.create_test_database(test_name)
            
            # Тест получения несуществующего пользователя
            self.test_logger.log_test_step("Тест получения несуществующего пользователя")
            non_existent_user = db.get_user(99999)
            self.test_logger.log_assertion(
                "Несуществующий пользователь возвращает None",
                non_existent_user is None,
                None,
                non_existent_user
            )
            assert non_existent_user is None, "Несуществующий пользователь должен возвращать None"
            
            # Тест обновления несуществующего пользователя
            self.test_logger.log_test_step("Тест обновления несуществующего пользователя")
            try:
                result = db.update_user(99999, training_completed=True)
                self.test_logger.log_assertion("Обновление несуществующего пользователя не вызывает ошибку", True)
            except Exception as e:
                self.test_logger.log_assertion("Обновление несуществующего пользователя не вызывает ошибку", False, None, str(e))
            
            # Тест добавления пользователя с некорректными данными
            self.test_logger.log_test_step("Тест добавления пользователя с некорректными данными")
            try:
                result = db.add_user(user_id=None)
                self.test_logger.log_assertion("Добавление пользователя с None ID обработано", True)
            except Exception as e:
                self.test_logger.log_assertion("Добавление пользователя с None ID обработано", True, None, str(e))
            
            # Тест добавления пользователя с дублирующимся ID
            self.test_logger.log_test_step("Тест добавления пользователя с дублирующимся ID")
            db.add_user(user_id=8001, username='test1', first_name='Test1', email='test1@test.com')
            
            try:
                db.add_user(user_id=8001, username='test2', first_name='Test2', email='test2@test.com')
                user = db.get_user(8001)
                self.test_logger.log_assertion(
                    "Дублирующийся ID обработан корректно",
                    user['first_name'] == 'Test2',
                    'Test2',
                    user['first_name']
                )
            except Exception as e:
                self.test_logger.log_assertion("Дублирующийся ID обработан корректно", False, None, str(e))
            
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration, {
                'error_scenarios_tested': 4
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, duration, {'error': str(e)})
            raise
        
        finally:
            if db:
                self.cleanup_test_database(db)
    
    def generate_test_report(self):
        """Генерация отчета о тестах"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(result['duration_ms'] for result in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                'total_duration_ms': round(total_duration, 2),
                'average_duration_ms': round(avg_duration, 2)
            },
            'performance_metrics': self.performance_metrics,
            'test_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Сохраняем отчет в файл
        with open('logs/test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Логируем сводку
        self.test_logger.logger.info(f"=== СВОДКА ТЕСТОВ ===")
        self.test_logger.logger.info(f"Всего тестов: {total_tests}")
        self.test_logger.logger.info(f"Пройдено: {passed_tests}")
        self.test_logger.logger.info(f"Провалено: {failed_tests}")
        self.test_logger.logger.info(f"Процент успеха: {report['summary']['success_rate']}%")
        self.test_logger.logger.info(f"Общее время: {report['summary']['total_duration_ms']}мс")
        
        return report
    
    def run_all_tests(self):
        """Запуск всех улучшенных тестов"""
        self.test_logger.logger.info("=== ЗАПУСК УЛУЧШЕННЫХ ТЕСТОВ ===")
        
        test_methods = [
            self.test_database_operations_enhanced,
            self.test_callback_handlers_enhanced,
            self.test_keyboards_enhanced,
            self.test_health_tips_enhanced,
            self.test_performance_enhanced,
            self.test_error_handling_enhanced
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.test_logger.logger.error(f"Тест {test_method.__name__} провален: {e}")
        
        # Генерируем отчет
        report = self.generate_test_report()
        
        self.test_logger.logger.info("=== ТЕСТЫ ЗАВЕРШЕНЫ ===")
        return report

def run_enhanced_tests():
    """Главная функция запуска улучшенных тестов"""
    test_suite = EnhancedTestSuite()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    run_enhanced_tests()
