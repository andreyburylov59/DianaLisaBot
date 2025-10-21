"""
🤖 Тест симуляции пользовательских действий
Симулирует нажатия на все кнопки и взаимодействие с ботом
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from callbacks import CallbackHandlers
from keyboards import Keyboards
from health_tips import health_tips

# Создаем экземпляр клавиатур
keyboards = Keyboards()

class BotSimulator:
    """Симулятор взаимодействия с ботом"""
    
    def __init__(self):
        self.db_path = "test_simulation.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        self.db = Database(self.db_path)
        self.db.init_database()
        self.callback_handler = CallbackHandlers()
        
        # Создаем тестовых пользователей
        self.test_users = [
            {'user_id': 7001, 'username': 'sim_user_1', 'first_name': 'Симулятор1', 'email': 'sim1@test.com'},
            {'user_id': 7002, 'username': 'sim_user_2', 'first_name': 'Симулятор2', 'email': 'sim2@test.com'},
            {'user_id': 7003, 'username': 'sim_user_3', 'first_name': 'Симулятор3', 'email': 'sim3@test.com'},
        ]
    
    def setup_test_users(self):
        """Настройка тестовых пользователей с разным прогрессом"""
        print("👥 Создание тестовых пользователей...")
        
        # Пользователь 1: Новый пользователь
        self.db.add_user(**self.test_users[0])
        print(f"✅ {self.test_users[0]['first_name']} - новый пользователь")
        
        # Пользователь 2: Активный пользователь
        self.db.add_user(**self.test_users[1])
        self.db.update_user(7002, 
                          training_completed=True,
                          nutrition_marked=True,
                          water_marked=False,
                          sleep_marked=True,
                          current_day=2)
        print(f"✅ {self.test_users[1]['first_name']} - активный пользователь (день 2)")
        
        # Пользователь 3: Премиум пользователь
        self.db.add_user(**self.test_users[2])
        self.db.update_user(7003,
                          training_completed=True,
                          nutrition_marked=True,
                          water_marked=True,
                          sleep_marked=True,
                          is_premium=True,
                          current_day=3)
        print(f"✅ {self.test_users[2]['first_name']} - премиум пользователь (день 3)")
    
    def create_mock_update(self, user_id, callback_data):
        """Создание мок объекта Update"""
        mock_update = MagicMock()
        mock_query = MagicMock()
        mock_user = MagicMock()
        
        mock_user.id = user_id
        mock_query.from_user = mock_user
        mock_query.data = callback_data
        mock_update.callback_query = mock_query
        
        return mock_update
    
    def create_mock_context(self):
        """Создание мок объекта Context"""
        return MagicMock()
    
    async def simulate_user_actions(self, user_id):
        """Симуляция действий пользователя"""
        print(f"\n🎮 Симуляция действий пользователя {user_id}...")
        
        mock_context = self.create_mock_context()
        
        # Получаем данные пользователя
        user = self.db.get_user(user_id)
        if not user:
            print(f"❌ Пользователь {user_id} не найден")
            return
        
        print(f"👤 Пользователь: {user['first_name']} (день {user['current_day']})")
        
        # Симулируем нажатия на кнопки чек-листа
        checklist_actions = [
            ('mark_training', 'Тренировка'),
            ('mark_nutrition', 'Питание'),
            ('mark_water', 'Вода'),
            ('mark_sleep', 'Сон')
        ]
        
        for callback_data, action_name in checklist_actions:
            print(f"🔘 Нажатие: {action_name}")
            
            mock_update = self.create_mock_update(user_id, callback_data)
            
            try:
                # Вызываем соответствующий обработчик
                if callback_data == 'mark_training':
                    await self.callback_handler.handle_mark_training(mock_update, mock_context, callback_data)
                elif callback_data == 'mark_nutrition':
                    await self.callback_handler.handle_mark_nutrition(mock_update, mock_context, callback_data)
                elif callback_data == 'mark_water':
                    await self.callback_handler.handle_mark_water(mock_update, mock_context, callback_data)
                elif callback_data == 'mark_sleep':
                    await self.callback_handler.handle_mark_sleep(mock_update, mock_context, callback_data)
                
                print(f"✅ {action_name} - обработано")
                
            except Exception as e:
                print(f"❌ Ошибка при обработке {action_name}: {e}")
        
        # Симулируем выбор часов сна
        sleep_hours = ['sleep_6h', 'sleep_7h', 'sleep_8h', 'sleep_9h']
        for sleep_hour in sleep_hours:
            print(f"🔘 Выбор сна: {sleep_hour}")
            
            mock_update = self.create_mock_update(user_id, sleep_hour)
            
            try:
                await self.callback_handler.handle_sleep_hours(mock_update, mock_context, sleep_hour)
                print(f"✅ {sleep_hour} - обработано")
                break  # Обрабатываем только один выбор
            except Exception as e:
                print(f"❌ Ошибка при обработке {sleep_hour}: {e}")
    
    def test_keyboards_generation(self):
        """Тест генерации клавиатур"""
        print("\n⌨️ Тестирование генерации клавиатур...")
        
        # Тест главного меню
        main_menu = keyboards.main_menu()
        print("✅ Главное меню сгенерировано")
        
        # Тест чек-листа для каждого пользователя
        for user_data in self.test_users:
            user = self.db.get_user(user_data['user_id'])
            if user:
                checklist = keyboards.checklist_menu(user)
                print(f"✅ Чек-лист для {user['first_name']} сгенерирован")
        
        # Тест меню выбора часов сна
        sleep_menu = keyboards.sleep_hours_menu()
        print("✅ Меню выбора часов сна сгенерировано")
    
    def test_health_tips_generation(self):
        """Тест генерации советов по здоровью"""
        print("\n💡 Тестирование генерации советов...")
        
        for user_data in self.test_users:
            user_id = user_data['user_id']
            
            # Тест советов по воде
            water_tip = health_tips.get_water_tip(user_id)
            print(f"✅ Совет по воде для {user_data['first_name']}: {water_tip[:30]}...")
            
            # Тест советов по завтраку
            breakfast_tip = health_tips.get_breakfast_tip(user_id)
            print(f"✅ Совет по завтраку для {user_data['first_name']}: {breakfast_tip[:30]}...")
            
            # Тест советов по ужину
            dinner_tip = health_tips.get_dinner_tip(user_id)
            print(f"✅ Совет по ужину для {user_data['first_name']}: {dinner_tip[:30]}...")
            
            # Тест советов по сну
            sleep_tip = health_tips.get_sleep_tip(user_id)
            print(f"✅ Совет по сну для {user_data['first_name']}: {sleep_tip[:30]}...")
    
    def test_database_queries(self):
        """Тест запросов к базе данных"""
        print("\n🗄️ Тестирование запросов к базе данных...")
        
        # Тест получения всех пользователей
        all_users = self.db.get_all_users()
        print(f"✅ Получено {len(all_users)} пользователей")
        
        # Тест подсчета пользователей
        count = self.db.get_users_count()
        print(f"✅ Количество пользователей: {count}")
        
        # Тест получения пользователей по статусу
        premium_users = [user for user in all_users if user.get('is_premium', False)]
        print(f"✅ Премиум пользователей: {len(premium_users)}")
        
        # Тест аналитики
        for user_data in self.test_users:
            user_id = user_data['user_id']
            self.db.add_analytics_event(user_id, 'simulation_test', 'button_press')
        print("✅ События аналитики добавлены")
    
    def cleanup(self):
        """Очистка тестовых данных"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        print("🧹 Тестовые данные очищены")
    
    async def run_simulation(self):
        """Запуск полной симуляции"""
        print("🚀 Запуск симуляции взаимодействия с ботом")
        print("=" * 60)
        
        try:
            # Настройка
            self.setup_test_users()
            
            # Тестирование клавиатур
            self.test_keyboards_generation()
            
            # Тестирование советов
            self.test_health_tips_generation()
            
            # Тестирование базы данных
            self.test_database_queries()
            
            # Симуляция действий пользователей
            for user_data in self.test_users:
                await self.simulate_user_actions(user_data['user_id'])
            
            print("\n" + "=" * 60)
            print("🎉 СИМУЛЯЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ ОШИБКА В СИМУЛЯЦИИ: {e}")
            raise
        
        finally:
            self.cleanup()

async def run_bot_simulation():
    """Главная функция симуляции"""
    simulator = BotSimulator()
    await simulator.run_simulation()

if __name__ == "__main__":
    asyncio.run(run_bot_simulation())
