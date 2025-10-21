"""
🕒 Планировщик задач и напоминания для бота DianaLisa
Управление расписанием, напоминаниями и автоматическими задачами
"""

import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pytz import timezone
import pytz

from config import SCHEDULER_SETTINGS, MESSAGES
from database import db
from utils import get_user_timezone
from training import training_system

logger = logging.getLogger(__name__)

class JobScheduler:
    """Класс для управления планировщиком задач"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.job_ids = {}  # Хранение ID задач для каждого пользователя
        self._started = False
    
    def schedule_user_jobs(self, user_id: int, user_timezone: str = 'Europe/Moscow'):
        """Планирование задач для пользователя"""
        try:
            # Удаляем старые задачи пользователя
            self.remove_user_jobs(user_id)
            
            # Получаем часовой пояс пользователя
            tz = timezone(user_timezone)
            
            # Утреннее мотивационное сообщение (8:00)
            morning_job_id = f"morning_{user_id}"
            self.scheduler.add_job(
                func=self.send_morning_motivation,
                trigger=CronTrigger(hour=8, minute=0, timezone=tz),
                args=[user_id],
                id=morning_job_id,
                replace_existing=True,
                max_instances=1
            )
            
            # Вечерняя мотивация (20:00)
            evening_job_id = f"evening_{user_id}"
            self.scheduler.add_job(
                func=self.send_evening_motivation,
                trigger=CronTrigger(hour=20, minute=0, timezone=tz),
                args=[user_id],
                id=evening_job_id,
                replace_existing=True,
                max_instances=1
            )
            
            # Напоминание о тренировке (18:00)
            training_job_id = f"training_{user_id}"
            self.scheduler.add_job(
                func=self.send_training_reminder,
                trigger=CronTrigger(hour=18, minute=0, timezone=tz),
                args=[user_id],
                id=training_job_id,
                replace_existing=True,
                max_instances=1
            )
            
            # Сохраняем ID задач
            self.job_ids[user_id] = {
                'morning': morning_job_id,
                'evening': evening_job_id,
                'training': training_job_id
            }
            
            # Сохраняем задачи в базу данных
            db.add_scheduled_job(user_id, 'morning_motivation', datetime.now().replace(hour=8, minute=0))
            db.add_scheduled_job(user_id, 'evening_motivation', datetime.now().replace(hour=20, minute=0))
            db.add_scheduled_job(user_id, 'training_reminder', datetime.now().replace(hour=18, minute=0))
            
            logger.info(f"Задачи запланированы для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка планирования задач для пользователя {user_id}: {e}")
    
    def remove_user_jobs(self, user_id: int):
        """Удаление задач пользователя"""
        try:
            if user_id in self.job_ids:
                for job_id in self.job_ids[user_id].values():
                    try:
                        self.scheduler.remove_job(job_id)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить задачу {job_id}: {e}")
                
                del self.job_ids[user_id]
            
            # Деактивируем задачи в базе данных
            jobs = db.get_scheduled_jobs(user_id)
            for job in jobs:
                db.deactivate_job(job['id'])
            
            logger.info(f"Задачи пользователя {user_id} удалены")
            
        except Exception as e:
            logger.error(f"Ошибка удаления задач пользователя {user_id}: {e}")
    
    async def send_morning_motivation(self, user_id: int):
        """Отправка утреннего мотивационного сообщения"""
        try:
            # Получаем глобальное приложение
            import main
            application = main.application
            
            if not application:
                logger.warning("Приложение не инициализировано")
                return
            
            from keyboards import Keyboards
            keyboards = Keyboards()
            
            user = db.get_user(user_id)
            if not user:
                return
            
            # Выбираем случайное мотивационное сообщение
            import random
            motivation = random.choice(MESSAGES['morning_motivation'])
            
            message_text = f"""
{motivation}

👋 Доброе утро, {user['first_name']}!

🌅 Сегодня День {user['current_day']} твоего курса!

💪 Готова начать день с тренировки?

🎯 Помни: каждый день приближает тебя к цели!
            """
            
            await application.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboards.training_menu(user['current_day'])
            )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'morning_motivation_sent')
            
            logger.info(f"Утреннее мотивационное сообщение отправлено пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки утреннего мотивационного сообщения: {e}")
    
    async def send_evening_motivation(self, user_id: int):
        """Отправка вечерней мотивации"""
        try:
            # Получаем глобальное приложение
            import main
            application = main.application
            
            if not application:
                logger.warning("Приложение не инициализировано")
                return
            
            user = db.get_user(user_id)
            if not user:
                return
            
            motivation_text = f"""
🌙 Добрый вечер, {user['first_name']}!

{MESSAGES['evening_motivation']}

💪 Ты молодец! Продолжай в том же духе!
            """
            
            await application.bot.send_message(
                chat_id=user_id,
                text=motivation_text,
                reply_markup=keyboards.main_menu()
            )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'evening_motivation_sent')
            
            logger.info(f"Вечерняя мотивация отправлена пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки вечерней мотивации: {e}")
    
    async def send_training_reminder(self, user_id: int):
        """Отправка напоминания о тренировке"""
        try:
            user = db.get_user(user_id)
            if not user:
                return
            
            # Проверяем, не выполнил ли пользователь уже тренировку
            if user['training_completed']:
                return
            
            await training_system.send_training_reminder(user_id, user['current_day'])
            
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания о тренировке: {e}")
    
    def schedule_daily_reset(self):
        """Планирование ежедневного сброса отметок"""
        try:
            # Сброс отметок в полночь по московскому времени
            self.scheduler.add_job(
                func=self.reset_daily_marks,
                trigger=CronTrigger(hour=0, minute=0, timezone='Europe/Moscow'),
                id='daily_reset',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info("Ежедневный сброс отметок запланирован")
            
        except Exception as e:
            logger.error(f"Ошибка планирования ежедневного сброса: {e}")
    
    async def reset_daily_marks(self):
        """Сброс ежедневных отметок всех пользователей"""
        try:
            users = db.get_all_users()
            reset_count = 0
            
            for user in users:
                if db.reset_daily_marks(user['user_id']):
                    reset_count += 1
            
            logger.info(f"Ежедневные отметки сброшены для {reset_count} пользователей")
            
        except Exception as e:
            logger.error(f"Ошибка сброса ежедневных отметок: {e}")
    
    def schedule_day_progression(self):
        """Планирование прогрессии дней курса"""
        try:
            # Проверка прогрессии дней в полночь
            self.scheduler.add_job(
                func=self.progress_user_days,
                trigger=CronTrigger(hour=0, minute=30, timezone='Europe/Moscow'),
                id='day_progression_midnight',
                replace_existing=True,
                max_instances=1
            )
            
            # Проверка прогрессии дней утром (8:00)
            self.scheduler.add_job(
                func=self.progress_user_days,
                trigger=CronTrigger(hour=8, minute=0, timezone='Europe/Moscow'),
                id='day_progression_morning',
                replace_existing=True,
                max_instances=1
            )
            
            # Ежедневный сброс чек-листа в полночь
            self.scheduler.add_job(
                func=self.reset_daily_checklist,
                trigger=CronTrigger(hour=0, minute=0, timezone='Europe/Moscow'),
                id='daily_checklist_reset',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info("Прогрессия дней курса запланирована")
            
        except Exception as e:
            logger.error(f"Ошибка планирования прогрессии дней: {e}")
    
    async def progress_user_days(self):
        """Прогрессия дней курса для пользователей"""
        try:
            users = db.get_all_users()
            progressed_count = 0
            
            for user in users:
                # Проверяем, нужно ли перевести пользователя на следующий день
                if self.should_progress_day(user):
                    new_day = min(user['current_day'] + 1, 3)  # Максимум 3 дня для базового курса
                    
                    # Определяем причину перехода
                    last_activity = datetime.fromisoformat(user['last_activity'])
                    hours_since_activity = (datetime.now() - last_activity).total_seconds() / 3600
                    
                    current_hour = datetime.now().hour
                    is_morning = 8 <= current_hour <= 12
                    
                    if hours_since_activity >= 24 and user.get('training_completed', False):
                        reason = "completed"
                    elif is_morning and hours_since_activity >= 8 and user.get('training_completed', False):
                        reason = "morning"
                    else:
                        reason = "unknown"
                    
                    # Обновляем день и сбрасываем тренировку
                    db.update_user(
                        user['user_id'], 
                        current_day=new_day,
                        training_completed=False
                    )
                    progressed_count += 1
                    
                    # Отправляем уведомление о новом дне
                    await self.send_new_day_notification(user['user_id'], new_day, reason)
            
            logger.info(f"Прогрессия дней выполнена для {progressed_count} пользователей")
            
        except Exception as e:
            logger.error(f"Ошибка прогрессии дней: {e}")
    
    def should_progress_day(self, user: dict) -> bool:
        """Проверка, нужно ли перевести пользователя на следующий день"""
        # Переводим на следующий день, если:
        # 1. Это не последний день базового курса
        # 2. И выполняется одно из условий:
        #    - Прошло более 24 часов с последней активности И тренировка выполнена
        #    - Наступило утро следующего дня (8:00) И тренировка выполнена
        
        if user['current_day'] >= 3:
            return False
        
        last_activity = datetime.fromisoformat(user['last_activity'])
        hours_since_activity = (datetime.now() - last_activity).total_seconds() / 3600
        
        # Проверяем, что тренировка выполнена
        training_completed = user.get('training_completed', False)
        
        # Условие 1: Прошло 24+ часов И тренировка выполнена
        condition_1 = hours_since_activity >= 24 and training_completed
        
        # Условие 2: Наступило утро следующего дня (8:00)
        # Проверяем, что сейчас утро (8:00-12:00), с последней активности прошло больше 8 часов
        # И тренировка предыдущего дня выполнена
        current_hour = datetime.now().hour
        is_morning = 8 <= current_hour <= 12
        condition_2 = is_morning and hours_since_activity >= 8 and training_completed
        
        return condition_1 or condition_2
    
    async def send_new_day_notification(self, user_id: int, new_day: int, reason: str = "completed"):
        """Отправка уведомления о новом дне и автоматическая отправка тренировки"""
        try:
            # Получаем глобальное приложение
            import main
            application = main.application
            
            if not application:
                logger.warning("Приложение не инициализировано")
                return
            
            from keyboards import Keyboards
            keyboards = Keyboards()
            from training import send_training_content
            
            user = db.get_user(user_id)
            if not user:
                return
            
            # Формируем уведомление в зависимости от причины перехода
            if reason == "completed":
                notification_text = f"""
🎉 Поздравляю, {user['first_name']}!

📅 Сегодня начинается День {new_day} твоего курса!

🏋️‍♀️ Ты отлично справился(ась) с предыдущим днем!

💪 Твоя новая тренировка уже готова!
                """
            else:  # reason == "morning"
                notification_text = f"""
🌅 Доброе утро, {user['first_name']}!

📅 Сегодня начинается День {new_day} твоего курса!

🏋️‍♀️ Время для новой тренировки!

💪 Начнем день с пользой для здоровья!
                """
            
            await application.bot.send_message(
                chat_id=user_id,
                text=notification_text,
                reply_markup=keyboards.main_menu()
            )
            
            # Автоматически отправляем тренировку нового дня
            await self.send_automatic_training(user_id, new_day)
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'new_day_notification', f'day_{new_day}_reason_{reason}')
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о новом дне: {e}")
    
    async def send_automatic_training(self, user_id: int, day: int):
        """Автоматическая отправка тренировки нового дня"""
        try:
            import main
            application = main.application
            
            if not application:
                return
            
            from training import TrainingSystem
            from keyboards import Keyboards
            keyboards = Keyboards()
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            training_manager = TrainingSystem()
            
            # Получаем контент тренировки
            content = training_manager.training_content.get(day)
            if not content:
                logger.error(f"Контент тренировки дня {day} не найден")
                return
            
            # Формируем сообщение с тренировкой
            message_text = f"""
🏋️‍♀️ <b>День {day} - {content['title']}</b>

{content['description']}

{content['content']}

{content['motivation']}
            """
            
            # Добавляем упражнения
            for exercise_group in content['exercises']:
                message_text += f"\n\n<b>{exercise_group['name']}</b>\n{exercise_group['description']}\n"
                for exercise in exercise_group['exercises']:
                    message_text += f"• {exercise}\n"
            
            # Добавляем советы
            if content['tips']:
                message_text += "\n\n💡 <b>Советы:</b>\n"
                for tip in content['tips']:
                    message_text += f"{tip}\n"
            
            # Создаем клавиатуру
            keyboard = [
                [InlineKeyboardButton("✅ Тренировка выполнена", callback_data='mark_training')],
                [InlineKeyboardButton("🔙 В меню", callback_data='main_menu')]
            ]
            
            if day == 3:
                keyboard.insert(1, [InlineKeyboardButton("💎 Полный курс", callback_data='full_course')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем тренировку
            if content['image']:
                # Используем новую функцию для отправки изображения с текстом
                from utils import send_image_with_text
                await send_image_with_text(
                    bot=application.bot,
                    chat_id=user_id,
                    image_path=content['image'],
                    text=message_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await application.bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'training_auto_sent', f'day_{day}')
            
            logger.info(f"Автоматическая тренировка дня {day} отправлена пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка автоматической отправки тренировки: {e}")
    
    def schedule_analytics_cleanup(self):
        """Планирование очистки старых данных аналитики"""
        try:
            # Очистка старых данных аналитики каждую неделю
            self.scheduler.add_job(
                func=self.cleanup_old_analytics,
                trigger=CronTrigger(day_of_week=0, hour=2, minute=0, timezone='Europe/Moscow'),
                id='analytics_cleanup',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info("Очистка аналитики запланирована")
            
        except Exception as e:
            logger.error(f"Ошибка планирования очистки аналитики: {e}")
    
    async def cleanup_old_analytics(self):
        """Очистка старых данных аналитики"""
        try:
            # Удаляем события старше 90 дней
            cutoff_date = datetime.now() - timedelta(days=90)
            
            with db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM analytics WHERE timestamp < ?',
                    (cutoff_date,)
                )
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"Удалено {deleted_count} старых записей аналитики")
            
        except Exception as e:
            logger.error(f"Ошибка очистки аналитики: {e}")
    
    def schedule_backup(self):
        """Планирование резервного копирования базы данных"""
        try:
            # Резервное копирование каждый день в 3:00
            self.scheduler.add_job(
                func=self.backup_database,
                trigger=CronTrigger(hour=3, minute=0, timezone='Europe/Moscow'),
                id='database_backup',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info("Резервное копирование базы данных запланировано")
            
        except Exception as e:
            logger.error(f"Ошибка планирования резервного копирования: {e}")
    
    async def backup_database(self):
        """Резервное копирование базы данных"""
        try:
            import shutil
            from datetime import datetime
            
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db.db_path, backup_filename)
            
            logger.info(f"Резервная копия создана: {backup_filename}")
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
    
    def start_all_scheduled_jobs(self):
        """Запуск всех запланированных задач"""
        try:
            # Запускаем планировщик, если еще не запущен
            if not self._started:
                self.scheduler.start()
                self._started = True
                logger.info("Планировщик задач запущен")
            
            # Планируем системные задачи
            self.schedule_daily_reset()
            self.schedule_day_progression()
            self.schedule_analytics_cleanup()
            self.schedule_backup()
            
            # Восстанавливаем задачи пользователей из базы данных
            self.restore_user_jobs()
            
            logger.info("Все запланированные задачи запущены")
            
        except Exception as e:
            logger.error(f"Ошибка запуска запланированных задач: {e}")
    
    def restore_user_jobs(self):
        """Восстановление задач пользователей из базы данных"""
        try:
            jobs = db.get_scheduled_jobs()
            
            for job in jobs:
                user_id = job['user_id']
                user = db.get_user(user_id)
                
                if user:
                    self.schedule_user_jobs(user_id, user['timezone'])
            
            logger.info(f"Восстановлены задачи для {len(jobs)} пользователей")
            
        except Exception as e:
            logger.error(f"Ошибка восстановления задач пользователей: {e}")
    
    def shutdown(self):
        """Остановка планировщика"""
        try:
            if self._started:
                self.scheduler.shutdown()
                self._started = False
                logger.info("Планировщик остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки планировщика: {e}")
    
    def get_job_status(self, user_id: int) -> dict:
        """Получение статуса задач пользователя"""
        try:
            if user_id not in self.job_ids:
                return {'status': 'no_jobs'}
            
            status = {}
            for job_type, job_id in self.job_ids[user_id].items():
                try:
                    job = self.scheduler.get_job(job_id)
                    status[job_type] = {
                        'exists': job is not None,
                        'next_run': job.next_run_time.isoformat() if job and job.next_run_time else None
                    }
                except Exception as e:
                    status[job_type] = {'exists': False, 'error': str(e)}
            
            return status
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса задач: {e}")
            return {'error': str(e)}

# Глобальный экземпляр планировщика
scheduler = JobScheduler()
