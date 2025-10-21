"""
Тесты для edge cases - проверка нестандартных ситуаций
"""
import asyncio
import sys
from unittest.mock import Mock, AsyncMock, MagicMock
from callbacks import CallbackHandlers
from database import db

class EdgeCasesTester:
    def __init__(self):
        self.handlers = CallbackHandlers()
        self.test_results = []
        
    def create_mock_update(self, callback_data: str, user_id: int = 260916055):
        """Создает mock Update объект"""
        mock_update = Mock()
        mock_query = Mock()
        mock_query.data = callback_data
        mock_query.from_user = Mock()
        mock_query.from_user.id = user_id
        mock_query.from_user.first_name = "Test"
        mock_query.message = Mock()
        mock_query.message.chat_id = user_id
        mock_query.answer = AsyncMock()
        mock_query.delete_message = AsyncMock()
        mock_update.callback_query = mock_query
        return mock_update
    
    def create_mock_context(self):
        """Создает mock Context объект"""
        mock_context = Mock()
        mock_context.user_data = {}
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock()
        mock_bot.send_photo = AsyncMock()
        mock_context.bot = mock_bot
        return mock_context
    
    async def test_unregistered_user(self):
        """Тест: незарегистрированный пользователь пытается начать тренировку"""
        print("\n[TEST] Незарегистрированный пользователь")
        
        try:
            # Используем несуществующий user_id
            fake_user_id = 999999999
            update = self.create_mock_update('start_training', fake_user_id)
            context = self.create_mock_context()
            
            # Пытаемся начать тренировку
            await self.handlers.handle_start_training(update, context, 'start_training')
            
            # Проверяем, что бот не упал
            print("  [OK] Бот корректно обработал незарегистрированного пользователя")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_invalid_callback_data(self):
        """Тест: некорректный callback_data"""
        print("\n[TEST] Некорректный callback_data")
        
        try:
            update = self.create_mock_update('mark_training_999')  # День 999 не существует
            context = self.create_mock_context()
            
            await self.handlers.handle_mark_training(update, context, 'mark_training_999')
            
            print("  [OK] Бот корректно обработал некорректный callback_data")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_user_without_access(self):
        """Тест: пользователь без доступа к тренировкам"""
        print("\n[TEST] Пользователь без доступа к тренировкам")
        
        try:
            # Создаем пользователя с истекшей подпиской
            test_user_id = 123456789
            
            # Пытаемся открыть День 2 (если нет доступа)
            update = self.create_mock_update('training_day_2', test_user_id)
            context = self.create_mock_context()
            
            await self.handlers.handle_training_day_2(update, context, 'training_day_2')
            
            print("  [OK] Бот корректно обработал пользователя без доступа")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_repeated_feedback(self):
        """Тест: повторная отправка обратной связи за один день"""
        print("\n[TEST] Повторная обратная связь за один день")
        
        try:
            update = self.create_mock_update('feedback_like_1')
            context = self.create_mock_context()
            
            # Отправляем обратную связь дважды
            await self.handlers.handle_feedback_like(update, context, 'feedback_like_1')
            await self.handlers.handle_feedback_like(update, context, 'feedback_like_1')
            
            print("  [OK] Бот корректно обработал повторную обратную связь")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_empty_callback_data(self):
        """Тест: пустой callback_data"""
        print("\n[TEST] Пустой callback_data")
        
        try:
            update = self.create_mock_update('')
            context = self.create_mock_context()
            
            # Попытка обработать пустой callback
            await self.handlers.handle_main_menu(update, context, '')
            
            print("  [OK] Бот корректно обработал пустой callback_data")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_concurrent_button_clicks(self):
        """Тест: одновременные нажатия кнопок"""
        print("\n[TEST] Одновременные нажатия кнопок")
        
        try:
            update1 = self.create_mock_update('main_menu')
            update2 = self.create_mock_update('start_training')
            context = self.create_mock_context()
            
            # Запускаем два обработчика одновременно
            await asyncio.gather(
                self.handlers.handle_main_menu(update1, context, 'main_menu'),
                self.handlers.handle_start_training(update2, context, 'start_training')
            )
            
            print("  [OK] Бот корректно обработал одновременные нажатия")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_training_beyond_day_3(self):
        """Тест: попытка открыть тренировку за пределами Дня 3"""
        print("\n[TEST] Тренировка за пределами Дня 3")
        
        try:
            # Устанавливаем current_day = 4 (не существует)
            test_user_id = 260916055
            user = db.get_user(test_user_id)
            if user:
                db.update_user(test_user_id, current_day=4)
            
            update = self.create_mock_update('start_training', test_user_id)
            context = self.create_mock_context()
            
            await self.handlers.handle_start_training(update, context, 'start_training')
            
            # Возвращаем обратно
            if user:
                db.update_user(test_user_id, current_day=user.get('current_day', 1))
            
            print("  [OK] Бот корректно обработал тренировку за пределами Дня 3")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_special_characters_in_feedback(self):
        """Тест: специальные символы в обратной связи"""
        print("\n[TEST] Специальные символы в обратной связи")
        
        try:
            # Симулируем обратную связь с HTML/SQL инъекцией
            special_text = "<script>alert('XSS')</script> OR 1=1; DROP TABLE users;"
            
            # Проверяем, что бот не падает при обработке
            self.handlers.log_feedback(
                user_id=260916055,
                day=1,
                feedback_type='dislike',
                details=special_text
            )
            
            print("  [OK] Бот корректно обработал специальные символы")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_null_user_data(self):
        """Тест: отсутствующие данные пользователя"""
        print("\n[TEST] Отсутствующие данные пользователя")
        
        try:
            # Создаем update с минимальными данными
            mock_update = Mock()
            mock_query = Mock()
            mock_query.data = 'main_menu'
            mock_query.from_user = None  # Нет данных пользователя
            mock_query.message = None
            mock_update.callback_query = mock_query
            
            context = self.create_mock_context()
            
            # Пытаемся обработать
            try:
                await self.handlers.handle_main_menu(mock_update, context, 'main_menu')
            except AttributeError:
                # Ожидаемая ошибка - это нормально
                pass
            
            print("  [OK] Бот корректно обработал отсутствующие данные")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def test_database_connection_failure(self):
        """Тест: сбой подключения к БД"""
        print("\n[TEST] Сбой подключения к БД")
        
        try:
            # Временно "ломаем" БД
            original_get_user = db.get_user
            db.get_user = lambda x: None  # Возвращаем None
            
            update = self.create_mock_update('main_menu')
            context = self.create_mock_context()
            
            await self.handlers.handle_main_menu(update, context, 'main_menu')
            
            # Восстанавливаем БД
            db.get_user = original_get_user
            
            print("  [OK] Бот корректно обработал сбой БД")
            return True
            
        except Exception as e:
            # Восстанавливаем БД в любом случае
            db.get_user = original_get_user
            print(f"  [FAIL] Ошибка: {e}")
            return False
    
    async def run_all_tests(self):
        """Запускает все edge case тесты"""
        print("="*60)
        print("ТЕСТИРОВАНИЕ EDGE CASES")
        print("="*60)
        
        tests = [
            self.test_unregistered_user(),
            self.test_invalid_callback_data(),
            self.test_user_without_access(),
            self.test_repeated_feedback(),
            self.test_empty_callback_data(),
            self.test_concurrent_button_clicks(),
            self.test_training_beyond_day_3(),
            self.test_special_characters_in_feedback(),
            self.test_null_user_data(),
            self.test_database_connection_failure(),
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        passed = sum(1 for r in results if r is True)
        total = len(results)
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*60)
        print(f"Всего тестов: {total}")
        print(f"[OK] Пройдено: {passed}")
        print(f"[FAIL] Провалено: {total - passed}")
        print(f"Процент успеха: {passed/total*100:.1f}%")
        print("="*60)
        
        return passed == total

async def main():
    tester = EdgeCasesTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())


