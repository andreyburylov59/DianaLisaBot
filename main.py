"""
🚀 Основной файл бота DianaLisa
Точка входа, инициализация и запуск бота
"""

import asyncio
import logging
import nest_asyncio
import psutil
import signal
import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, filters, ContextTypes
)

# Импорты модулей
from config import BOT_TOKEN, ADMIN_IDS
from logger import setup_logging, get_logger, log_user_action, log_error
from enhanced_logger import main_logger
from database import db
from keyboards import keyboards
from callbacks import callback_handlers
from registration import registration_handler
from training import training_system
from payment import payment_system
from admin import admin_panel
from info import info_system
from utils import utils
# from validation import error_handler  # Модуль не существует

# Настройка логирования
setup_logging()

# Отключаем логирование httpx (HTTP запросы)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpx").disabled = True

logger = get_logger(__name__)

# Поддержка Windows
nest_asyncio.apply()

# Глобальная переменная для приложения
application = None

class DianaLisaBot:
    """Основной класс бота DianaLisa"""
    
    def __init__(self):
        self.application = None
        self.bot_token = BOT_TOKEN
        self.admin_ids = ADMIN_IDS
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        try:
            user_id = update.effective_user.id
            user_data = update.effective_user
            
            # Логируем действие пользователя
            log_user_action(user_id, 'start_command')
            
            # Проверяем, есть ли реферальный код
            referral_code = None
            if context.args:
                referral_code = context.args[0]
            
            # Проверяем, зарегистрирован ли пользователь
            existing_user = db.get_user(user_id)
            if existing_user:
                # Проверяем, является ли пользователь админом
                is_admin = user_id in self.admin_ids
                
                # Отправляем приветствие с изображением для существующего пользователя
                welcome_text = f"""
🌟 <b>Добро пожаловать обратно!</b>

👋 Привет, {existing_user['first_name']}!

💪 Рада видеть тебя снова! Продолжай свой путь к здоровому образу жизни!

🎯 Твой текущий прогресс: День {existing_user.get('current_day', 1)}/3
💎 Статус: {'Премиум' if existing_user.get('is_premium', False) else 'Базовый'}

🏋️‍♀️ Выбери действие:
                """
                
                # Выбираем клавиатуру в зависимости от прав пользователя
                menu_keyboard = keyboards.admin_main_menu() if is_admin else keyboards.main_menu()
                
                # Отправляем изображение с приветствием
                from utils import send_image_with_text
                await send_image_with_text(
                    bot=context.bot,
                    chat_id=user_id,
                    image_path="DianaLisa1.jpg",
                    text=welcome_text,
                    reply_markup=menu_keyboard,
                    parse_mode=ParseMode.HTML
                )
                return  # Важно! Прерываем выполнение, чтобы не запускать регистрацию
            else:
                # Отправляем приветственное сообщение для нового пользователя
                from registration import registration_handler
                await registration_handler.send_welcome_message(update, context)
            
        except Exception as e:
            log_error(e, 'start_command')
            await update.message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, 'help_command')
            
            help_text = """
🆘 ПОМОЩЬ

📋 Основные команды:
/start - Начать работу с ботом
/help - Показать эту справку
/menu - Открыть главное меню
/stats - Показать статистику
/support - Связаться с поддержкой

🏋️‍♀️ Как пользоваться:
1. Зарегистрируйся через /start
2. Выбери часовой пояс
3. Начинай тренировки
4. Отмечай выполнение тренировок

❓ Есть вопросы? Используй кнопку FAQ в меню!
            """
            
            await update.message.reply_text(
                help_text,
                reply_markup=keyboards.back_to_main()
            )
            
        except Exception as e:
            log_error(e, 'help_command')
            await update.message.reply_text(
                "❌ Ошибка загрузки справки.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /menu"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, 'menu_command')
            
            user = db.get_user(user_id)
            if not user:
                await update.message.reply_text(
                    "❌ Сначала нужно зарегистрироваться. Используйте /start",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            await update.message.reply_text(
                f"👋 Главное меню, {user['first_name']}!",
                reply_markup=keyboards.main_menu()
            )
            
        except Exception as e:
            log_error(e, 'menu_command')
            await update.message.reply_text(
                "❌ Ошибка открытия меню.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /stats"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, 'stats_command')
            
            user = db.get_user(user_id)
            if not user:
                await update.message.reply_text(
                    "❌ Сначала нужно зарегистрироваться. Используйте /start",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            stats = db.get_user_stats(user_id)
            training_progress = training_system.get_training_progress(user_id)
            
            stats_text = f"""
📊 ТВОЯ СТАТИСТИКА

👋 Имя: {user['first_name']}
📅 День курса: {user['current_day']}
💎 Статус: {'Премиум' if user['is_premium'] else 'Базовый'}
📅 Регистрация: {user['registration_date'][:10]}

🏋️‍♀️ Тренировки:
• Выполнено: {training_progress.get('total_trainings', 0)}
• Дней пройдено: {training_progress.get('days_completed', 0)}
• Прогресс: {training_progress.get('progress_percentage', 0):.1f}%

💰 Платежи:
• Всего: {stats.get('payments_count', 0)}
• Потрачено: {stats.get('total_spent', 0):.2f} ₽

📈 Активность:
• Кнопок нажато: {stats.get('events', {}).get('button_click', 0)}
• Тренировок завершено: {stats.get('events', {}).get('training_completed', 0)}
            """
            
            await update.message.reply_text(
                stats_text,
                reply_markup=keyboards.back_to_main()
            )
            
        except Exception as e:
            log_error(e, 'stats_command')
            await update.message.reply_text(
                "❌ Ошибка получения статистики.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /support"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, 'support_command')
            
            await info_system.show_support_info(update.message)
            
        except Exception as e:
            log_error(e, 'support_command')
            await update.message.reply_text(
                "❌ Ошибка загрузки информации о поддержке.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /admin"""
        try:
            user_id = update.effective_user.id
            
            if not admin_panel.is_admin(user_id):
                await update.message.reply_text(
                    "❌ У вас нет прав доступа к админ-панели.",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            log_user_action(user_id, 'admin_command')
            
            await update.message.reply_text(
                "🛠 Админ-панель DianaLisa",
                reply_markup=keyboards.admin_menu()
            )
            
        except Exception as e:
            log_error(e, 'admin_command')
            await update.message.reply_text(
                "❌ Ошибка доступа к админ-панели.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            
            # Логируем сообщение пользователя
            log_user_action(user_id, 'text_message', message_text[:100])
            
            # Проверяем, ожидает ли бот сообщение для рассылки
            if context.user_data.get('waiting_for_broadcast'):
                await admin_panel.process_broadcast_message(update, context)
                context.user_data['waiting_for_broadcast'] = False
                return
            
            # Проверяем, ожидает ли бот сообщение для пользователя
            if context.user_data.get('waiting_for_user_message'):
                target_user_id = context.user_data['waiting_for_user_message']
                await admin_panel.process_user_message(update, context, target_user_id)
                context.user_data['waiting_for_user_message'] = None
                return
            
            # Проверяем, ожидает ли бот обратную связь по тренировке
            feedback_key = f'waiting_feedback_{user_id}'
            if context.user_data.get(feedback_key):
                day = context.user_data[feedback_key]
                await self.process_training_feedback(update, context, user_id, day, message_text)
                context.user_data[feedback_key] = None
                return
            
            # Проверяем, находится ли пользователь в процессе регистрации
            if await registration_handler.handle_registration_message(update, context):
                return
            
            # Для всех остальных сообщений показываем главное меню
            await update.message.reply_text(
                "👋 Используйте кнопки меню для навигации или команду /help для справки.",
                reply_markup=keyboards.main_menu()
            )
            
        except Exception as e:
            log_error(e, 'handle_text_message')
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке сообщения.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def process_training_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, day: int, feedback_text: str):
        """Обработка текстовой обратной связи по тренировке"""
        try:
            # Записываем обратную связь в файл
            from callbacks import CallbackHandlers
            callback_handler = CallbackHandlers()
            callback_handler.log_feedback(user_id, day, "dislike", feedback_text)
            
            # Сразу открываем следующий день при отрицательной обратной связи
            user = db.get_user(user_id)
            current_day = user.get('current_day', 1)
            if current_day < 3:
                new_day = current_day + 1
                db.update_user(user_id, current_day=new_day)
                main_logger.log_user_action(user_id, 'day_progress_immediate', {'from_day': current_day, 'to_day': new_day, 'reason': 'dislike'})
            
            # Отправляем ответ пользователю
            next_day_text = f"День {current_day + 1}" if current_day < 3 else "завершение курса"
            await update.message.reply_text(
                f"📝 Спасибо за подробный отзыв о тренировке День {day}!\n\n"
                "Ваше мнение поможет нам улучшить тренировки.\n\n"
                f"🎯 Следующая тренировка ({next_day_text}) уже доступна! Попробуйте её - возможно, она понравится больше! 💪",
                reply_markup=keyboards.main_menu(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            log_error(e, 'process_training_feedback')
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке отзыва.",
                reply_markup=keyboards.main_menu()
            )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback-ов от кнопок"""
        try:
            await callback_handlers.process_callback(update, context)
        except Exception as e:
            log_error(e, 'handle_callback_query')
            await update.callback_query.answer("❌ Произошла ошибка.")
    
    async def handle_pre_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка предварительной проверки платежа"""
        try:
            await payment_system.handle_pre_checkout(update, context)
        except Exception as e:
            log_error(e, 'handle_pre_checkout')
            await update.pre_checkout_query.answer(
                ok=False,
                error_message="Произошла ошибка при обработке платежа"
            )
    
    async def handle_successful_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка успешного платежа"""
        try:
            await payment_system.handle_successful_payment(update, context)
        except Exception as e:
            log_error(e, 'handle_successful_payment')
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке платежа. Обратитесь в поддержку.",
                reply_markup=keyboards.back_to_main()
            )
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        try:
            # Команды
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("menu", self.menu_command))
            self.application.add_handler(CommandHandler("stats", self.stats_command))
            self.application.add_handler(CommandHandler("support", self.support_command))
            self.application.add_handler(CommandHandler("admin", self.admin_command))
            
            # Callback-и
            self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
            
            # Платежи
            self.application.add_handler(PreCheckoutQueryHandler(self.handle_pre_checkout))
            self.application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, self.handle_successful_payment))
            
            # Текстовые сообщения
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
            
            logger.info("Обработчики настроены успешно")
            
        except Exception as e:
            log_error(e, 'setup_handlers')
            raise
    
    async def startup(self):
        """Инициализация при запуске"""
        try:
            # Инициализируем базу данных
            db.init_database()
            logger.info("База данных инициализирована")
            
            # Запускаем планировщик задач
            from jobs import scheduler
            scheduler.start_all_scheduled_jobs()
            logger.info("Планировщик задач запущен")
            
            # Логируем запуск бота
            logger.info("Бот DianaLisa запущен успешно")
            
        except Exception as e:
            log_error(e, 'startup')
            raise
    
    async def shutdown(self):
        """Очистка при завершении"""
        try:
            # Останавливаем планировщик
            from jobs import scheduler
            scheduler.shutdown()
            logger.info("Планировщик остановлен")
            
            # Закрываем соединения с базой данных
            # (SQLite автоматически закрывает соединения)
            
            logger.info("Бот DianaLisa остановлен")
            
        except Exception as e:
            log_error(e, 'shutdown')
    
    def run(self):
        """Запуск бота"""
        try:
            # Проверяем, не запущен ли уже бот
            if self.application is not None:
                logger.warning("Бот уже запущен!")
                return
            
            # Создаем приложение
            self.application = Application.builder().token(self.bot_token).build()
            application = self.application  # Глобальная переменная
            
            # Настраиваем обработчики
            self.setup_handlers()
            
            # Настраиваем обработчики запуска и завершения
            self.application.add_handler(CommandHandler("startup", self.startup))
            self.application.add_handler(CommandHandler("shutdown", self.shutdown))
            
            # Запускаем бота
            logger.info("Запуск бота DianaLisa...")
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False  # Не закрываем event loop при ошибках
            )
            
        except Exception as e:
            log_error(e, 'run')
            logger.critical("Критическая ошибка при запуске бота")
            # Не поднимаем исключение, чтобы не крашить процесс

def check_and_kill_conflicting_processes():
    """Проверяет и останавливает конфликтующие процессы бота"""
    try:
        current_pid = os.getpid()
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Проверяем процессы Python с main.py
                if (proc.info['name'] == 'python.exe' and 
                    proc.info['cmdline'] and 
                    'main.py' in ' '.join(proc.info['cmdline']) and
                    proc.info['pid'] != current_pid):
                    
                    logger.info(f"Найден конфликтующий процесс: PID {proc.info['pid']}")
                    proc.kill()
                    killed_count += 1
                    logger.info(f"Процесс {proc.info['pid']} остановлен")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if killed_count > 0:
            logger.info(f"Остановлено {killed_count} конфликтующих процессов")
            # Даем время процессам завершиться
            import time
            time.sleep(2)
        else:
            logger.info("Конфликтующих процессов не найдено")
            
    except Exception as e:
        logger.error(f"Ошибка при проверке конфликтующих процессов: {e}")

def setup_signal_handlers():
    """Настройка обработчиков сигналов для корректного завершения"""
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}, завершаем работу...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Главная функция"""
    try:
        # Настройка обработчиков сигналов
        setup_signal_handlers()
        
        # Проверка и остановка конфликтующих процессов
        check_and_kill_conflicting_processes()
        
        # Проверяем токен бота
        if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            logger.critical("Не установлен токен бота! Установите BOT_TOKEN в config.py")
            return
        
        # Создаем и запускаем бота
        bot = DianaLisaBot()
        
        # Обработка конфликтов и перезапуск
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                bot.run()
                break
            except Exception as e:
                if "Conflict" in str(e) and "getUpdates" in str(e):
                    retry_count += 1
                    logger.warning(f"Конфликт с другим экземпляром бота. Попытка {retry_count}/{max_retries}")
                    if retry_count < max_retries:
                        import time
                        time.sleep(5)  # Ждем 5 секунд перед повтором
                        continue
                else:
                    raise
        
        if retry_count >= max_retries:
            logger.critical("Не удалось запустить бота после нескольких попыток")
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        log_error(e, 'main')
        logger.critical("Критическая ошибка в главной функции")

if __name__ == '__main__':
    main()
