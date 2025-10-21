"""
🛠 Админ-панель для бота DianaLisa
Управление пользователями, статистикой, рассылками и настройками
"""

import logging
import csv
import io
import asyncio
import os
import sys
import subprocess
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import ADMIN_IDS, MESSAGES
from keyboards import Keyboards
from database import db
from payment import payment_system
# from validation import input_validator, error_handler, ValidationError  # Модуль не существует

logger = logging.getLogger(__name__)

# Создаем экземпляр клавиатур
keyboards = Keyboards()

class AdminPanel:
    """Класс для управления админ-панелью"""
    
    def __init__(self):
        self.admin_ids = ADMIN_IDS
        self.broadcast_queue = []  # Очередь рассылки
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь админом"""
        return user_id in self.admin_ids
    
    async def handle_admin_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Обработка админских действий"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            # Проверяем права админа
            if not self.is_admin(user_id):
                await query.edit_message_text(
                    "❌ У вас нет прав доступа к админ-панели.",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            # Обрабатываем различные админские действия
            if callback_data == 'admin_stats':
                await self.show_statistics(query)
            elif callback_data == 'admin_send_message':
                await self.start_broadcast(query)
            elif callback_data == 'admin_export_db':
                await self.export_database(query)
            elif callback_data == 'admin_analytics':
                await self.show_simple_analytics(query)
            elif callback_data == 'admin_users':
                await self.show_users(query)
            elif callback_data == 'admin_payments':
                await self.show_payments(query)
            elif callback_data == 'admin_reviews':
                await self.show_reviews(query)
            elif callback_data == 'admin_clear_db':
                await self.show_clear_db_confirmation(query)
            elif callback_data == 'confirm_clear_db':
                await self.clear_database(query)
            elif callback_data.startswith('admin_user_'):
                await self.handle_user_action(query, callback_data)
            elif callback_data.startswith('admin_message_'):
                await self.start_user_message(query, callback_data)
            else:
                await query.edit_message_text(
                    "❓ Неизвестное админское действие.",
                    reply_markup=keyboards.admin_menu()
                )
            
        except Exception as e:
            logger.error(f"Ошибка обработки админского действия: {e}")
            await query.edit_message_text(
                "❌ Произошла ошибка при выполнении действия.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def show_statistics(self, query):
        """Показ общей статистики"""
        try:
            # Получаем статистику
            users_count = db.get_users_count()
            premium_users = len([u for u in db.get_all_users() if u['is_premium']])
            
            # Безопасное получение статистики платежей
            try:
                payment_stats = payment_system.get_payment_statistics()
                total_payments = payment_stats.get('total', {}).get('payments', 0)
                total_amount = payment_stats.get('total', {}).get('amount', 0)
                avg_amount = payment_stats.get('total', {}).get('average', 0)
            except Exception as e:
                logger.error(f"Ошибка получения статистики платежей: {e}")
                total_payments = 0
                total_amount = 0
                avg_amount = 0
            
            # Статистика по дням курса
            users_by_day = {}
            for user in db.get_all_users():
                day = user['current_day']
                users_by_day[day] = users_by_day.get(day, 0) + 1
            
            stats_text = f"""
📊 СТАТИСТИКА БОТА

👥 Пользователи:
• Всего: {users_count}
• Премиум: {premium_users}
• Обычные: {users_count - premium_users}

💰 Платежи:
• Всего: {total_payments}
• Сумма: {total_amount:.2f} ₽
• Средний чек: {avg_amount:.2f} ₽

📅 Прогресс по дням:
• День 1: {users_by_day.get(1, 0)}
• День 2: {users_by_day.get(2, 0)}
• День 3: {users_by_day.get(3, 0)}

🕒 Последнее обновление: {datetime.now().strftime('%H:%M:%S')}
            """
            
            await query.edit_message_text(
                stats_text,
                reply_markup=keyboards.admin_menu(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа статистики: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения статистики.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def show_simple_analytics(self, query):
        """Показ упрощенной аналитики"""
        try:
            # Получаем базовую статистику
            users_count = db.get_users_count()
            premium_users = len([u for u in db.get_all_users() if u['is_premium']])
            
            analytics_text = f"""
📊 <b>АНАЛИТИКА</b>

👥 <b>Пользователи:</b>
• Всего: {users_count}
• Премиум: {premium_users}
• Обычные: {users_count - premium_users}

📈 <b>Конверсия:</b>
• В премиум: {(premium_users / max(users_count, 1)) * 100:.1f}%

💡 <b>Рекомендации:</b>
• Фокус на конверсии в премиум
• Улучшение удержания пользователей
            """
            
            await query.edit_message_text(
                analytics_text,
                reply_markup=keyboards.admin_menu(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа аналитики: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения аналитики.",
                reply_markup=keyboards.admin_menu()
            )
    
    
    
    
    
    
    async def show_users(self, query):
        """Показ списка пользователей"""
        try:
            users = db.get_all_users()[:10]  # Показываем первых 10
            
            users_text = "👥 ПОЛЬЗОВАТЕЛИ (последние 10)\n\n"
            
            for user in users:
                status = "💎 Премиум" if user['is_premium'] else "👤 Обычный"
                phone = user.get('phone', 'Не указан')
                users_text += f"• {user['first_name']} (@{user['username']}) - {status}\n"
                users_text += f"  📱 Телефон: {phone}\n"
                users_text += f"  День: {user['current_day']}, Регистрация: {user['registration_date'][:10]}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data='admin_menu')]
            ]
            
            await query.edit_message_text(
                users_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа пользователей: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения списка пользователей.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def show_payments(self, query):
        """Показ статистики платежей"""
        try:
            payment_stats = payment_system.get_payment_statistics()
            
            payments_text = f"""
💰 СТАТИСТИКА ПЛАТЕЖЕЙ

📊 Общая статистика:
• Всего платежей: {payment_stats['total']['payments']}
• Общая сумма: {payment_stats['total']['amount']:.2f} ₽
• Средний чек: {payment_stats['total']['average']:.2f} ₽

📈 По типам:
            """
            
            for stat in payment_stats['by_type']:
                payments_text += f"• {stat['type']}: {stat['count']} ({stat['amount']:.2f} ₽)\n"
            
            payments_text += "\n📅 За последние дни:\n"
            for stat in payment_stats['daily'][:5]:
                payments_text += f"• {stat['date']}: {stat['count']} ({stat['amount']:.2f} ₽)\n"
            
            await query.edit_message_text(
                payments_text,
                reply_markup=keyboards.admin_menu(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа платежей: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения статистики платежей.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def show_reviews(self, query):
        """Показ отзывов"""
        try:
            reviews = db.get_reviews(approved_only=False)[:5]  # Показываем последние 5
            
            reviews_text = "⭐ ОТЗЫВЫ (последние 5)\n\n"
            
            if not reviews:
                reviews_text += "📝 Отзывов пока нет"
            else:
                for review in reviews:
                    status = "✅ Одобрен" if review['is_approved'] else "⏳ На модерации"
                    reviews_text += f"• {review['first_name']} - {review['rating']}/5 ⭐\n"
                    reviews_text += f"  {review['review_text'][:100]}...\n"
                    reviews_text += f"  {status} - {review['created_at'][:10]}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("✅ Одобрить все", callback_data='admin_approve_reviews')],
                [InlineKeyboardButton("🔙 Назад", callback_data='admin_menu')]
            ]
            
            await query.edit_message_text(
                reviews_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа отзывов: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения отзывов.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def show_training_feedback(self, query):
        """Показ отзывов о тренировках"""
        try:
            feedback = db.get_all_training_feedback()[:10]  # Показываем последние 10
            
            feedback_text = "💪 ОТЗЫВЫ О ТРЕНИРОВКАХ (последние 10)\n\n"
            
            if not feedback:
                feedback_text += "📝 Отзывов пока нет"
            else:
                for fb in feedback:
                    name = fb.get('first_name', 'Неизвестно')
                    day = fb.get('day', '?')
                    difficulty = fb.get('difficulty_rating', 0)
                    clarity = fb.get('clarity_rating', 0)
                    comments = fb.get('comments', '')
                    timestamp = fb.get('timestamp', '')[:10]
                    
                    # Определяем тип отзыва
                    if difficulty >= 4 and clarity >= 4:
                        emoji = "😊"
                        type_text = "Понравилось"
                    elif difficulty <= 2 and clarity <= 2:
                        emoji = "😞"
                        type_text = "Не понравилось"
                    else:
                        emoji = "😐"
                        type_text = "Нейтрально"
                    
                    feedback_text += f"{emoji} <b>{name}</b> - День {day}\n"
                    feedback_text += f"   Сложность: {difficulty}/5 | Понятность: {clarity}/5\n"
                    feedback_text += f"   Тип: {type_text}\n"
                    if comments:
                        feedback_text += f"   Комментарий: {comments[:50]}...\n"
                    feedback_text += f"   Дата: {timestamp}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data='admin_menu')]
            ]
            
            # Используем delete_message + send_message вместо edit_message_text
            try:
                await query.delete_message()
            except:
                pass
            
            await query.get_bot().send_message(
                chat_id=query.message.chat_id,
                text=feedback_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа отзывов о тренировках: {e}")
            try:
                await query.delete_message()
            except:
                pass
            
            await query.get_bot().send_message(
                chat_id=query.message.chat_id,
                text="❌ Ошибка получения отзывов о тренировках.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def start_broadcast(self, query):
        """Начало рассылки"""
        try:
            broadcast_text = """
📨 РАССЫЛКА СООБЩЕНИЙ

Введите сообщение для рассылки всем пользователям:

💡 Поддерживается HTML разметка
📝 Максимум 4000 символов
⏰ Рассылка может занять время
            """
            
            await query.edit_message_text(
                broadcast_text,
                reply_markup=keyboards.back_to_main()
            )
            
            # Устанавливаем состояние ожидания сообщения для рассылки
            # context.user_data['waiting_for_broadcast'] = True  # Убрано - context не доступен
            
        except Exception as e:
            logger.error(f"Ошибка начала рассылки: {e}")
            await query.edit_message_text(
                "❌ Ошибка начала рассылки.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def process_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщения для рассылки с валидацией"""
        try:
            message_text = update.message.text
            
            # Простая валидация сообщения
            if not message_text or len(message_text.strip()) < 3:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Сообщение слишком короткое. Минимум 3 символа."
                )
                return
            
            if len(message_text) > 4000:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Сообщение слишком длинное. Максимум 4000 символов."
                )
                return
            
            # Подтверждение рассылки
            confirmation_text = f"""
📨 ПОДТВЕРЖДЕНИЕ РАССЫЛКИ

Сообщение:
{message_text}

📊 Будет отправлено: {db.get_users_count()} пользователям

Подтвердить рассылку?
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Да, отправить", callback_data='confirm_broadcast'),
                    InlineKeyboardButton("❌ Отмена", callback_data='cancel_broadcast')
                ]
            ]
            
            await update.message.reply_text(
                confirmation_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
            # Сохраняем сообщение для рассылки
            context.user_data['broadcast_message'] = message_text
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения рассылки: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def execute_broadcast(self, query, message_text: str):
        """Выполнение рассылки"""
        try:
            users = db.get_all_users()
            sent_count = 0
            failed_count = 0
            
            await query.edit_message_text(
                f"📤 Начинаем рассылку для {len(users)} пользователей...",
                reply_markup=keyboards.back_to_main()
            )
            
            for user in users:
                try:
                    await query.bot.send_message(
                        chat_id=user['user_id'],
                        text=message_text,
                        parse_mode=ParseMode.HTML
                    )
                    sent_count += 1
                    
                    # Небольшая задержка между сообщениями
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    failed_count += 1
                    logger.warning(f"Не удалось отправить сообщение пользователю {user['user_id']}: {e}")
            
            # Отчет о рассылке
            report_text = f"""
📊 ОТЧЕТ О РАССЫЛКЕ

✅ Отправлено: {sent_count}
❌ Не отправлено: {failed_count}
📊 Всего пользователей: {len(users)}

🕒 Завершено: {datetime.now().strftime('%H:%M:%S')}
            """
            
            await query.edit_message_text(
                report_text,
                reply_markup=keyboards.admin_menu(),
                parse_mode=ParseMode.HTML
            )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(query.from_user.id, 'broadcast_sent', f'sent_{sent_count}_failed_{failed_count}')
            
        except Exception as e:
            logger.error(f"Ошибка выполнения рассылки: {e}")
            await query.edit_message_text(
                "❌ Ошибка выполнения рассылки.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def export_database(self, query):
        """Экспорт базы данных"""
        try:
            # Создаем CSV файл с данными пользователей
            users = db.get_all_users()
            
            csv_data = io.StringIO()
            writer = csv.writer(csv_data)
            
            # Заголовки
            writer.writerow([
                'user_id', 'username', 'first_name', 'last_name', 'email',
                'timezone', 'current_day', 'registration_date', 'is_premium',
                'total_referrals', 'total_purchases'
            ])
            
            # Данные пользователей
            for user in users:
                writer.writerow([
                    user['user_id'], user['username'], user['first_name'],
                    user['last_name'], user['email'], user['timezone'],
                    user['current_day'], user['registration_date'],
                    user['is_premium'], user['total_referrals'],
                    user['total_purchases']
                ])
            
            # Отправляем файл
            csv_data.seek(0)
            await query.bot.send_document(
                chat_id=query.from_user.id,
                document=io.BytesIO(csv_data.getvalue().encode('utf-8')),
                filename=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption=f"📊 Экспорт пользователей ({len(users)} записей)"
            )
            
            await query.edit_message_text(
                f"✅ База данных экспортирована! Отправлено {len(users)} записей.",
                reply_markup=keyboards.admin_menu()
            )
            
        except Exception as e:
            logger.error(f"Ошибка экспорта базы данных: {e}")
            await query.edit_message_text(
                "❌ Ошибка экспорта базы данных.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def handle_user_action(self, query, callback_data: str):
        """Обработка действий с пользователем"""
        try:
            # Извлекаем ID пользователя из callback_data
            user_id = int(callback_data.split('_')[-1])
            user = db.get_user(user_id)
            
            if not user:
                await query.edit_message_text(
                    "❌ Пользователь не найден.",
                    reply_markup=keyboards.admin_menu()
                )
                return
            
            if 'stats' in callback_data:
                await self.show_user_stats(query, user)
            elif 'message' in callback_data:
                await self.start_user_message(query, user_id)
            elif 'payments' in callback_data:
                await self.show_user_payments(query, user_id)
            elif 'reviews' in callback_data:
                await self.show_user_reviews(query, user_id)
            
        except Exception as e:
            logger.error(f"Ошибка обработки действия с пользователем: {e}")
            await query.edit_message_text(
                "❌ Ошибка обработки действия.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def show_user_stats(self, query, user: dict):
        """Показ статистики пользователя"""
        try:
            stats = db.get_user_stats(user['user_id'])
            
            stats_text = f"""
👤 СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ

👋 Имя: {user['first_name']} {user['last_name'] or ''}
📧 Email: {user['email']}
🌍 Часовой пояс: {user['timezone']}
📅 День курса: {user['current_day']}
💎 Премиум: {'Да' if user['is_premium'] else 'Нет'}
📅 Регистрация: {user['registration_date'][:10]}

📊 Активность:
• Тренировки выполнено: {stats['events'].get('training_completed', 0)}
• Кнопки нажато: {stats['events'].get('button_click', 0)}
• Платежей: {stats['payments_count']}
• Потрачено: {stats['total_spent']:.2f} ₽
            """
            
            keyboard = [
                [InlineKeyboardButton("📨 Написать сообщение", callback_data=f'admin_message_{user["user_id"]}')],
                [InlineKeyboardButton("🔙 Назад", callback_data='admin_users')]
            ]
            
            await query.edit_message_text(
                stats_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа статистики пользователя: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения статистики пользователя.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def start_user_message(self, query, user_id: int):
        """Начало отправки сообщения пользователю"""
        try:
            user = db.get_user(user_id)
            
            message_text = f"""
📨 ОТПРАВКА СООБЩЕНИЯ

Получатель: {user['first_name']} (@{user['username']})

Введите сообщение для отправки:
            """
            
            await query.edit_message_text(
                message_text,
                reply_markup=keyboards.back_to_main()
            )
            
            # Устанавливаем состояние ожидания сообщения
            # context.user_data['waiting_for_user_message'] = user_id
            
        except Exception as e:
            logger.error(f"Ошибка начала отправки сообщения пользователю: {e}")
            await query.edit_message_text(
                "❌ Ошибка начала отправки сообщения.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def process_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Обработка сообщения для пользователя"""
        try:
            message_text = update.message.text
            
            # Отправляем сообщение пользователю
            await update.message.bot.send_message(
                chat_id=user_id,
                text=f"📨 Сообщение от поддержки:\n\n{message_text}",
                parse_mode=ParseMode.HTML
            )
            
            await update.message.reply_text(
                f"✅ Сообщение отправлено пользователю {user_id}",
                reply_markup=keyboards.admin_menu()
            )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(update.effective_user.id, 'admin_message_sent', str(user_id))
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю: {e}")
            await update.message.reply_text(
                "❌ Ошибка отправки сообщения.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def show_clear_db_confirmation(self, query):
        """Показ подтверждения очистки базы данных"""
        try:
            confirmation_text = """
⚠️ <b>ВНИМАНИЕ! ОЧИСТКА И ПЕРЕЗАПУСК БОТА</b>

🗑️ Это действие удалит ВСЕ данные:
• Всех пользователей
• Всю статистику
• Все платежи
• Все отзывы
• Всю аналитику

🔄 После очистки бот будет автоматически перезапущен

❌ <b>Это действие НЕОБРАТИМО!</b>

🤔 Вы уверены, что хотите продолжить?
            """
            
            keyboard = [
                [InlineKeyboardButton("✅ Да, очистить и перезапустить", callback_data='confirm_clear_db')],
                [InlineKeyboardButton("❌ Отмена", callback_data='admin_panel')]
            ]
            
            await query.edit_message_text(
                confirmation_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа подтверждения очистки БД: {e}")
            await query.edit_message_text(
                "❌ Ошибка показа подтверждения.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def clear_database(self, query):
        """Очистка базы данных"""
        try:
            logger.info("Начинаем очистку базы данных...")
            
            # Получаем список всех таблиц
            tables_to_clear = [
                'users', 'analytics', 'payments', 'reviews', 
                'training_feedback', 'analysis_requests', 'daily_stats', 'scheduled_jobs'
            ]
            
            cleared_count = 0
            
            # Используем правильный способ работы с базой данных
            import sqlite3
            from config import DATABASE_PATH
            
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                
                # Получаем список существующих таблиц
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables_to_clear:
                    if table in existing_tables:
                        try:
                            # Очищаем таблицу
                            cursor.execute(f"DELETE FROM {table}")
                            cleared_count += 1
                            logger.info(f"Очищена таблица: {table}")
                            
                        except Exception as table_error:
                            logger.error(f"Ошибка очистки таблицы {table}: {table_error}")
                    else:
                        logger.info(f"Таблица {table} не существует, пропускаем")
                
                # Сохраняем изменения
                conn.commit()
            
            success_text = f"""
✅ <b>База данных успешно очищена!</b>

🗑️ Очищено таблиц: {cleared_count}
📊 Все данные удалены

🔄 <b>Перезапускаем бота...</b>

⏳ Пожалуйста, подождите несколько секунд.
            """
            
            await query.edit_message_text(
                success_text,
                reply_markup=keyboards.admin_menu(),
                parse_mode=ParseMode.HTML
            )
            
            # Перезапускаем бота
            await self.restart_bot()
            
        except Exception as e:
            logger.error(f"Ошибка очистки базы данных: {e}")
            await query.edit_message_text(
                "❌ Ошибка очистки базы данных.",
                reply_markup=keyboards.admin_menu()
            )
    
    async def restart_bot(self):
        """Перезапуск бота"""
        try:
            logger.info("Начинаем перезапуск бота...")
            
            # Проверяем, запущен ли бот через менеджер
            import psutil
            current_process = psutil.Process()
            
            # Ищем процессы Python с main.py
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'main.py' in ' '.join(proc.info['cmdline']):
                        python_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if python_processes:
                logger.info(f"Найдено {len(python_processes)} процессов бота")
                
                # Завершаем все процессы бота
                for proc in python_processes:
                    try:
                        logger.info(f"Завершаем процесс {proc.pid}")
                        proc.terminate()
                        proc.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        try:
                            proc.kill()
                        except:
                            pass
                
                # Ждем завершения процессов
                await asyncio.sleep(3)
            
            # Запускаем новый процесс через менеджер, если он есть
            manager_path = "bot_manager.py"
            if os.path.exists(manager_path):
                logger.info("Запускаем бота через менеджер...")
                subprocess.Popen([
                    sys.executable, manager_path
                ], cwd=os.getcwd())
            else:
                # Запускаем напрямую
                logger.info("Запускаем бота напрямую...")
                subprocess.Popen([
                    sys.executable, "main.py"
                ], cwd=os.getcwd())
            
            logger.info("Новый процесс бота запущен")
            
            # Даем время новому процессу запуститься
            await asyncio.sleep(2)
            
            # Завершаем текущий процесс
            logger.info("Завершаем текущий процесс бота")
            os._exit(0)
            
        except Exception as e:
            logger.error(f"Ошибка перезапуска бота: {e}")
            # В случае ошибки просто завершаем процесс
            os._exit(1)

# Глобальный экземпляр админ-панели
admin_panel = AdminPanel()

# Функция для совместимости с callbacks.py
async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """Функция для обработки админских действий"""
    await admin_panel.handle_admin_actions(update, context, callback_data)
