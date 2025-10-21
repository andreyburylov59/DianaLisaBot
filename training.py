"""
🏋️‍♀️ Система тренировок для бота DianaLisa
Содержит контент для 3-дневного курса и управление тренировками
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import MESSAGES, IMAGES, BUTTONS
from keyboards import keyboards
from database import db
from utils import get_user_timezone

logger = logging.getLogger(__name__)

class TrainingSystem:
    """Класс для управления тренировками"""
    
    def __init__(self):
        self.training_content = {
            1: self.get_day1_content(),
            2: self.get_day2_content(),
            3: self.get_day3_content()
        }
    
    def get_day1_content(self) -> dict:
        """Контент для дня 1"""
        return {
            'title': '🏋️‍♀️ ДЕНЬ 1: Тренировка всего тела',
            'description': 'Начинаем с основ! Сегодня мы подготовим тело к тренировкам.',
            'image': 'DianaLisa2.jpg',
            'content': MESSAGES['training_day1'],
            'exercises': [
                {
                    'name': '🔥 Разминка (5 минут)',
                    'description': 'Подготовка тела к нагрузке',
                    'exercises': [
                        'Круговые движения руками - 30 сек',
                        'Наклоны головы - 30 сек',
                        'Вращения плечами - 30 сек',
                        'Легкие приседания - 30 сек',
                        'Махи ногами - 30 сек'
                    ]
                },
                {
                    'name': '💪 Основная тренировка (15 минут)',
                    'description': 'Базовые упражнения для укрепления мышц',
                    'exercises': [
                        'Приседания: 3 подхода по 10 раз',
                        'Отжимания от колен: 3 подхода по 8 раз',
                        'Планка: 3 подхода по 30 секунд',
                        'Выпады: 3 подхода по 8 раз на каждую ногу',
                        'Подъемы на носки: 3 подхода по 15 раз'
                    ]
                },
                {
                    'name': '🧘‍♀️ Заминка (5 минут)',
                    'description': 'Растяжка и расслабление',
                    'exercises': [
                        'Растяжка ног - 1 минута',
                        'Растяжка спины - 1 минута',
                        'Растяжка рук - 1 минута',
                        'Глубокое дыхание - 2 минуты'
                    ]
                }
            ],
            'tips': [
                '💡 Не торопись! Качество важнее скорости',
                '💧 Пей воду во время тренировки',
                '🫁 Дыши ровно и глубоко',
                '🎯 Сосредоточься на технике выполнения'
            ],
            'motivation': '🌟 Ты делаешь первый шаг к лучшей версии себя!'
        }
    
    def get_day2_content(self) -> dict:
        """Контент для дня 2"""
        return {
            'title': '🏋️‍♀️ ДЕНЬ 2: СИЛОВАЯ ТРЕНИРОВКА',
            'description': 'Увеличиваем интенсивность! Сегодня работаем над силой и выносливостью.',
            'image': 'DianaLisa3.jpg',
            'content': MESSAGES['training_day2'],
            'exercises': [
                {
                    'name': '🔥 Разминка (5 минут)',
                    'description': 'Активная подготовка к нагрузке',
                    'exercises': [
                        'Бег на месте - 1 минута',
                        'Махи руками - 1 минута',
                        'Наклоны в стороны - 1 минута',
                        'Приседания без веса - 1 минута',
                        'Прыжки на месте - 1 минута'
                    ]
                },
                {
                    'name': '💪 Основная тренировка (20 минут)',
                    'description': 'Силовые упражнения для укрепления мышц',
                    'exercises': [
                        'Приседания с прыжком: 3 подхода по 12 раз',
                        'Отжимания: 3 подхода по 10 раз',
                        'Планка с подъемом ног: 3 подхода по 45 секунд',
                        'Бурпи: 3 подхода по 8 раз',
                        'Приседания на одной ноге: 3 подхода по 6 раз',
                        'Отжимания с широкой постановкой: 3 подхода по 8 раз'
                    ]
                },
                {
                    'name': '🧘‍♀️ Заминка (5 минут)',
                    'description': 'Полная растяжка всего тела',
                    'exercises': [
                        'Растяжка всего тела - 3 минуты',
                        'Медитация - 2 минуты'
                    ]
                }
            ],
            'tips': [
                '💪 Слушай свое тело - не переусердствуй',
                '⏱️ Делай перерывы между подходами',
                '🎵 Включи мотивирующую музыку',
                '📱 Засекай время выполнения упражнений'
            ],
            'motivation': '🔥 Ты становишься сильнее с каждым упражнением!'
        }
    
    def get_day3_content(self) -> dict:
        """Контент для дня 3"""
        return {
            'title': '🏋️‍♀️ ДЕНЬ 3: ИНТЕНСИВНАЯ ТРЕНИРОВКА',
            'description': 'Финальный день! Максимальная интенсивность и результат.',
            'image': 'DianaLisa3.jpg',
            'content': MESSAGES['training_day3'],
            'exercises': [
                {
                    'name': '🔥 Разминка (7 минут)',
                    'description': 'Полная подготовка к интенсивной нагрузке',
                    'exercises': [
                        'Кардио разминка - 3 минуты',
                        'Динамическая растяжка - 2 минуты',
                        'Подготовка суставов - 2 минуты'
                    ]
                },
                {
                    'name': '💪 Основная тренировка (25 минут)',
                    'description': 'Интенсивная тренировка по методу Табата',
                    'exercises': [
                        'Табата приседания: 4 раунда по 20 сек',
                        'Табата отжимания: 4 раунда по 20 сек',
                        'Табата планка: 4 раунда по 20 сек',
                        'Табата выпады: 4 раунда по 20 сек',
                        'Бурпи с прыжком: 3 подхода по 10 раз',
                        'Планка с боковыми поворотами: 3 подхода по 45 сек'
                    ]
                },
                {
                    'name': '🧘‍♀️ Заминка (8 минут)',
                    'description': 'Полное восстановление и расслабление',
                    'exercises': [
                        'Полная растяжка - 4 минуты',
                        'Дыхательные упражнения - 2 минуты',
                        'Медитация - 2 минуты'
                    ]
                }
            ],
            'tips': [
                '🎯 Табата: 20 сек работы, 10 сек отдыха',
                '💨 Дыши через нос, выдыхай через рот',
                '🏆 Гордись собой - ты прошла 3 дня!',
                '🎉 Готовься к полному курсу!'
            ],
            'motivation': '🎉 Поздравляю! Ты прошла базовый курс!'
        }
    
    async def send_training_content(self, query, day: int, context):
        """Отправка контента тренировки"""
        try:
            user_id = query.from_user.id
            user = db.get_user(user_id)
            
            if not user:
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
            
            # Проверяем, может ли пользователь получить тренировку этого дня
            if not self.can_access_training(user, day):
                try:
                    await query.delete_message()
                except:
                    pass
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ У вас нет доступа к этой тренировке. Пройдите предыдущие дни.",
                    reply_markup=keyboards.main_menu()
                )
                return
            
            content = self.training_content.get(day)
            if not content:
                try:
                    await query.delete_message()
                except:
                    pass
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ Тренировка не найдена.",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            # Формируем сообщение
            message_text = f"""
{content['title']}

{content['content']}
            """
            
            # Создаем клавиатуру
            keyboard = [
                [InlineKeyboardButton("✅ Тренировка выполнена", callback_data=f'mark_training_{day}')],
                [InlineKeyboardButton("🔙 В меню", callback_data='main_menu')]
            ]
            
            if day == 3:
                keyboard.insert(1, [InlineKeyboardButton("💎 Полный курс", callback_data='full_course')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем сообщение
            if content['image']:
                # Удаляем предыдущее сообщение и отправляем новое с изображением
                try:
                    await query.delete_message()
                except:
                    pass  # Игнорируем ошибки удаления
                
                # Используем новую функцию для отправки изображения с текстом
                from utils import send_image_with_text
                await send_image_with_text(
                    bot=context.bot,
                    chat_id=user_id,
                    image_path=content['image'],
                    text=message_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                # Удаляем предыдущее сообщение и отправляем новое
                try:
                    await query.delete_message()
                except:
                    pass  # Игнорируем ошибки удаления
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'training_viewed', f'day_{day}')
            
            logger.info(f"Тренировка дня {day} отправлена пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки тренировки: {e}")
            try:
                await query.delete_message()
            except:
                pass
            
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при загрузке тренировки.",
                reply_markup=keyboards.back_to_main()
            )
    
    def can_access_training(self, user: dict, day: int) -> bool:
        """Проверка доступа к тренировке"""
        # Пользователь может получить тренировку, если:
        # 1. Это его текущий день или предыдущие дни
        # 2. Он премиум пользователь (доступ ко всем тренировкам)
        
        if user['is_premium']:
            return True
        
        return day <= user['current_day']
    
    async def complete_training(self, user_id: int, day: int):
        """Завершение тренировки"""
        try:
            user = db.get_user(user_id)
            if not user:
                return False
            
            # Отмечаем тренировку как выполненную
            db.mark_training_completed(user_id)
            
            # Если это последний день базового курса, предлагаем полный курс
            if day == 3 and not user['is_premium']:
                await self.offer_full_course(user_id)
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'training_completed', f'day_{day}')
            
            logger.info(f"Пользователь {user_id} завершил тренировку дня {day}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка завершения тренировки: {e}")
            return False
    
    async def offer_full_course(self, user_id: int):
        """Предложение полного курса после завершения базового"""
        try:
            # Получаем глобальное приложение
            import main
            application = main.application
            
            if not application:
                logger.warning("Приложение не инициализировано")
                return
            
            offer_text = """
🎉 Поздравляю! Ты завершила базовый курс!

💎 Готова к полному курсу DianaLisa?

✨ Что тебя ждет:
• 30 дней персональных тренировок
• План питания на месяц
• Поддержка 24/7
• Доступ к закрытому чату
• Бонусные материалы

🔥 Скидка 50% только сегодня!
            """
            
            await application.bot.send_message(
                chat_id=user_id,
                text=offer_text,
                reply_markup=keyboards.course_packages(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка отправки предложения полного курса: {e}")
    
    def get_training_progress(self, user_id: int) -> dict:
        """Получение прогресса тренировок пользователя"""
        try:
            user = db.get_user(user_id)
            if not user:
                return {}
            
            # Получаем статистику тренировок
            training_events = db.get_user_stats(user_id).get('events', {})
            
            return {
                'current_day': user['current_day'],
                'is_premium': user['is_premium'],
                'training_completed': user['training_completed'],
                'total_trainings': training_events.get('training_completed', 0),
                'days_completed': min(user['current_day'], 3),
                'progress_percentage': (min(user['current_day'], 3) / 3) * 100
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения прогресса тренировок: {e}")
            return {}
    
    async def send_training_reminder(self, user_id: int, day: int):
        """Отправка напоминания о тренировке"""
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
            
            reminder_text = f"""
⏰ Напоминание о тренировке!

👋 Привет, {user['first_name']}!

🏋️‍♀️ Время для тренировки Дня {day}!

💪 Ты можешь это сделать! Начни прямо сейчас!
            """
            
            await application.bot.send_message(
                chat_id=user_id,
                text=reminder_text,
                reply_markup=keyboards.training_menu(day),
                parse_mode=ParseMode.HTML
            )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'training_reminder_sent', f'day_{day}')
            
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания о тренировке: {e}")

# Глобальный экземпляр системы тренировок
training_system = TrainingSystem()

# Функция для совместимости с callbacks.py
async def send_training_content(query, day: int, context):
    """Функция для отправки контента тренировки"""
    await training_system.send_training_content(query, day, context)
