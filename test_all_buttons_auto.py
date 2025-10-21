"""
Автоматический тест всех кнопок бота
"""
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Chat, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Импортируем модули бота
from callbacks import CallbackHandlers
from keyboards import Keyboards
import database as db

class BotTester:
    def __init__(self):
        self.keyboards = Keyboards()
        self.handlers = CallbackHandlers()
        self.test_results = []
        self.user_id = 260916055  # Тестовый пользователь
        
    def create_mock_update(self, callback_data: str):
        """Создает mock объект Update с callback query"""
        mock_update = MagicMock(spec=Update)
        mock_query = MagicMock(spec=CallbackQuery)
        mock_user = MagicMock(spec=User)
        mock_message = MagicMock(spec=Message)
        mock_chat = MagicMock(spec=Chat)
        
        # Настраиваем mock объекты
        mock_user.id = self.user_id
        mock_user.first_name = "Test"
        mock_chat.id = self.user_id
        mock_message.chat_id = self.user_id
        mock_message.chat = mock_chat
        
        mock_query.from_user = mock_user
        mock_query.message = mock_message
        mock_query.data = callback_data
        
        # Делаем delete_message и edit_message_text async
        mock_query.delete_message = AsyncMock()
        mock_query.edit_message_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        mock_update.callback_query = mock_query
        return mock_update
    
    def create_mock_context(self):
        """Создает mock объект Context"""
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        mock_bot.send_photo = AsyncMock()
        mock_context.bot = mock_bot
        return mock_context
    
    async def test_callback(self, callback_name: str, callback_data: str):
        """Тестирует один callback"""
        print(f"\n[TEST] Тестируем callback: {callback_name} ({callback_data})")
        
        try:
            # Получаем обработчик - сначала пытаемся стандартное имя
            handler_method = getattr(self.handlers, f'handle_{callback_name}', None)
            
            if not handler_method:
                # Пробуем найти по другим паттернам
                # Например, mark_training_1 -> handle_mark_training
                base_name = callback_name.rsplit('_', 1)[0] if '_' in callback_name and callback_name[-1].isdigit() else callback_name
                handler_method = getattr(self.handlers, f'handle_{base_name}', None)
                
            if not handler_method:
                print(f"  [FAIL] Обработчик не найден")
                self.test_results.append({
                    'callback': callback_name,
                    'status': 'FAIL',
                    'error': 'Handler not found'
                })
                return False
            
            # Создаем mock объекты
            update = self.create_mock_update(callback_data)
            context = self.create_mock_context()
            
            # Вызываем обработчик
            if callable(handler_method):
                await handler_method(update, context, callback_data)
            else:
                await handler_method(update, context)
            
            print(f"  [OK] Успешно выполнен")
            self.test_results.append({
                'callback': callback_name,
                'status': 'PASS',
                'error': None
            })
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            self.test_results.append({
                'callback': callback_name,
                'status': 'FAIL',
                'error': str(e)
            })
            return False
    
    async def test_all_callbacks(self):
        """Тестирует все callbacks"""
        print("\n" + "="*60)
        print("АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ВСЕХ КНОПОК")
        print("="*60)
        
        # Список всех РЕАЛИЗОВАННЫХ callbacks для тестирования
        callbacks_to_test = [
            ('main_menu', 'main_menu'),
            ('start_training', 'start_training'),
            ('training_day_1', 'training_day_1'),
            ('training_day_2', 'training_day_2'),
            ('training_day_3', 'training_day_3'),
            ('mark_training_1', 'mark_training_1'),
            ('mark_training_2', 'mark_training_2'),
            ('mark_training_3', 'mark_training_3'),
            ('feedback_like_1', 'feedback_like_1'),
            ('feedback_like_2', 'feedback_like_2'),
            ('feedback_like_3', 'feedback_like_3'),
            ('feedback_dislike_1', 'feedback_dislike_1'),
            ('package_basic', 'package_basic'),
            ('buy_course', 'buy_course'),
            ('buy_training', 'buy_training'),
            ('faq', 'faq'),
            ('full_course', 'full_course'),
            ('online_training', 'online_training'),
            ('contact_support', 'contact_support'),
            ('start_registration', 'start_registration'),
        ]
        
        total = len(callbacks_to_test)
        passed = 0
        failed = 0
        
        for callback_name, callback_data in callbacks_to_test:
            result = await self.test_callback(callback_name, callback_data)
            if result:
                passed += 1
            else:
                failed += 1
            
            # Небольшая задержка между тестами
            await asyncio.sleep(0.1)
        
        # Выводим итоги
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*60)
        print(f"Всего тестов: {total}")
        print(f"[OK] Успешно: {passed}")
        print(f"[FAIL] Провалено: {failed}")
        print(f"Процент успеха: {(passed/total*100):.1f}%")
        
        # Выводим детали провалов
        if failed > 0:
            print("\n" + "="*60)
            print("ДЕТАЛИ ПРОВАЛОВ")
            print("="*60)
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"\n[FAIL] {result['callback']}")
                    print(f"   Ошибка: {result['error']}")
        
        return passed == total
    
    def test_all_keyboards(self):
        """Тестирует создание всех клавиатур"""
        print("\n" + "="*60)
        print("ТЕСТИРОВАНИЕ КЛАВИАТУР")
        print("="*60)
        
        keyboards_to_test = [
            ('main_menu', lambda: self.keyboards.main_menu()),
            ('training_menu_1', lambda: self.keyboards.training_menu(1)),
            ('training_menu_2', lambda: self.keyboards.training_menu(2)),
            ('training_menu_3', lambda: self.keyboards.training_menu(3)),
            ('like_dislike_menu_1', lambda: self.keyboards.like_dislike_menu(1)),
            ('back_to_main', lambda: self.keyboards.back_to_main()),
            ('payment_menu', lambda: self.keyboards.payment_menu()),
            ('admin_menu', lambda: self.keyboards.admin_menu()),
        ]
        
        total = len(keyboards_to_test)
        passed = 0
        failed = 0
        
        for kb_name, kb_func in keyboards_to_test:
            try:
                print(f"\n[TEST] Тестируем клавиатуру: {kb_name}")
                keyboard = kb_func()
                
                if keyboard and isinstance(keyboard, InlineKeyboardMarkup):
                    print(f"  [OK] Клавиатура создана успешно")
                    passed += 1
                else:
                    print(f"  [FAIL] Неверный тип клавиатуры")
                    failed += 1
                    
            except Exception as e:
                print(f"  [FAIL] Ошибка: {e}")
                failed += 1
        
        print(f"\nКлавиатуры: {passed}/{total} успешно")
        return passed == total

async def main():
    """Основная функция тестирования"""
    tester = BotTester()
    
    # Тестируем клавиатуры
    keyboards_ok = tester.test_all_keyboards()
    
    # Тестируем callbacks
    callbacks_ok = await tester.test_all_callbacks()
    
    # Общий результат
    print("\n" + "="*60)
    print("ОБЩИЙ РЕЗУЛЬТАТ")
    print("="*60)
    if keyboards_ok and callbacks_ok:
        print("[OK] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print("[FAIL] НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        if not keyboards_ok:
            print("   - Проблемы с клавиатурами")
        if not callbacks_ok:
            print("   - Проблемы с callbacks")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

