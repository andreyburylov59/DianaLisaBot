"""
🔄 Обработчики кнопок и callback-ов для бота DianaLisa
Обработка всех интерактивных элементов интерфейса
"""

import logging
import traceback
from datetime import datetime
from enhanced_logger import get_logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import MESSAGES, BUTTONS, ADMIN_IDS, IMAGES
from keyboards import keyboards
from database import db
from admin import AdminPanel
from utils import get_user_timezone, send_motivational_message
from training import send_training_content
from payment import create_payment_invoice
from admin import handle_admin_actions

# Создаем детальный логгер для callbacks
callback_logger = logging.getLogger('callbacks')
callback_logger.setLevel(logging.DEBUG)

# Удалены старые функции логирования для упрощения
# from validation import error_handler, ValidationError  # Модуль не существует

logger = logging.getLogger(__name__)
enhanced_logger = get_logger("callbacks")

class CallbackHandlers:
    """Класс для обработки callback-ов от кнопок"""
    
    def __init__(self):
        self.handlers = {
            # Основные действия
            'main_menu': self.handle_main_menu,
            'skip_phone': self.handle_skip_phone,
            'start_training': self.handle_start_training,
            'faq': self.handle_faq,
            'full_course': self.handle_full_course,
            'online_training': self.handle_online_training,
            'contact_support': self.handle_contact_support,
            
            # Тренировки
            'training_day_1': self.handle_training_day_1,
            'training_day_2': self.handle_training_day_2,
            'training_day_3': self.handle_training_day_3,
            
            # Тренировки
            'mark_training': self.handle_mark_training,
            
            # Обратная связь по тренировкам
            'feedback_like_1': self.handle_feedback_like,
            'feedback_like_2': self.handle_feedback_like,
            'feedback_like_3': self.handle_feedback_like,
            'feedback_dislike_1': self.handle_feedback_dislike,
            'feedback_dislike_2': self.handle_feedback_dislike,
            'feedback_dislike_3': self.handle_feedback_dislike,
            
            # Оценка тренировок (убрано - теперь автоматически)
            # 'feedback_training_': self.handle_training_feedback,
            'difficulty_1_': self.handle_difficulty_rating,
            'difficulty_2_': self.handle_difficulty_rating,
            'difficulty_3_': self.handle_difficulty_rating,
            'difficulty_4_': self.handle_difficulty_rating,
            'difficulty_5_': self.handle_difficulty_rating,
            'clarity_1_': self.handle_clarity_rating,
            'clarity_2_': self.handle_clarity_rating,
            'clarity_3_': self.handle_clarity_rating,
            'clarity_4_': self.handle_clarity_rating,
            'clarity_5_': self.handle_clarity_rating,
            'finish_feedback_': self.handle_finish_feedback,
            'training_feedback_': self.handle_training_feedback,
            'skip_feedback': self.handle_skip_feedback,
            'view_results': self.handle_view_results,
            
            # Часовой пояс
            'timezone_': self.handle_timezone_selection,
            
            # Оплата
            'buy_course': self.handle_buy_course,
            'buy_training': self.handle_buy_training,
            'package_': self.handle_package_selection,
            'training_': self.handle_training_selection,
            
            # Админка
            'admin_': self.handle_admin_action,
            'admin_stats': self.handle_admin_stats,
            'admin_users': self.handle_admin_users,
            'admin_payments': self.handle_admin_payments,
            'admin_reviews': self.handle_admin_reviews,
            'admin_training_feedback': self.handle_admin_training_feedback,
            'admin_analytics': self.handle_admin_analytics,
            'admin_export_db': self.handle_admin_export_db,
            'admin_send_message': self.handle_admin_send_message,
            'admin_menu': self.handle_admin_menu,
            'admin_clear_db': self.handle_admin_clear_db,
            'confirm_broadcast': self.handle_confirm_broadcast,
            'cancel_broadcast': self.handle_cancel_broadcast,
            'confirm_clear_db': self.handle_confirm_clear_db,
            'admin_confirm_clear_db': self.handle_confirm_clear_db,
            'admin_panel': self.handle_admin_action,
            
            # Рейтинг
            'rating_': self.handle_rating,
            'rating_1': self.handle_rating_1,
            'rating_2': self.handle_rating_2,
            'rating_3': self.handle_rating_3,
            'rating_4': self.handle_rating_4,
            'rating_5': self.handle_rating_5,
            
            # Часовые пояса
            'timezone_': self.handle_timezone_selection,
            'timezone_Europe/Moscow': self.handle_timezone_moscow,
            'timezone_Europe/Kiev': self.handle_timezone_kiev,
            'timezone_Europe/Minsk': self.handle_timezone_minsk,
            'timezone_Asia/Almaty': self.handle_timezone_almaty,
            'timezone_America/New_York': self.handle_timezone_new_york,
            'timezone_Europe/London': self.handle_timezone_london,
            'timezone_Europe/Berlin': self.handle_timezone_berlin,
            'timezone_Europe/Paris': self.handle_timezone_paris,
            'timezone_Asia/Tokyo': self.handle_timezone_tokyo,
            'timezone_Australia/Sydney': self.handle_timezone_sydney,
            
            # Пакеты
            'package_basic': self.handle_package_basic,
            'payment_success': self.handle_payment_success,
            'payment_cancel': self.handle_payment_cancel,
            
            # Тренировки
            'training_single': self.handle_training_single,
            'training_pack5': self.handle_training_pack5,
            'training_pack10': self.handle_training_pack10,
            'training_unlimited': self.handle_training_unlimited,
            
            # Регистрация
            'start_registration': self.handle_start_registration,
            'back_to_registration_start': self.handle_back_to_registration_start,
            
            # Отзывы
            'leave_review': self.handle_leave_review,
            
            # Подтверждения
            'yes': self.handle_yes,
            'no': self.handle_no,
            'confirm_': self.handle_confirm,
            'cancel_action': self.handle_cancel,
            
            # Пагинация
            '_page_': self.handle_pagination,
            
            # Заглушка
            'noop': self.handle_noop
        }
    
    async def process_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основной обработчик callback-ов"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        user_id = query.from_user.id
        
        logger.info(f"Обработка callback: {callback_data} от пользователя {user_id}")
        
        # Добавляем событие в аналитику
        db.add_analytics_event(user_id, 'button_click', callback_data)
        
        # Ищем подходящий обработчик
        handler = None
        for pattern, handler_func in self.handlers.items():
            if callback_data.startswith(pattern):
                handler = handler_func
                break
        
        if handler:
            try:
                await handler(update, context, callback_data)
            except Exception as e:
                logger.error(f"Ошибка обработки callback {callback_data}: {e}")
                # Удаляем сообщение и отправляем новое вместо edit_message_text
                try:
                    await query.delete_message()
                except:
                    pass
                
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Произошла ошибка. Попробуйте позже.",
                    reply_markup=keyboards.back_to_main()
                )
        else:
            logger.warning(f"Неизвестный callback: {callback_data}")
            # Удаляем сообщение и отправляем новое вместо edit_message_text
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❓ Неизвестная команда. Возвращаемся в главное меню.",
                reply_markup=keyboards.main_menu()
            )
    
    # ============================================================================
    # ГЛАВНОЕ МЕНЮ И НАВИГАЦИЯ
    # ============================================================================
    
    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка возврата в главное меню"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            logger.info(f"[MAIN_MENU] Начало обработки для пользователя {user_id}")
            user = db.get_user(user_id)
            logger.info(f"[MAIN_MENU] Пользователь получен: {user is not None}")
            
            enhanced_logger.log_user_action(user_id, 'main_menu_clicked')
            logger.info(f"[MAIN_MENU] Действие залогировано")
            
            # Проверяем, находится ли пользователь в процессе регистрации
            logger.info(f"[MAIN_MENU] Проверяем регистрацию")
            try:
                from registration import registration_handler
                in_registration = user_id in registration_handler.registration_states
            except Exception as reg_error:
                logger.error(f"[MAIN_MENU] Ошибка проверки регистрации: {reg_error}")
                in_registration = False
            
            if in_registration:
                logger.info(f"[MAIN_MENU] Пользователь в процессе регистрации")
                state = registration_handler.registration_states[user_id]
                if state['step'] == 'email':
                    # Удаляем сообщение с картинкой и отправляем новое
                    try:
                        await query.delete_message()
                    except:
                        pass
                    
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="❌ Пожалуйста, завершите регистрацию. Введите email:",
                        reply_markup=keyboards.email_input_keyboard()
                    )
                    return
                elif state['step'] == 'timezone':
                    # Удаляем сообщение с картинкой и отправляем новое
                    try:
                        await query.delete_message()
                    except:
                        pass
                    
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="❌ Пожалуйста, завершите регистрацию. Выберите часовой пояс:",
                        reply_markup=keyboards.timezone_menu()
                    )
                    return
            
            logger.info(f"[MAIN_MENU] Формируем текст приветствия")
            if user:
                from utils import format_course_progress_bar, get_user_status_text
                
                current_day = user.get('current_day', 1)
                progress_bar = format_course_progress_bar(current_day)
                status_text = get_user_status_text(user)
                
                
                welcome_text = f"""
🌟 <b>Добро пожаловать обратно!</b>

👋 Привет, {user['first_name']}!

💪 Рады видеть тебя снова! Продолжай свой путь к здоровому образу жизни!

{progress_bar}
{status_text}

🏋️‍♀️ Выбери действие:
                """
                enhanced_logger.log_user_action(user_id, 'welcome_back_message')
            else:
                welcome_text = f"""
🌟 <b>Добро пожаловать в DianaLisa Bot, {query.from_user.first_name}!</b>

💪 Я твой помощник на пути к стройному телу!

🎯 <b>Что тебя ждет:</b>
• 3 дня бесплатных тренировок
• Мотивация и поддержка 
• Отслеживание прогресса

🚀 Давай начнем твое преображение!
                """
                enhanced_logger.log_user_action(user_id, 'welcome_new_message')
            
            logger.info(f"[MAIN_MENU] Удаляем предыдущее сообщение")
            # Удаляем предыдущее сообщение и отправляем новое с изображением
            try:
                await query.delete_message()
                enhanced_logger.log_user_action(user_id, 'message_deleted')
                logger.info(f"[MAIN_MENU] Сообщение удалено")
            except Exception as e:
                logger.error(f"[MAIN_MENU] Ошибка удаления сообщения: {e}")
                enhanced_logger.log_error(e, {'user_id': user_id, 'action': 'delete_message'})
            
            # Отправляем изображение с приветствием
            logger.info(f"[MAIN_MENU] Отправляем изображение с приветствием")
            try:
                from utils import send_image_with_text
                enhanced_logger.log_user_action(user_id, 'sending_welcome_image')
                
                # Проверяем, является ли пользователь админом
                from config import ADMIN_IDS
                is_admin = user_id in ADMIN_IDS
                
                # Выбираем клавиатуру в зависимости от прав пользователя
                menu_keyboard = keyboards.admin_main_menu() if is_admin else keyboards.main_menu()
                logger.info(f"[MAIN_MENU] Клавиатура подготовлена, is_admin={is_admin}")
                
                await send_image_with_text(
                    bot=context.bot,
                    chat_id=user_id,
                    image_path="DianaLisa1.jpg",
                    text=welcome_text,
                    reply_markup=menu_keyboard,
                    parse_mode=ParseMode.HTML
                )
                enhanced_logger.log_user_action(user_id, 'welcome_image_sent')
                logger.info(f"[MAIN_MENU] Изображение отправлено успешно")
            except Exception as e:
                logger.error(f"[MAIN_MENU] Ошибка отправки изображения: {e}")
                enhanced_logger.log_error(e, {'user_id': user_id, 'action': 'send_welcome_image'})
                # В случае ошибки отправляем только текст
                try:
                    from config import ADMIN_IDS
                    is_admin = user_id in ADMIN_IDS
                    menu_keyboard = keyboards.admin_main_menu() if is_admin else keyboards.main_menu()
                    
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=welcome_text,
                        reply_markup=menu_keyboard,
                        parse_mode=ParseMode.HTML
                    )
                    logger.info(f"[MAIN_MENU] Fallback сообщение отправлено")
                except Exception as fallback_error:
                    logger.error(f"[MAIN_MENU] Критическая ошибка fallback: {fallback_error}")
                    
        except Exception as e:
            logger.error(f"[MAIN_MENU] Критическая ошибка в handle_main_menu: {e}")
            # Последний fallback - отправляем простое сообщение
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🌟 Главное меню",
                    reply_markup=keyboards.main_menu()
                )
            except Exception as final_error:
                logger.error(f"[MAIN_MENU] Финальный fallback провалился: {final_error}")
    
    async def handle_skip_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка пропуска ввода номера телефона"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем, находится ли пользователь в процессе регистрации
        from registration import registration_handler
        if user_id in registration_handler.registration_states:
            state = registration_handler.registration_states[user_id]
            if state['step'] == 'phone':
                # Пропускаем номер телефона и завершаем регистрацию
                registration_handler.registration_states[user_id]['phone'] = None
                
                # Удаляем сообщение с картинкой
                try:
                    await query.delete_message()
                except:
                    pass
                
                # Завершаем регистрацию
                await registration_handler.complete_registration(update, context, user_id)
                return
        
        # Если пользователь не в процессе регистрации, переходим в главное меню
        await self.handle_main_menu(update, context, callback_data)
    
    # ============================================================================
    # ТРЕНИРОВКИ
    # ============================================================================
    
    async def handle_start_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка начала тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        logger.info(f"Обработка start_training для пользователя {user_id}")
        
        user = db.get_user(user_id)
        logger.info(f"Пользователь {user_id} найден в БД: {user is not None}")
        
        if not user:
            logger.warning(f"Пользователь {user_id} не найден в БД!")
            # Удаляем предыдущее сообщение и отправляем новое
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Сначала нужно зарегистрироваться. Используйте /start",
                reply_markup=keyboards.back_to_main()
            )
            return
        
        current_day = user['current_day']
        
        # Удаляем предыдущее сообщение и отправляем новое с изображением
        try:
            await query.delete_message()
        except:
            pass
        
        training_text = f"""<b>Выберите тренировку</b>

Ваш текущий прогресс: <b>День {current_day}</b>

Доступные тренировки:
🏋️‍♀️ <b>День 1</b> - Базовая разминка (25 минут) - ✅ Доступна
{'🏋️‍♀️ <b>День 2</b> - Силовые упражнения (30 минут) - ✅ Доступна' if current_day >= 2 else '🔒 <b>День 2</b> - Силовые упражнения (30 минут) - ❌ Заблокирована'}
{'🏋️‍♀️ <b>День 3</b> - Интенсивная тренировка (35 минут) - ✅ Доступна' if current_day >= 3 else '🔒 <b>День 3</b> - Интенсивная тренировка (35 минут) - ❌ Заблокирована'}

Выберите доступную тренировку:"""
        
        # Отправляем изображение с меню тренировок
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="DianaLisa2.jpg",
            text=training_text,
            reply_markup=keyboards.training_menu(current_day),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка FAQ"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Отправляем FAQ с изображением
        faq_text = MESSAGES['faq']
        
        # Удаляем предыдущее сообщение и отправляем новое с изображением
        try:
            await query.delete_message()
        except:
            pass  # Игнорируем ошибки удаления
        
        # Отправляем изображение с FAQ
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="DianaLisa2.jpg",
            text=faq_text,
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_full_course(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка покупки полного курса"""
        query = update.callback_query
        user_id = query.from_user.id
        
        course_text = """
💎 ПОЛНЫЙ КУРС DIANALISA

🎯 Что входит:
• 30 дней персональных тренировок
• План питания на месяц
• Поддержка 24/7
• Доступ к закрытому чату
• Бонусные материалы
• Гарантия результата

📞 Запись и проведение тренировок: @Dianalisa5

💰 Выберите пакет:
        """
        
        # Отправляем информацию о курсах с изображением
        course_text = """
🌟 <b>Полный курс с DianaLisa</b>

💪 <b>Что входит в курс:</b>
• Длительность 28 дней 
• 12 тренировок (3 тренировки в неделю)
• Программа питания
• Ежедневная поддержка тренера
• Отслеживание прогресса
• Мотивация и советы 24/7
• Доступ 40 дней

🎯 <b>Результат:</b>
• Похудение на 5-10 кг за месяц
• Укрепление мышц
• Стройное тело
• Здоровые привычки 

📞 Запись и проведение курса: @Dianalisa5

💰 Оплатить курс:
        """
        
        # Удаляем предыдущее сообщение и отправляем новое с изображением
        try:
            await query.delete_message()
        except:
            pass  # Игнорируем ошибки удаления
        
        # Отправляем изображение с информацией о курсах
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="DianaLisa2.jpg",
            text=course_text,
            reply_markup=keyboards.course_packages(),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_online_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка записи на онлайн-тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        training_text = """
💻 ОНЛАЙН-ТРЕНИРОВКИ

🏋️‍♀️ Что входит:
• Персональные тренировки с тренером
• Индивидуальный подход
• Корректировка техники
• Мотивация и поддержка
• Гибкое расписание

🏢 ОФЛАЙН-ТРЕНИРОВКИ В ПЕРМИ
• Персональные тренировки в зале
• Групповые занятия
• Современное оборудование
• Индивидуальный подход

📞 Запись и проведение тренировок: @Dianalisa5

💰 Выберите пакет:
        """
        
        # Отправляем информацию о тренировках с изображением
        training_text = """
🌟 <b>Онлайн тренировки с DianaLisa</b>

💪 <b>Что вас ждет:</b>
• Персональные тренировки онлайн
• Индивидуальная программа
• Поддержка тренера 24/7
• Гибкий график занятий
• Результат уже через неделю!

🏠 <b>Преимущества онлайн:</b>
• Тренируйся дома
• Экономия времени
• Комфортная обстановка
• Индивидуальный подход

📞 Запись и проведение тренировок: @Dianalisa5

💰 Выберите пакет:
        """
        
        # Удаляем предыдущее сообщение и отправляем новое с изображением
        try:
            await query.delete_message()
        except:
            pass  # Игнорируем ошибки удаления
        
        # Отправляем изображение с информацией о тренировках
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="DianaLisa2.jpg",
            text=training_text,
            reply_markup=keyboards.training_packages(),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_contact_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка обращения в поддержку"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Отправляем информацию о поддержке с изображением
        support_text = """
📞 ПОДДЕРЖКА

💬 Способы связи:
• Telegram: @Dianalisa5
• Email: support@dianalisa.com
• Телефон: +7 (999) 123-45-67

⏰ Время работы: 9:00 - 21:00 (МСК)

❓ Частые вопросы смотрите в FAQ
        """
        
        # Удаляем предыдущее сообщение и отправляем новое с изображением
        try:
            await query.delete_message()
        except:
            pass  # Игнорируем ошибки удаления
        
        # Отправляем изображение с информацией о поддержке
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="DianaLisa2.jpg",
            text=support_text,
            reply_markup=keyboards.back_to_main(),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_training_day_1(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка тренировки дня 1"""
        query = update.callback_query
        await send_training_content(query, 1, context)
    
    async def handle_training_day_2(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка тренировки дня 2"""
        query = update.callback_query
        await send_training_content(query, 2, context)
    
    async def handle_training_day_3(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка тренировки дня 3"""
        query = update.callback_query
        await send_training_content(query, 3, context)
    
    async def handle_mark_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Отметка выполнения тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Извлекаем номер дня из callback_data (mark_training_1, mark_training_2, и т.д.)
        try:
            day_from_callback = int(callback_data.split('_')[-1])
            logger.info(f"День из callback_data: {day_from_callback}")
        except:
            day_from_callback = None
            logger.warning(f"Не удалось извлечь день из callback_data: {callback_data}")
        
        try:
            # Логируем действие пользователя
            enhanced_logger.log_user_action(user_id, 'mark_training_clicked')

            # Получаем пользователя из БД
            try:
                user = db.get_user(user_id)
            except Exception as db_error:
                logger.error(f"Ошибка получения пользователя: {db_error}")
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Ошибка получения данных пользователя"
                )
                return
            
            if not user:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Пользователь не найден"
                )
                return

            # Если тренировка уже выполнена, показываем обратную связь
            if user.get('training_completed', False):
                # Используем день из callback если есть, иначе из БД
                current_day = day_from_callback if day_from_callback else user.get('current_day', 1)
                logger.info(f"Используем день для обратной связи: {current_day}")
                
                # Удаляем предыдущее сообщение
                try:
                    await query.delete_message()
                except:
                    pass
                
                # Отправляем сообщение с кнопками оценки
                keyboard = keyboards.like_dislike_menu(current_day)
                message_text = f"🎯 Тренировка День {current_day} завершена!\n\nКак прошла тренировка?"
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    reply_markup=keyboard
                )
                
                enhanced_logger.log_user_action(user_id, 'training_feedback_requested')
                return

            # Переключаем состояние
            new_state = not user.get('training_completed', False)
            try:
                db.update_user(user_id, training_completed=new_state)
                db.add_analytics_event(user_id, 'training_toggled', f'state_{new_state}')
            except Exception as update_error:
                logger.error(f"Ошибка обновления пользователя: {update_error}")
                # Продолжаем выполнение

            # Обновляем данные пользователя для клавиатуры
            user['training_completed'] = new_state

            if new_state:
                # Добавляем совет в коллекцию
                training_tip = "Регулярные тренировки ускоряют метаболизм на 24 часа!"
                try:
                    db.add_tip_to_collection(user_id, 'training', training_tip)
                except Exception as tip_error:
                    logger.error(f"Ошибка добавления совета: {tip_error}")
                    # Продолжаем выполнение
                
                # Получаем текущий день тренировки - используем день из callback если есть
                current_day = day_from_callback if day_from_callback else user.get('current_day', 1)
                logger.info(f"Отправляем обратную связь для дня: {current_day}")
                
                # Удаляем предыдущее сообщение и показываем обратную связь
                try:
                    await query.delete_message()
                except:
                    pass
                
                try:
                    await self.start_training_feedback(user_id, current_day, context)
                    enhanced_logger.log_user_action(user_id, 'training_marked_completed')
                except Exception as feedback_error:
                    logger.error(f"Ошибка отправки обратной связи: {feedback_error}")
                    # Fallback - отправляем простое сообщение
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🎯 Тренировка День {current_day} завершена!\n\nКак прошла тренировка?",
                            reply_markup=keyboards.like_dislike_menu(current_day)
                        )
                        enhanced_logger.log_user_action(user_id, 'training_marked_completed_fallback')
                    except Exception as fallback_error:
                        logger.error(f"Ошибка fallback сообщения: {fallback_error}")
                return
            else:
                message = "❌ Тренировка отмечена как не выполненная"
                enhanced_logger.log_user_action(user_id, 'training_marked_incomplete')
                
                # Удаляем предыдущее сообщение и отправляем новое с изображением
                try:
                    await query.delete_message()
                except:
                    pass
                
                # Отправляем изображение с сообщением
                try:
                    from utils import send_image_with_text
                    await send_image_with_text(
                        bot=context.bot,
                        chat_id=user_id,
                        image_path="DianaLisa2.jpg",
                        text=message,
                        reply_markup=keyboards.main_menu(),
                        parse_mode=ParseMode.HTML
                    )
                except Exception as image_error:
                    logger.error(f"Ошибка отправки изображения: {image_error}")
                    # Fallback - отправляем простое сообщение
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=message,
                            reply_markup=keyboards.main_menu(),
                            parse_mode=ParseMode.HTML
                        )
                    except Exception as fallback_error:
                        logger.error(f"Ошибка fallback сообщения: {fallback_error}")

        except Exception as e:
            logger.error(f"Ошибка обработки отметки тренировки: {e}")
            # Удаляем предыдущее сообщение и отправляем новое
            try:
                await query.delete_message()
            except:
                pass  # Игнорируем ошибки удаления
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ Произошла ошибка при обработке запроса"
            )
    
    async def handle_timezone_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка выбора часового пояса"""
        query = update.callback_query
        user_id = query.from_user.id
        
        timezone = callback_data.replace('timezone_', '')
        
        # Завершаем регистрацию с выбранным часовым поясом
        from registration import registration_handler
        await registration_handler.complete_timezone_selection(update, context, timezone)
    
    # ============================================================================
    # ПЛАТЕЖИ И ПОДПИСКИ
    # ============================================================================
    
    async def handle_buy_course(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка покупки курса"""
        query = update.callback_query
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="💎 Выберите пакет курса:",
            reply_markup=keyboards.course_packages()
        )
    
    async def handle_buy_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка покупки тренировок"""
        query = update.callback_query
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="💻 Выберите пакет тренировок:",
            reply_markup=keyboards.training_packages()
        )
    
    async def handle_package_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка выбора пакета"""
        query = update.callback_query
        user_id = query.from_user.id
        
        package_type = callback_data.replace('package_', '')
        
        # Создаем инвойс для оплаты
        await create_payment_invoice(query, package_type, 'course')
    
    async def handle_training_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка выбора тренировок"""
        query = update.callback_query
        user_id = query.from_user.id
        
        training_type = callback_data.replace('training_', '')
        
        # Создаем инвойс для оплаты
        await create_payment_invoice(query, training_type, 'training')
    
    # ============================================================================
    # АДМИН-ПАНЕЛЬ
    # ============================================================================
    
    async def handle_admin_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка админских действий"""
        if callback_data == 'admin_panel':
            # Для кнопки админ-панели вызываем команду /admin
            await self.handle_admin_command(update, context)
        else:
            await handle_admin_actions(update, context, callback_data)
    
    async def handle_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /admin через callback"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем права админа
        from config import ADMIN_IDS
        if user_id not in ADMIN_IDS:
            await query.answer("❌ У вас нет прав доступа к админ-панели.")
            return
        
        # Удаляем предыдущее сообщение
        try:
            await query.delete_message()
        except:
            pass
        
        # Показываем админ-панель напрямую
        admin_text = """
🛠 <b>Админ-панель DianaLisa Bot</b>

👋 Добро пожаловать в панель управления!

📊 <b>Доступные функции:</b>
• Статистика пользователей
• Аналитика и отчеты
• Управление пользователями
• Статистика платежей
• Отзывы и рейтинги
• Рассылка сообщений
• Экспорт базы данных

🎯 Выберите действие:
        """
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=admin_text,
            reply_markup=keyboards.admin_menu(),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка оценки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        rating = int(callback_data.replace('rating_', ''))
        db.add_analytics_event(user_id, 'rating_given', str(rating))
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"⭐ Спасибо за оценку {rating}/5! Ваше мнение очень важно для нас!",
            reply_markup=keyboards.back_to_main()
        )
    
    async def handle_yes(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка ответа 'Да'"""
        query = update.callback_query
        user_id = query.from_user.id
        
        db.add_analytics_event(user_id, 'yes_clicked')
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✅ Отлично! Продолжаем!",
            reply_markup=keyboards.main_menu()
        )
    
    async def handle_no(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка ответа 'Нет'"""
        query = update.callback_query
        user_id = query.from_user.id
        
        db.add_analytics_event(user_id, 'no_clicked')
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ Понятно. Возвращаемся в главное меню.",
            reply_markup=keyboards.main_menu()
        )
    
    async def handle_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка подтверждения"""
        query = update.callback_query
        user_id = query.from_user.id
        
        action = callback_data.replace('confirm_', '')
        db.add_analytics_event(user_id, 'action_confirmed', action)
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"✅ Действие '{action}' подтверждено!",
            reply_markup=keyboards.back_to_main()
        )
    
    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка отмены"""
        query = update.callback_query
        user_id = query.from_user.id
        
        db.add_analytics_event(user_id, 'action_cancelled')
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ Действие отменено.",
            reply_markup=keyboards.main_menu()
        )
    
    async def handle_pagination(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка пагинации"""
        query = update.callback_query
        
        # Здесь можно реализовать логику пагинации
        await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="📄 Пагинация будет реализована в следующих версиях.",
                    reply_markup=keyboards.back_to_main()
        )
    
    async def handle_confirm_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка подтверждения рассылки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем права админа
        from admin import admin_panel
        if not admin_panel.is_admin(user_id):
            await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="❌ У вас нет прав доступа к админ-панели.",
                    reply_markup=keyboards.back_to_main()
            )
            return
        
        # Получаем сообщение для рассылки
        message_text = context.user_data.get('broadcast_message')
        if not message_text:
            await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="❌ Сообщение для рассылки не найдено.",
                    reply_markup=keyboards.admin_menu()
            )
            return
        
        # Выполняем рассылку
        await admin_panel.execute_broadcast(query, message_text)
        
        # Очищаем данные
        context.user_data['broadcast_message'] = None
    
    async def handle_cancel_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка отмены рассылки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем права админа
        from admin import admin_panel
        if not admin_panel.is_admin(user_id):
            await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="❌ У вас нет прав доступа к админ-панели.",
                    reply_markup=keyboards.back_to_main()
            )
            return
        
        # Очищаем данные
        context.user_data['broadcast_message'] = None
        
        await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="❌ Рассылка отменена.",
                    reply_markup=keyboards.admin_menu()
        )
    
    async def handle_noop(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Заглушка для кнопок без действия"""
        pass
    
    async def start_training_feedback(self, user_id: int, day: int, context: ContextTypes.DEFAULT_TYPE):
        """Автоматический запуск оценки тренировки"""
        try:
            # Создаем клавиатуру
            keyboard = keyboards.like_dislike_menu(day)
            
            # Отправляем сообщение
            message_text = f"🎯 Тренировка День {day} завершена!\n\nКак прошла тренировка?"
            
            # Отправляем простое сообщение без изображения
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения обратной связи: {e}")
            
            # Fallback - отправляем простое сообщение
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎯 Тренировка День {day} завершена!\n\nКак прошла тренировка?",
                    reply_markup=keyboards.like_dislike_menu(day)
                )
            except Exception as fallback_error:
                logger.error(f"Ошибка fallback сообщения: {fallback_error}")
    
    async def handle_training_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка начала оценки тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            # Парсим callback_data: training_feedback_1 -> day=1
            parts = callback_data.split('_')
            if len(parts) < 3:
                raise ValueError(f"Неверный формат callback_data: {callback_data}")
            
            day = int(parts[2])
            logger.info(f"Пользователь {user_id} начал оценку тренировки дня {day}")
            
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📝 Оценка тренировки День {day}\n\n"
                     "Насколько сложной была для тебя эта тренировка?",
                reply_markup=keyboards.difficulty_rating_menu(day)
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки оценки тренировки: {e}")
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при обработке запроса"
            )
    
    async def handle_difficulty_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка оценки сложности тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            # Парсим callback_data: difficulty_1_1 -> rating=1, day=1
            parts = callback_data.split('_')
            if len(parts) < 3:
                raise ValueError(f"Неверный формат callback_data: {callback_data}")
            
            rating = int(parts[1])
            day = int(parts[2])
            
            # Сохраняем оценку сложности в контексте
            context.user_data[f'difficulty_{day}'] = rating
            
            logger.info(f"Пользователь {user_id} оценил сложность тренировки дня {day}: {rating}")
            
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📝 Оценка тренировки День {day}\n\n"
                     "Насколько понятными были инструкции?",
                reply_markup=keyboards.clarity_rating_menu(day)
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки оценки сложности: {e}")
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при обработке запроса"
            )
    
    async def handle_clarity_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка оценки понятности тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            # Парсим callback_data: clarity_1_1 -> rating=1, day=1
            parts = callback_data.split('_')
            if len(parts) < 3:
                raise ValueError(f"Неверный формат callback_data: {callback_data}")
            
            rating = int(parts[1])
            day = int(parts[2])
            
            # Сохраняем оценку понятности в контексте
            context.user_data[f'clarity_{day}'] = rating
            
            logger.info(f"Пользователь {user_id} оценил понятность тренировки дня {day}: {rating}")
            
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📝 Оценка тренировки День {day}\n\n"
                     "Хочешь добавить комментарий к тренировке?",
                reply_markup=keyboards.comments_menu(day)
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки оценки понятности: {e}")
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при обработке запроса"
            )
    
    async def handle_finish_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Завершение оценки тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            # Парсим callback_data: finish_feedback_1 -> day=1
            parts = callback_data.split('_')
            if len(parts) < 3:
                raise ValueError(f"Неверный формат callback_data: {callback_data}")
            
            day = int(parts[2])
            
            # Получаем оценки из контекста
            difficulty = context.user_data.get(f'difficulty_{day}', 3)
            clarity = context.user_data.get(f'clarity_{day}', 3)
            
            # Сохраняем оценку в базу данных
            success = db.add_training_feedback(user_id, day, difficulty, clarity)
            
            if success:
                # Очищаем данные из контекста
                context.user_data.pop(f'difficulty_{day}', None)
                context.user_data.pop(f'clarity_{day}', None)
                
                logger.info(f"Оценка тренировки дня {day} сохранена для пользователя {user_id}")
                
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=f"✅ Спасибо за оценку тренировки День {day}!\n\n"
                         "Твоя обратная связь поможет улучшить курс! 💪",
                    reply_markup=keyboards.main_menu()
                )
            else:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="❌ Ошибка сохранения оценки. Попробуй еще раз.",
                    reply_markup=keyboards.main_menu()
                )
                
        except Exception as e:
            logger.error(f"Ошибка завершения оценки: {e}")
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при обработке запроса"
            )
    
    async def handle_skip_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Пропуск оценки тренировки"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            logger.info(f"Пользователь {user_id} пропустил оценку тренировки")
            
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="⏭️ Оценка пропущена\n\n"
                     "Ты всегда можешь оценить тренировку позже!",
                    reply_markup=keyboards.main_menu()
            )
            
        except Exception as e:
            logger.error(f"Ошибка пропуска оценки: {e}")
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="❌ Произошла ошибка при обработке запроса"
            )
    
    async def handle_view_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Показ результатов курса"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            summary = db.get_user_course_summary(user_id)
            if not summary:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="❌ Не удалось получить результаты курса",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            # Формируем отчет
            from utils import format_course_progress
            
            course_progress = format_course_progress(summary['current_day'], 3)
            
            report_text = f"""
🎉 <b>Поздравляем с завершением курса!</b>

{course_progress}

👤 <b>Имя:</b> {summary['user_name']}
🏋️‍♀️ <b>Выполнено тренировок:</b> {summary['completed_trainings']}/3

📈 <b>Средние оценки:</b>
• Сложность: {summary['avg_difficulty']}/5
• Понятность: {summary['avg_clarity']}/5

💪 Ты отлично справляешься! Продолжай в том же духе!
            """
            
            await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=report_text,
                    reply_markup=keyboards.course_completion_menu(),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа результатов: {e}")
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="❌ Произошла ошибка при обработке запроса"
            )

    # ========== НЕДОСТАЮЩИЕ ОБРАБОТЧИКИ ==========
    
    async def handle_admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка статистики админки"""
        query = update.callback_query
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📊 Статистика бота",
            reply_markup=keyboards.admin_menu()
        )
    
    async def handle_admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка управления пользователями"""
        query = update.callback_query
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="👥 Управление пользователями",
            reply_markup=keyboards.admin_menu()
        )
    
    async def handle_admin_payments(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка платежей"""
        query = update.callback_query
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="💳 Управление платежами",
            reply_markup=keyboards.admin_menu()
        )
    
    async def handle_admin_reviews(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка отзывов"""
        query = update.callback_query
        
        # Удаляем сообщение и отправляем новое вместо edit_message_text
        try:
            await query.delete_message()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="⭐ Управление отзывами",
            reply_markup=keyboards.admin_menu()
        )
    
    async def handle_admin_training_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка отзывов о тренировках"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем права админа
        if user_id not in ADMIN_IDS:
            await query.answer("❌ У вас нет прав администратора")
            return
        
        await query.answer()
        
        # Вызываем функцию показа отзывов о тренировках
        admin_panel = AdminPanel()
        await admin_panel.show_training_feedback(query)
    
    async def handle_admin_analytics(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка аналитики"""
        query = update.callback_query
        await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="📈 Аналитика",
                    reply_markup=keyboards.admin_menu())
    
    async def handle_admin_export_db(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка экспорта базы данных"""
        query = update.callback_query
        await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="📤 Экспорт базы данных",
                    reply_markup=keyboards.admin_menu())
    
    async def handle_admin_send_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка отправки сообщений"""
        query = update.callback_query
        await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="📨 Отправка сообщений",
                    reply_markup=keyboards.admin_menu())
    
    async def handle_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка админ-меню"""
        query = update.callback_query
        await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="🛠 Админ-панель",
                    reply_markup=keyboards.admin_menu())
    
    async def handle_admin_clear_db(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка очистки БД"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем права админа
        if user_id not in ADMIN_IDS:
            await query.answer("❌ У вас нет прав администратора")
            return
        
        # Показываем подтверждение
        confirmation_text = """
⚠️ <b>ПОДТВЕРЖДЕНИЕ ОЧИСТКИ БД</b>

🗑️ Это действие удалит ВСЕ данные:
• Всех пользователей
• Историю тренировок
• Аналитику
• Платежи
• Отзывы

❌ <b>Данные восстановить НЕЛЬЗЯ!</b>

Вы уверены, что хотите продолжить?
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Да, очистить БД", callback_data='confirm_clear_db')],
            [InlineKeyboardButton("❌ Отмена", callback_data='admin_panel')]
        ]
        
        await query.edit_message_text(
            confirmation_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_rating_1(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка рейтинга 1"""
        await self.handle_rating(update, context, "rating_1")
    
    async def handle_rating_2(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка рейтинга 2"""
        await self.handle_rating(update, context, "rating_2")
    
    async def handle_rating_3(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка рейтинга 3"""
        await self.handle_rating(update, context, "rating_3")
    
    async def handle_rating_4(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка рейтинга 4"""
        await self.handle_rating(update, context, "rating_4")
    
    async def handle_rating_5(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка рейтинга 5"""
        await self.handle_rating(update, context, "rating_5")
    
    async def handle_timezone_moscow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Москва"""
        await self.handle_timezone_selection(update, context, "timezone_Europe/Moscow")
    
    async def handle_timezone_kiev(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Киев"""
        await self.handle_timezone_selection(update, context, "timezone_Europe/Kiev")
    
    async def handle_timezone_minsk(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Минск"""
        await self.handle_timezone_selection(update, context, "timezone_Europe/Minsk")
    
    async def handle_timezone_almaty(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Алматы"""
        await self.handle_timezone_selection(update, context, "timezone_Asia/Almaty")
    
    async def handle_timezone_new_york(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Нью-Йорк"""
        await self.handle_timezone_selection(update, context, "timezone_America/New_York")
    
    async def handle_timezone_london(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Лондон"""
        await self.handle_timezone_selection(update, context, "timezone_Europe/London")
    
    async def handle_timezone_berlin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Берлин"""
        await self.handle_timezone_selection(update, context, "timezone_Europe/Berlin")
    
    async def handle_timezone_paris(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Париж"""
        await self.handle_timezone_selection(update, context, "timezone_Europe/Paris")
    
    async def handle_timezone_tokyo(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Токио"""
        await self.handle_timezone_selection(update, context, "timezone_Asia/Tokyo")
    
    async def handle_timezone_sydney(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка часового пояса Сидней"""
        await self.handle_timezone_selection(update, context, "timezone_Australia/Sydney")
    
    async def handle_package_basic(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка базового пакета"""
        await self.handle_package_selection(update, context, "package_basic")
    
    async def handle_payment_success(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка успешного платежа"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            await query.answer("Платеж успешно обработан!")
            await query.edit_message_text(
                "✅ Платеж успешно обработан!\n\nСпасибо за покупку!",
                reply_markup=keyboards.back_to_main()
            )
            enhanced_logger.log_user_action(user_id, 'payment_success')
        except Exception as e:
            logger.error(f"Ошибка обработки успешного платежа: {e}")
    
    async def handle_payment_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка отмены платежа"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            await query.answer("Платеж отменен")
            await query.edit_message_text(
                "❌ Платеж отменен.\n\nВы можете попробовать снова позже.",
                reply_markup=keyboards.back_to_main()
            )
            enhanced_logger.log_user_action(user_id, 'payment_cancel')
        except Exception as e:
            logger.error(f"Ошибка обработки отмены платежа: {e}")
    
    async def handle_training_single(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка одиночной тренировки"""
        await self.handle_training_selection(update, context, "training_single")
    
    async def handle_training_pack5(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка пакета из 5 тренировок"""
        await self.handle_training_selection(update, context, "training_pack5")
    
    async def handle_training_pack10(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка пакета из 10 тренировок"""
        await self.handle_training_selection(update, context, "training_pack10")
    
    async def handle_training_unlimited(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка безлимитных тренировок"""
        await self.handle_training_selection(update, context, "training_unlimited")
    
    async def handle_start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка начала регистрации"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем, есть ли пользователь в базе
        user = db.get_user(user_id)
        if user:
            # Удаляем предыдущее сообщение и отправляем новое
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Вы уже зарегистрированы! Добро пожаловать обратно!",
                reply_markup=keyboards.main_menu()
            )
            return
        
        # Начинаем процесс регистрации
        from registration import registration_handler
        
        # Удаляем предыдущее сообщение
        try:
            await query.delete_message()
        except:
            pass
        
        # Отправляем сообщение с запросом имени и картинкой
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="DianaLisa1.jpg",
            text=MESSAGES['name_request'],
            reply_markup=keyboards.name_input_keyboard(),
            parse_mode=ParseMode.HTML
        )
        
        # Инициализируем состояние регистрации
        await registration_handler.start_registration(update, context)
    
    async def handle_back_to_registration_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка возврата к началу регистрации"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем, есть ли пользователь в базе
        user = db.get_user(user_id)
        if user:
            # Удаляем предыдущее сообщение и отправляем новое
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Вы уже зарегистрированы! Добро пожаловать обратно!",
                reply_markup=keyboards.main_menu()
            )
            return
        
        # Удаляем предыдущее сообщение
        try:
            await query.delete_message()
        except:
            pass
        
        # Отправляем начальное сообщение регистрации с картинкой
        from utils import send_image_with_text
        await send_image_with_text(
            bot=context.bot,
            chat_id=user_id,
            image_path="DianaLisa1.jpg",
            text=MESSAGES['start_registration_welcome'],
            reply_markup=keyboards.start_registration_menu(),
            parse_mode=ParseMode.HTML
        )
    
    # ============================================================================
    # ОБРАТНАЯ СВЯЗЬ И ОТЗЫВЫ
    # ============================================================================
    
    async def handle_feedback_like(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка положительной обратной связи"""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            logger.info(f"[FEEDBACK_LIKE] START для user {user_id}")
            
            # Извлекаем номер дня из callback_data
            day = int(callback_data.split('_')[-1])
            logger.info(f"[FEEDBACK_LIKE] День: {day}")
            
            # Получаем пользователя
            logger.info(f"[FEEDBACK_LIKE] Получаем пользователя")
            user = db.get_user(user_id)
            current_day = user.get('current_day', 1)
            logger.info(f"[FEEDBACK_LIKE] Текущий день: {current_day}")
            
            # Планируем следующий день
            if current_day < 3:
                logger.info(f"[FEEDBACK_LIKE] Планируем день {current_day + 1}")
                try:
                    await self.schedule_next_day_opening(user_id, current_day + 1, context)
                    enhanced_logger.log_user_action(user_id, 'day_scheduled', {'day': current_day + 1, 'time': '06:00'})
                except Exception as e:
                    logger.error(f"[FEEDBACK_LIKE] Ошибка планирования: {e}")
            
            # Удаляем сообщение
            logger.info(f"[FEEDBACK_LIKE] Удаляем сообщение")
            try:
                await query.delete_message()
            except Exception as e:
                logger.error(f"[FEEDBACK_LIKE] Ошибка удаления: {e}")
            
            # Формируем текст
            next_day_text = f"День {current_day + 1}" if current_day < 3 else "завершение курса"
            logger.info(f"[FEEDBACK_LIKE] Отправляем ответ")
            
            # Отправляем ответ
            from utils import send_image_with_text
            await send_image_with_text(
                bot=context.bot,
                chat_id=user_id,
                image_path="DianaLisa2.jpg",
                text=f"😊 Отлично! Спасибо за положительную обратную связь!\n\n"
                     f"🎯 Следующая тренировка ({next_day_text}) будет доступна завтра в 6:00!\n\n"
                     f"Отличная работа! 💪",
                reply_markup=keyboards.back_to_main(),
                parse_mode=ParseMode.HTML
            )
            logger.info(f"[FEEDBACK_LIKE] SUCCESS")
            
        except Exception as e:
            logger.error(f"[FEEDBACK_LIKE] ОШИБКА: {e}", exc_info=True)
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ Произошла ошибка",
                    reply_markup=keyboards.main_menu()
                )
            except:
                pass
    
    async def handle_feedback_dislike(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка отрицательной обратной связи"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Извлекаем номер дня из callback_data
        day = int(callback_data.split('_')[-1])
        
        try:
            # Удаляем предыдущее сообщение и отправляем новое
            try:
                await query.delete_message()
            except:
                pass  # Игнорируем ошибки удаления
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"😞 Мне очень жаль, что тренировка День {day} не понравилась.\n\n"
                     "Что именно не понравилось? Пожалуйста, опишите подробнее:",
                reply_markup=keyboards.text_input_menu(),
                parse_mode=ParseMode.HTML
            )
            
            # Сохраняем состояние ожидания текстового отзыва
            context.user_data[f'waiting_feedback_{user_id}'] = day
            
        except Exception as e:
            logger.error(f"Ошибка обработки отрицательной обратной связи: {e}")
            # Удаляем предыдущее сообщение и отправляем новое
            try:
                await query.delete_message()
            except:
                pass  # Игнорируем ошибки удаления
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ Произошла ошибка. Попробуйте еще раз.",
                reply_markup=keyboards.main_menu()
            )
    
    def log_feedback(self, user_id: int, day: int, feedback_type: str, details: str):
        """Запись обратной связи в базу данных и файл"""
        try:
            import os
            from datetime import datetime
            
            # Записываем в файл для резервного копирования
            feedback_file = "training_feedback.txt"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] User {user_id}, Day {day}, Type: {feedback_type}, Details: {details}\n")
            
            # Записываем в базу данных
            from database import db
            success = db.add_training_feedback(user_id, day, 
                                             difficulty_rating=5 if feedback_type == "like" else 1,
                                             clarity_rating=5 if feedback_type == "like" else 1,
                                             comments=details)
            
            if success:
                logger.info(f"Обратная связь записана в БД: User {user_id}, Day {day}, Type: {feedback_type}")
            else:
                logger.error(f"Ошибка записи обратной связи в БД: User {user_id}, Day {day}, Type: {feedback_type}")
                
        except Exception as e:
            logger.error(f"Ошибка записи обратной связи: {e}")
    
    async def schedule_next_day_opening(self, user_id: int, next_day: int, context: ContextTypes.DEFAULT_TYPE):
        """Планирование открытия следующего дня тренировки в 6:00"""
        try:
            logger.info(f"[SCHEDULE] Начало планирования Дня {next_day} для пользователя {user_id}")
            
            from jobs import scheduler
            from datetime import datetime, timedelta
            import pytz
            
            # Получаем пользователя для определения часового пояса
            user = db.get_user(user_id)
            if not user:
                logger.error(f"[SCHEDULE] Пользователь {user_id} не найден в БД")
                return
                
            user_timezone = user.get('timezone') or 'Europe/Moscow'  # Защита от None
            if user_timezone is None:
                user_timezone = 'Europe/Moscow'
            logger.info(f"[SCHEDULE] Часовой пояс пользователя: {user_timezone}")
            
            # Планируем открытие на завтра в 6:00
            tz = pytz.timezone(user_timezone)
            now = datetime.now(tz)
            tomorrow_6am = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            logger.info(f"[SCHEDULE] Запланированное время: {tomorrow_6am}")
            
            # Проверяем доступность планировщика
            if not hasattr(scheduler, 'scheduler'):
                logger.error(f"[SCHEDULE] Планировщик не доступен!")
                return
            
            # Добавляем задачу в планировщик
            job_id = f"open_day_{next_day}_{user_id}"
            logger.info(f"[SCHEDULE] Добавляем задачу с ID: {job_id}")
            
            scheduler.scheduler.add_job(
                func=self.open_next_training_day,
                trigger='date',
                run_date=tomorrow_6am,
                args=[user_id, next_day, context],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"[SCHEDULE] [OK] Успешно запланировано открытие Дня {next_day} для пользователя {user_id} на {tomorrow_6am}")
            
        except Exception as e:
            logger.error(f"[SCHEDULE] [FAIL] Ошибка планирования открытия следующего дня: {e}", exc_info=True)
    
    async def open_next_training_day(self, user_id: int, day: int, context: ContextTypes.DEFAULT_TYPE):
        """Открытие следующего дня тренировки"""
        try:
            # Обновляем current_day пользователя
            db.update_user(user_id, current_day=day)
            enhanced_logger.log_user_action(user_id, 'day_opened_scheduled', {'day': day, 'time': '06:00'})
            
            # Отправляем уведомление пользователю
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🌅 Доброе утро!\n\n"
                     f"🎯 Тренировка День {day} теперь доступна!\n\n"
                     f"Время начинать новый день тренировок! 💪",
                reply_markup=keyboards.main_menu(),
                parse_mode=ParseMode.HTML
            )
            
            logger.info(f"Открыт День {day} для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка открытия следующего дня: {e}")
    
    async def handle_leave_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка оставления отзыва"""
        query = update.callback_query
        await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="⭐ Спасибо за ваш отзыв! Ваше мнение очень важно для нас.",
                    reply_markup=keyboards.main_menu()
        )
    
    async def handle_confirm_clear_db(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка подтверждения очистки базы данных"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Проверяем права админа
        from config import ADMIN_IDS
        if user_id not in ADMIN_IDS:
            await query.answer("❌ У вас нет прав доступа к этой функции.")
            return
        
        # Вызываем функцию очистки базы данных из админ-панели
        from admin import admin_panel
        await admin_panel.clear_database(query)

# Глобальный экземпляр обработчиков
callback_handlers = CallbackHandlers()
