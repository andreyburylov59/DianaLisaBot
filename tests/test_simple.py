"""
Интеграционные тесты для DianaLisaBot
Автоматическое тестирование всех функций бота
"""

import pytest
import asyncio
import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import os
import sys

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from registration import RegistrationHandler
from callbacks import CallbackHandlers
from keyboards import Keyboards
from health_tips import health_tips
from config import MESSAGES, BUTTONS
import tempfile
import shutil

# Глобальная фикстура для базы данных
@pytest.fixture(scope="session")
def temp_db():
    """Создает временную базу данных для всех тестов"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_session.db")
    db = Database(db_path)
    db.init_database()
    yield db
    # Очистка после всех тестов
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

@pytest.fixture(scope="function")
def clean_db(temp_db):
    """Очищает базу данных перед каждым тестом"""
    # Очищаем все таблицы
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM analytics")
        cursor.execute("DELETE FROM scheduled_jobs")
        cursor.execute("DELETE FROM payments")
        cursor.execute("DELETE FROM training_feedback")
        conn.commit()
    return temp_db

# Создаем экземпляр клавиатур
keyboards = Keyboards()

class TestDianaLisaBotIntegration:
    """Интеграционные тесты для всех функций бота"""
    
    def test_database_operations(self, clean_db):
        """Тест операций с базой данных"""
        print("\nТестирование операций с базой данных...")
        
        db = clean_db
        
        # Тест добавления пользователей
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
        
        # Добавляем пользователей
        for user in test_users:
            success = db.add_user(**user)
            assert success, f"Не удалось добавить пользователя {user['user_id']}"
            print(f"OK: Пользователь {user['first_name']} добавлен")
        
        # Проверяем количество пользователей
        count = db.get_users_count()
        assert count == 3, f"Ожидалось 3 пользователя, получено {count}"
        print(f"OK: Количество пользователей: {count}")
        
        # Тест получения пользователя
        user = db.get_user(1001)
        assert user is not None, "Пользователь не найден"
        assert user['first_name'] == 'Анна', "Неверное имя пользователя"
        print(f"OK: Пользователь найден: {user['first_name']}")
        
        # Тест обновления пользователя
        db.update_user(1001, training_completed=True)
        updated_user = db.get_user(1001)
        assert updated_user['training_completed'] == True, "Тренировка не отмечена"
        print("OK: Пользователь обновлен")
        
        # Тест аналитики
        db.add_analytics_event(1001, 'test_event', 'test_data')
        print("OK: Событие аналитики добавлено")
    
    def test_keyboards(self):
        """Тест клавиатур"""
        print("\nТестирование клавиатур...")
        
        # Тест главного меню
        main_menu = keyboards.main_menu()
        assert main_menu is not None, "Главное меню не создано"
        print("OK: Главное меню создано")
        
        # Тест главного меню
        main_menu = keyboards.main_menu()
        assert main_menu is not None, "Главное меню не создано"
        print("OK: Главное меню создано")
    
    def test_health_tips(self):
        """Тест советов по здоровью"""
        print("\nТестирование советов по здоровью...")
        
        test_user_id = 3001
        
        # Тест советов по завтраку
        breakfast_tip = health_tips.get_breakfast_tip(test_user_id)
        assert breakfast_tip is not None, "Совет по завтраку не получен"
        assert len(breakfast_tip) > 0, "Совет по завтраку пустой"
        print(f"OK: Совет по завтраку: {breakfast_tip[:50].replace('💧', '').replace('🌅', '').replace('🌙', '').replace('😴', '')}...")
        
        # Тест советов по ужину
        dinner_tip = health_tips.get_dinner_tip(test_user_id)
        assert dinner_tip is not None, "Совет по ужину не получен"
        assert len(dinner_tip) > 0, "Совет по ужину пустой"
        print(f"OK: Совет по ужину: {dinner_tip[:50].replace('💧', '').replace('🌅', '').replace('🌙', '').replace('😴', '')}...")
        
        print("OK: Все советы по здоровью работают корректно")
    
    def test_user_progress_scenarios(self, clean_db):
        """Тест различных сценариев прогресса пользователей"""
        print("\nТестирование сценариев прогресса пользователей...")
        
        db = clean_db
        
        # Сценарий 1: Новый пользователь
        user1 = {
            'user_id': 4001,
            'username': 'newbie',
            'first_name': 'Новичок',
            'email': 'newbie@test.com',
            'timezone': 'Europe/Moscow'
        }
        db.add_user(**user1)
        user1_data = db.get_user(4001)
        assert user1_data['training_completed'] == False, "Новый пользователь не должен иметь выполненные тренировки"
        assert user1_data['current_day'] == 1, "Новый пользователь должен быть на 1 дне"
        print("OK: Сценарий 1: Новый пользователь")
        
        # Сценарий 2: Активный пользователь
        user2 = {
            'user_id': 4002,
            'username': 'active',
            'first_name': 'Активный',
            'email': 'active@test.com',
            'timezone': 'Europe/Moscow'
        }
        db.add_user(**user2)
        db.update_user(4002, 
                      training_completed=True,
                      current_day=2)
        user2_data = db.get_user(4002)
        assert user2_data['training_completed'] == True, "Активный пользователь должен иметь выполненные тренировки"
        assert user2_data['current_day'] == 2, "Активный пользователь должен быть на 2 дне"
        print("OK: Сценарий 2: Активный пользователь")
        
        # Сценарий 3: Премиум пользователь
        user3 = {
            'user_id': 4003,
            'username': 'premium',
            'first_name': 'Премиум',
            'email': 'premium@test.com',
            'timezone': 'Europe/Moscow'
        }
        db.add_user(**user3)
        db.update_user(4003,
                      is_premium=True,
                      premium_expires=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
                      current_day=3)
        user3_data = db.get_user(4003)
        assert user3_data['is_premium'] == True, "Премиум пользователь должен иметь премиум статус"
        assert user3_data['current_day'] == 3, "Премиум пользователь должен быть на 3 дне"
        print("OK: Сценарий 3: Премиум пользователь")
    
    def test_performance(self, clean_db):
        """Тест производительности"""
        print("\nТестирование производительности...")
        
        db = clean_db
        import time
        
        # Тест массового добавления пользователей
        start_time = time.time()
        
        for i in range(100):
            db.add_user(
                user_id=6000 + i,
                username=f'perf_test_{i}',
                first_name=f'Пользователь{i}',
                email=f'user{i}@test.com'
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"OK: Добавлено 100 пользователей за {duration:.2f} секунд")
        assert duration < 15.0, f"Добавление пользователей заняло слишком много времени: {duration:.2f}с"
        
        # Тест получения всех пользователей
        start_time = time.time()
        users = db.get_all_users()
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"OK: Получено {len(users)} пользователей за {duration:.2f} секунд")
        assert duration < 1.0, f"Получение пользователей заняло слишком много времени: {duration:.2f}с"

if __name__ == "__main__":
    # Запуск тестов через pytest
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
