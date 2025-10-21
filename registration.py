"""
📝 Регистрация пользователей для бота DianaLisa
Обработка регистрации, валидация данных и создание профиля
"""

import re
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import MESSAGES
from keyboards import Keyboards
from database import db
from utils import validate_phone, get_user_timezone
# from validation import input_validator, error_handler, ValidationError  # Модуль не существует

logger = logging.getLogger(__name__)

# Создаем экземпляр клавиатур
keyboards = Keyboards()

class RegistrationHandler:
    """Класс для обработки регистрации пользователей"""
    
    def __init__(self):
        self.registration_states = {}  # Хранение состояний регистрации
    
    async def send_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправка приветственного сообщения с кнопкой регистрации"""
        user_id = update.effective_user.id
        user_data = update.effective_user
        
        # Отправляем приветственное сообщение с изображением
        welcome_text = f"""
🌟 <b>Добро пожаловать в DianaLisa Bot!</b>

👋 Привет, {user_data.first_name}!

💪 Я помогу тебе начать путь к здоровому образу жизни!

🎯 <b>Что тебя ждет:</b>
• 3 дня бесплатных тренировок
• Мотивация и поддержка 24/7
• Отслеживание прогресса

🚀 Давай начнем твое преображение!
        """
        
        # Отправляем изображение с приветствием
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="znakomstvo.jpg",
            text=welcome_text,
            reply_markup=keyboards.start_registration_menu(),
            parse_mode=ParseMode.HTML
        )
    
    async def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало процесса регистрации"""
        user_id = update.effective_user.id
        user_data = update.effective_user
        
        # Проверяем, есть ли пользователь в базе
        existing_user = db.get_user(user_id)
        if existing_user:
            # Отправляем приветствие с изображением для существующего пользователя
            welcome_back_text = f"""
🌟 <b>Добро пожаловать обратно!</b>

👋 Привет, {existing_user['first_name']}!

💪 Рады видеть тебя снова! Продолжай свой путь к здоровому образу жизни!

🎯 Твой текущий прогресс: День {existing_user.get('current_day', 1)}/3
            """
            
            from utils import send_image_with_text
            await send_image_with_text(
                bot=context.bot,
                chat_id=user_id,
                image_path="znakomstvo.jpg",
                text=welcome_back_text,
                reply_markup=keyboards.main_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Добавляем событие в аналитику
        db.add_analytics_event(user_id, 'registration_started')
        
        # Инициализируем состояние регистрации
        self.registration_states[user_id] = {
            'step': 'name',
            'user_id': user_id,
            'username': user_data.username,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name
        }
    
    async def handle_name_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода имени"""
        user_id = update.effective_user.id
        
        if user_id not in self.registration_states:
            await update.message.reply_text(
                "❌ Регистрация не начата. Используйте /start",
                reply_markup=keyboards.back_to_main()
            )
            return
        
        name = update.message.text.strip()
        
        # Валидация имени - только текст, без цифр
        from utils import validate_name
        if not validate_name(name):
            # Удаляем сообщение пользователя с невалидным именем
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Удаляем старое сообщение с кнопкой "Назад к регистрации"
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id - 1
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Отправляем ошибку с картинкой
            from utils import send_image_with_text
            await send_image_with_text(
                bot=context.bot,
                chat_id=update.effective_chat.id,
                image_path="znakomstvo.jpg",
                text="❌ Имя должно содержать только буквы. Цифры и специальные символы не допускаются.",
                reply_markup=keyboards.name_input_keyboard(),
                parse_mode=ParseMode.HTML
            )
            return
        
        if len(name) > 50:
            # Удаляем сообщение пользователя с длинным именем
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Удаляем старое сообщение с кнопкой "Назад к регистрации"
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id - 1
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Отправляем ошибку с картинкой
            from utils import send_image_with_text
            await send_image_with_text(
                bot=context.bot,
                chat_id=update.effective_chat.id,
                image_path="znakomstvo.jpg",
                text="❌ Имя слишком длинное. Максимум 50 символов.",
                reply_markup=keyboards.name_input_keyboard(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Сохраняем имя
        self.registration_states[user_id]['name'] = name
        self.registration_states[user_id]['step'] = 'phone'
        
        # Удаляем сообщение пользователя с именем
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except:
            pass  # Игнорируем ошибки удаления
        
        # Удаляем старое сообщение с кнопкой "Назад к регистрации"
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id - 1
            )
        except:
            pass  # Игнорируем ошибки удаления
        
        # Отправляем новое сообщение о вводе телефона с картинкой
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=update.effective_chat.id,
            image_path="znakomstvo.jpg",
            text=MESSAGES['phone_request'],
            reply_markup=keyboards.phone_input_keyboard(),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_phone_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода номера телефона"""
        user_id = update.effective_user.id
        
        if user_id not in self.registration_states:
            await update.message.reply_text(
                "❌ Регистрация не начата. Используйте /start",
                reply_markup=keyboards.back_to_main()
            )
            return
        
        phone = update.message.text.strip()
        
        # Валидация номера телефона - только цифры и разрешенные символы
        from utils import validate_phone
        if not validate_phone(phone):
            # Удаляем сообщение пользователя с невалидным номером
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Удаляем старое сообщение с кнопкой "Назад к регистрации"
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id - 1
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Отправляем ошибку с картинкой
            from utils import send_image_with_text
            await send_image_with_text(
                bot=context.bot,
                chat_id=update.effective_chat.id,
                image_path="znakomstvo.jpg",
                text="❌ Неверный формат номера телефона. Используйте только цифры, плюс, скобки, пробелы и дефисы. Пример: +7 (999) 123-45-67",
                reply_markup=keyboards.phone_input_keyboard(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Проверяем, не занят ли номер телефона
        if self.is_phone_taken(phone):
            # Удаляем сообщение пользователя с занятым номером
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Удаляем старое сообщение с кнопкой "Назад к регистрации"
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id - 1
                )
            except:
                pass  # Игнорируем ошибки удаления
            
            # Отправляем ошибку с картинкой
            from utils import send_image_with_text
            await send_image_with_text(
                bot=context.bot,
                chat_id=update.effective_chat.id,
                image_path="znakomstvo.jpg",
                text="❌ Этот номер телефона уже используется. Попробуйте другой.",
                reply_markup=keyboards.phone_input_keyboard(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Сохраняем номер телефона
        self.registration_states[user_id]['phone'] = phone
        
        # Удаляем сообщение пользователя с номером телефона
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except:
            pass  # Игнорируем ошибки удаления
        
        # Удаляем старое сообщение с кнопкой "Назад к регистрации"
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id - 1
            )
        except:
            pass  # Игнорируем ошибки удаления
        
        # Завершаем регистрацию
        await self.complete_registration(update, context, user_id)
    
    async def handle_timezone_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора часового пояса"""
        user_id = update.effective_user.id
        
        if user_id not in self.registration_states:
            await update.message.reply_text(
                "❌ Регистрация не начата. Используйте /start",
                reply_markup=keyboards.back_to_main()
            )
            return
        
        # Получаем часовой пояс из callback_data
        query = update.callback_query
        if query:
            timezone = query.data.replace('timezone_', '')
            await query.answer()
        else:
            timezone = 'Europe/Moscow'  # По умолчанию
        
        # Сохраняем часовой пояс
        self.registration_states[user_id]['timezone'] = timezone
        self.registration_states[user_id]['step'] = 'complete'
        
        # Завершаем регистрацию
        await self.complete_registration(update, context, user_id)
    
    async def complete_timezone_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, timezone: str):
        """Завершение выбора часового пояса и регистрации"""
        query = update.callback_query
        user_id = query.from_user.id
        
        logger.info(f"Завершение выбора часового пояса для пользователя {user_id}: {timezone}")
        
        # Проверяем, есть ли состояние регистрации
        if user_id not in self.registration_states:
            logger.error(f"Состояние регистрации не найдено для пользователя {user_id}")
            await query.edit_message_text(
                "❌ Ошибка регистрации. Начните заново с /start",
                reply_markup=keyboards.back_to_main()
            )
            return
        
        # Обновляем часовой пояс в состоянии
        self.registration_states[user_id]['timezone'] = timezone
        self.registration_states[user_id]['step'] = 'complete'
        
        # Завершаем регистрацию
        await self.complete_registration(update, context, user_id)
    
    async def complete_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Завершение регистрации"""
        try:
            state = self.registration_states[user_id]
            
            logger.info(f"Завершение регистрации для пользователя {user_id}")
            logger.info(f"Состояние регистрации: {state}")
            
            # Создаем пользователя в базе данных
            success = db.add_user(
                user_id=user_id,
                username=state.get('username'),
                first_name=state.get('name'),
                last_name=state.get('last_name'),
                phone=state.get('phone'),
                timezone=state.get('timezone')
            )
            
            logger.info(f"Результат добавления пользователя {user_id}: {success}")
            
            if success:
                # Добавляем событие в аналитику
                db.add_analytics_event(user_id, 'registration_completed')
                
                # Проверяем, что пользователь действительно добавлен
                added_user = db.get_user(user_id)
                if not added_user:
                    logger.error(f"Пользователь {user_id} не найден после добавления!")
                    await self.handle_registration_error(update, "Ошибка сохранения данных")
                    return
                
                logger.info(f"Пользователь {user_id} успешно добавлен в базу данных")
                
                # Отправляем приветственное сообщение
                welcome_text = f"""
🎉 Добро пожаловать, {state['name']}!

{MESSAGES['registration_success']}
                """
                
                # Удаляем старое сообщение с кнопкой "Назад к регистрации"
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=update.message.message_id - 1
                    )
                except:
                    pass  # Игнорируем ошибки удаления
                
                # Отправляем приветственное сообщение с главным меню
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=welcome_text,
                    reply_markup=keyboards.main_menu(),
                    parse_mode=ParseMode.HTML
                )
                
                # Планируем напоминания
                timezone = state.get('timezone', 'Europe/Moscow')
                await self.schedule_user_reminders(user_id, timezone)
                
                logger.info(f"Пользователь {user_id} успешно зарегистрирован и получил доступ к меню")
            else:
                await self.handle_registration_error(update, "Ошибка сохранения данных")
            
            # Очищаем состояние регистрации
            del self.registration_states[user_id]
            
        except Exception as e:
            logger.error(f"Ошибка завершения регистрации для пользователя {user_id}: {e}")
            await self.handle_registration_error(update, "Произошла ошибка при регистрации")
    
    async def schedule_user_reminders(self, user_id: int, timezone: str):
        """Планирование напоминаний для пользователя"""
        try:
            # Простое планирование без сложной логики
            # Утреннее напоминание (8:00)
            morning_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
            db.add_scheduled_job(user_id, 'morning_motivation', morning_time)
            
            # Вечернее напоминание (20:00)
            evening_time = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
            db.add_scheduled_job(user_id, 'evening_motivation', evening_time)
            
            logger.info(f"Напоминания запланированы для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка планирования напоминаний: {e}")
    
    async def handle_registration_error(self, update: Update, error_message: str):
        """Обработка ошибок регистрации"""
        error_text = f"❌ {error_message}\n\nПопробуйте начать регистрацию заново с помощью /start"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                error_text,
                reply_markup=keyboards.back_to_main()
            )
        else:
            await update.message.reply_text(
                error_text,
                reply_markup=keyboards.back_to_main()
            )
    
    def validate_name(self, name: str) -> bool:
        """Валидация имени"""
        if not name or len(name) < 2 or len(name) > 50:
            return False
        
        # Проверяем, что имя содержит только буквы, пробелы и дефисы
        if not re.match(r'^[a-zA-Zа-яА-Я\s\-]+$', name):
            return False
        
        return True
    
    def is_phone_taken(self, phone: str) -> bool:
        """Проверка, занят ли номер телефона"""
        try:
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE phone = ?', (phone,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка проверки номера телефона: {e}")
            return False
    
    async def handle_registration_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений во время регистрации"""
        user_id = update.effective_user.id
        
        if user_id not in self.registration_states:
            return False
        
        state = self.registration_states[user_id]
        
        if state['step'] == 'name':
            await self.handle_name_input(update, context)
            return True
        elif state['step'] == 'phone':
            await self.handle_phone_input(update, context)
            return True
        
        return False
    
    def get_registration_state(self, user_id: int) -> dict:
        """Получение состояния регистрации пользователя"""
        return self.registration_states.get(user_id, {})
    
    def clear_registration_state(self, user_id: int):
        """Очистка состояния регистрации"""
        if user_id in self.registration_states:
            del self.registration_states[user_id]
    
    async def handle_referral_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, referral_code: str):
        """Обработка регистрации по реферальной ссылке"""
        user_id = update.effective_user.id
        
        # Находим пользователя, который пригласил
        try:
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE referral_code = ?', (referral_code,))
                referrer = cursor.fetchone()
                
                if referrer:
                    referrer_id = referrer[0]
                    
                    # Инициализируем состояние регистрации с реферером
                    self.registration_states[user_id] = {
                        'step': 'name',
                        'user_id': user_id,
                        'username': update.effective_user.username,
                        'first_name': update.effective_user.first_name,
                        'last_name': update.effective_user.last_name,
                        'referred_by': referrer_id
                    }
                    
                    # Увеличиваем счетчик рефералов
                    db.update_user(referrer_id, total_referrals=db.get_user(referrer_id)['total_referrals'] + 1)
                    
                    await update.message.reply_text(
                        f"🎉 Ты приглашен(а) другом! Начинаем регистрацию!\n\n{MESSAGES['name_request']}",
                        reply_markup=keyboards.back_to_main()
                    )
                else:
                    await update.message.reply_text(
                        "❌ Неверная реферальная ссылка. Начинаем обычную регистрацию.",
                        reply_markup=keyboards.back_to_main()
                    )
                    await self.start_registration(update, context)
                    
        except Exception as e:
            logger.error(f"Ошибка обработки реферальной регистрации: {e}")
            await self.start_registration(update, context)

# Глобальный экземпляр обработчика регистрации
registration_handler = RegistrationHandler()
