"""
💳 Система оплаты для бота DianaLisa
Интеграция с Telegram Payments и обработка платежей
"""

import logging
import uuid
from datetime import datetime, timedelta
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import PAYMENT_PROVIDER_TOKEN, CURRENCY, MESSAGES
from keyboards import keyboards
from database import db

logger = logging.getLogger(__name__)

class PaymentSystem:
    """Класс для управления платежами"""
    
    def __init__(self):
        self.payment_provider_token = PAYMENT_PROVIDER_TOKEN
        self.currency = CURRENCY
        
        # Пакеты курсов
        self.course_packages = {
            'basic': {
                'name': '💎 Приобрести курс',
                'description': '28 дней персональных тренировок',
                'price': 1990,
                'features': [
                    '28 дней тренировок',
                    '12 тренировок (3 в неделю)',
                    'Программа питания',
                    'Ежедневная поддержка тренера',
                    'Отслеживание прогресса',
                    'Мотивация и советы 24/7',
                    'Доступ 40 дней'
                ]
            }
        }
        
        # Пакеты тренировок
        self.training_packages = {
            'single': {
                'name': '💻 1 тренировка',
                'description': 'Персональная тренировка с тренером',
                'price': 500,
                'features': [
                    '1 час персональной тренировки',
                    'Индивидуальный подход',
                    'Корректировка техники'
                ]
            },
            'pack5': {
                'name': '📅 5 тренировок',
                'description': 'Пакет из 5 персональных тренировок',
                'price': 2000,
                'features': [
                    '5 персональных тренировок',
                    'Скидка 20%',
                    'Гибкое расписание',
                    'Индивидуальный подход'
                ]
            },
            'pack10': {
                'name': '🏋️‍♀️ 10 тренировок',
                'description': 'Пакет из 10 персональных тренировок',
                'price': 3500,
                'features': [
                    '10 персональных тренировок',
                    'Скидка 30%',
                    'Гибкое расписание',
                    'Индивидуальный подход',
                    'Бонусные консультации'
                ]
            },
            'unlimited': {
                'name': '🔥 Безлимит на месяц',
                'description': 'Неограниченные тренировки на месяц',
                'price': 5000,
                'features': [
                    'Неограниченные тренировки',
                    'Групповые занятия',
                    'Персональные тренировки',
                    'Гибкое расписание',
                    'Все бонусы'
                ]
            }
        }
    
    async def create_payment_invoice(self, query, package_type: str, payment_type: str):
        """Создание инвойса для оплаты"""
        try:
            user_id = query.from_user.id
            
            # Получаем информацию о пакете
            if payment_type == 'course':
                package_info = self.course_packages.get(package_type)
            elif payment_type == 'training':
                package_info = self.training_packages.get(package_type)
            else:
                await query.edit_message_text(
                    "❌ Неверный тип платежа.",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            if not package_info:
                await query.edit_message_text(
                    "❌ Пакет не найден.",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            # Создаем уникальный ID транзакции
            transaction_id = f"{payment_type}_{package_type}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Формируем описание платежа
            description = f"{package_info['name']}\n\n{package_info['description']}\n\n"
            description += "Включает:\n"
            for feature in package_info['features']:
                description += f"• {feature}\n"
            
            # Создаем инвойс
            prices = [LabeledPrice(package_info['name'], package_info['price'] * 100)]  # Цена в копейках
            
            await query.bot.send_invoice(
                chat_id=user_id,
                title=package_info['name'],
                description=description,
                payload=transaction_id,
                provider_token=self.payment_provider_token,
                currency=self.currency,
                prices=prices,
                reply_markup=self.get_payment_keyboard(transaction_id)
            )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'payment_invoice_created', f"{payment_type}_{package_type}")
            
            logger.info(f"Инвойс создан для пользователя {user_id}: {transaction_id}")
            
        except Exception as e:
            logger.error(f"Ошибка создания инвойса: {e}")
            await query.edit_message_text(
                "❌ Произошла ошибка при создании платежа. Попробуйте позже.",
                reply_markup=keyboards.back_to_main()
            )
    
    def get_payment_keyboard(self, transaction_id: str) -> InlineKeyboardMarkup:
        """Создание клавиатуры для платежа"""
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить", pay=True)],
            [InlineKeyboardButton("❌ Отмена", callback_data='cancel_payment')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_pre_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка предварительной проверки платежа"""
        try:
            query = update.pre_checkout_query
            user_id = query.from_user.id
            
            # Проверяем валидность платежа
            if self.validate_payment(query.invoice_payload):
                await query.answer(ok=True)
                logger.info(f"Предварительная проверка платежа прошла успешно: {query.invoice_payload}")
            else:
                await query.answer(ok=False, error_message="Неверные данные платежа")
                logger.warning(f"Предварительная проверка платежа не прошла: {query.invoice_payload}")
            
        except Exception as e:
            logger.error(f"Ошибка предварительной проверки платежа: {e}")
            await query.answer(ok=False, error_message="Произошла ошибка при обработке платежа")
    
    async def handle_successful_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка успешного платежа"""
        try:
            message = update.message
            user_id = message.from_user.id
            payment = message.successful_payment
            
            # Извлекаем информацию о платеже
            transaction_id = payment.invoice_payload
            amount = payment.total_amount / 100  # Конвертируем из копеек
            currency = payment.currency
            
            # Определяем тип платежа и пакет
            payment_type, package_type = self.parse_transaction_id(transaction_id)
            
            # Сохраняем платеж в базу данных
            success = db.add_payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                payment_type=payment_type,
                status='completed',
                transaction_id=transaction_id
            )
            
            if success:
                # Активируем услуги для пользователя
                await self.activate_user_services(user_id, payment_type, package_type)
                
                # Отправляем подтверждение
                await self.send_payment_confirmation(message, payment_type, package_type)
                
                # Добавляем событие в аналитику
                db.add_analytics_event(user_id, 'payment_completed', f"{payment_type}_{package_type}")
                
                logger.info(f"Платеж успешно обработан: {transaction_id}")
            else:
                await message.reply_text(
                    "❌ Произошла ошибка при обработке платежа. Обратитесь в поддержку.",
                    reply_markup=keyboards.back_to_main()
                )
            
        except Exception as e:
            logger.error(f"Ошибка обработки успешного платежа: {e}")
            await message.reply_text(
                "❌ Произошла ошибка при обработке платежа. Обратитесь в поддержку.",
                reply_markup=keyboards.back_to_main()
            )
    
    def validate_payment(self, transaction_id: str) -> bool:
        """Валидация платежа"""
        try:
            # Проверяем формат transaction_id
            parts = transaction_id.split('_')
            if len(parts) != 4:
                return False
            
            payment_type, package_type, user_id, random_part = parts
            
            # Проверяем, что типы платежей валидны
            if payment_type not in ['course', 'training']:
                return False
            
            if payment_type == 'course' and package_type not in self.course_packages:
                return False
            
            if payment_type == 'training' and package_type not in self.training_packages:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации платежа: {e}")
            return False
    
    def parse_transaction_id(self, transaction_id: str) -> tuple:
        """Парсинг ID транзакции"""
        try:
            parts = transaction_id.split('_')
            payment_type = parts[0]
            package_type = parts[1]
            return payment_type, package_type
        except Exception as e:
            logger.error(f"Ошибка парсинга ID транзакции: {e}")
            return None, None
    
    async def activate_user_services(self, user_id: int, payment_type: str, package_type: str):
        """Активация услуг для пользователя"""
        try:
            user = db.get_user(user_id)
            if not user:
                return
            
            if payment_type == 'course':
                # Активируем премиум доступ
                premium_expires = datetime.now() + timedelta(days=30)
                db.update_user(user_id, 
                             is_premium=True, 
                             premium_expires=premium_expires)
                
                logger.info(f"Премиум доступ активирован для пользователя {user_id}")
                
            elif payment_type == 'training':
                # Добавляем тренировки к балансу пользователя
                training_count = self.get_training_count(package_type)
                # Здесь можно добавить логику для отслеживания количества тренировок
                
                logger.info(f"Тренировки активированы для пользователя {user_id}: {training_count}")
            
        except Exception as e:
            logger.error(f"Ошибка активации услуг: {e}")
    
    def get_training_count(self, package_type: str) -> int:
        """Получение количества тренировок в пакете"""
        training_counts = {
            'single': 1,
            'pack5': 5,
            'pack10': 10,
            'unlimited': -1  # Безлимит
        }
        return training_counts.get(package_type, 0)
    
    async def send_payment_confirmation(self, message, payment_type: str, package_type: str):
        """Отправка подтверждения платежа"""
        try:
            if payment_type == 'course':
                package_info = self.course_packages.get(package_type)
            else:
                package_info = self.training_packages.get(package_type)
            
            if not package_info:
                return
            
            confirmation_text = f"""
{MESSAGES['payment_success']}

📦 Активирован пакет: {package_info['name']}

✨ Что дальше:
• Материалы отправлены на твой email
• Доступ к закрытому чату активирован
• Поддержка 24/7 готова помочь

💪 Готова к новым достижениям?
            """
            
            await message.reply_text(
                confirmation_text,
                reply_markup=keyboards.main_menu(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка отправки подтверждения платежа: {e}")
    
    async def handle_payment_cancellation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка отмены платежа"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            await query.edit_message_text(
                "❌ Платеж отменен. Вы можете попробовать снова в любое время.",
                reply_markup=keyboards.main_menu()
            )
            
            # Добавляем событие в аналитику
            db.add_analytics_event(user_id, 'payment_cancelled')
            
        except Exception as e:
            logger.error(f"Ошибка обработки отмены платежа: {e}")
    
    def get_payment_statistics(self) -> dict:
        """Получение статистики платежей"""
        try:
            with db.connection() as conn:
                cursor = conn.cursor()
                
                # Общая статистика
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_payments,
                        SUM(amount) as total_amount,
                        AVG(amount) as average_amount
                    FROM payments 
                    WHERE status = 'completed'
                ''')
                total_stats = cursor.fetchone()
                
                # Статистика по типам
                cursor.execute('''
                    SELECT 
                        payment_type,
                        COUNT(*) as count,
                        SUM(amount) as total_amount
                    FROM payments 
                    WHERE status = 'completed'
                    GROUP BY payment_type
                ''')
                type_stats = cursor.fetchall()
                
                # Статистика по дням
                cursor.execute('''
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as count,
                        SUM(amount) as total_amount
                    FROM payments 
                    WHERE status = 'completed'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                    LIMIT 30
                ''')
                daily_stats = cursor.fetchall()
                
                return {
                    'total': {
                        'payments': total_stats[0] or 0,
                        'amount': total_stats[1] or 0,
                        'average': total_stats[2] or 0
                    },
                    'by_type': [
                        {'type': row[0], 'count': row[1], 'amount': row[2]}
                        for row in type_stats
                    ],
                    'daily': [
                        {'date': row[0], 'count': row[1], 'amount': row[2]}
                        for row in daily_stats
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики платежей: {e}")
            return {}
    
    async def process_refund(self, user_id: int, transaction_id: str, reason: str = None):
        """Обработка возврата средств"""
        try:
            # Здесь должна быть интеграция с платежной системой для возврата
            # Пока просто отмечаем в базе данных
            
            db.add_payment(
                user_id=user_id,
                amount=0,  # Возврат
                currency=CURRENCY,
                payment_type='refund',
                status='refunded',
                transaction_id=f"refund_{transaction_id}"
            )
            
            logger.info(f"Возврат обработан для транзакции {transaction_id}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки возврата: {e}")

# Глобальный экземпляр системы платежей
payment_system = PaymentSystem()

# Функция для совместимости с callbacks.py
async def create_payment_invoice(query, package_type: str, payment_type: str):
    """Функция для создания инвойса платежа"""
    await payment_system.create_payment_invoice(query, package_type, payment_type)
