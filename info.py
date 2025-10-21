"""
ℹ️ Информационные функции для бота DianaLisa
FAQ, информация о курсах, поддержка и другие справочные материалы
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import MESSAGES, BUTTONS
from keyboards import Keyboards
keyboards = Keyboards()
from database import db

logger = logging.getLogger(__name__)

class InfoSystem:
    """Класс для управления информационными функциями"""
    
    def __init__(self):
        self.faq_data = self.load_faq_data()
        self.course_info = self.load_course_info()
        self.support_info = self.load_support_info()
    
    def load_faq_data(self) -> dict:
        """Загрузка данных FAQ"""
        return {
            'general': {
                'title': '❓ ОБЩИЕ ВОПРОСЫ',
                'questions': [
                    {
                        'question': 'Как часто нужно тренироваться?',
                        'answer': 'Для начинающих достаточно 3-4 раза в неделю. Главное - регулярность, а не интенсивность.'
                    },
                    {
                        'question': 'Что делать, если пропустил день?',
                        'answer': 'Не переживай! Просто продолжи с того места, где остановился. Главное - не бросать.'
                    },
                    {
                        'question': 'Нужно ли специальное оборудование?',
                        'answer': 'Нет! Все тренировки рассчитаны на выполнение дома без специального оборудования.'
                    },
                    {
                        'question': 'Как долго длится курс?',
                        'answer': 'Базовый курс - 3 дня, полный курс - 30 дней. Можно заниматься в своем темпе.'
                    }
                ]
            },
            'training': {
                'title': '🏋️‍♀️ ВОПРОСЫ О ТРЕНИРОВКАХ',
                'questions': [
                    {
                        'question': 'Что делать, если упражнение слишком сложное?',
                        'answer': 'Упрости упражнение или делай меньше повторений. Лучше сделать меньше, но правильно.'
                    },
                    {
                        'question': 'Можно ли заниматься во время месячных?',
                        'answer': 'Да, но слушай свое тело. Если чувствуешь слабость, сделай легкую тренировку.'
                    },
                    {
                        'question': 'Как понять, что тренировка эффективна?',
                        'answer': 'Если после тренировки чувствуешь легкую усталость и удовлетворение - это нормально.'
                    },
                    {
                        'question': 'Что делать, если болят мышцы?',
                        'answer': 'Это нормально! Делай растяжку, принимай теплый душ, пей больше воды.'
                    }
                ]
            },
            'technical': {
                'title': '🔧 ТЕХНИЧЕСКИЕ ВОПРОСЫ',
                'questions': [
                    {
                        'question': 'Не приходят напоминания',
                        'answer': 'Проверь, что уведомления включены в настройках Telegram. Также проверь часовой пояс.'
                    },
                    {
                        'question': 'Как изменить часовой пояс?',
                        'answer': 'Напиши /start и пройди регистрацию заново, выбрав нужный часовой пояс.'
                    },
                    {
                        'question': 'Не работает оплата',
                        'answer': 'Убедись, что у тебя установлена последняя версия Telegram. Попробуй другой способ оплаты.'
                    },
                    {
                        'question': 'Как связаться с поддержкой?',
                        'answer': 'Напиши @DianaLisaSupport или используй кнопку "Поддержка" в меню.'
                    }
                ]
            }
        }
    
    def load_course_info(self) -> dict:
        """Загрузка информации о курсах"""
        return {
            'basic_course': {
                'title': '💎 БАЗОВЫЙ КУРС',
                'duration': '30 дней',
                'price': '990 ₽',
                'description': 'Идеальный старт для новичков',
                'features': [
                    '30 дней персональных тренировок',
                    'План питания на месяц',
                    'Поддержка в чате',
                    'Доступ к материалам',
                    'Мотивационные сообщения',
                    'Отслеживание прогресса'
                ],
                'target': 'Для тех, кто только начинает свой путь к здоровому образу жизни'
            },
            'premium_course': {
                'title': '🔥 ПРЕМИУМ КУРС',
                'duration': '30 дней',
                'price': '1990 ₽',
                'description': 'Максимальный результат с персональным тренером',
                'features': [
                    '30 дней персональных тренировок',
                    'Персональный тренер',
                    'Индивидуальный план тренировок',
                    'Видео-консультации',
                    'Поддержка 24/7',
                    'План питания',
                    'Доступ к закрытому чату',
                    'Бонусные материалы'
                ],
                'target': 'Для тех, кто хочет максимальный результат с персональным подходом'
            },
            'vip_course': {
                'title': '👑 VIP КУРС',
                'duration': '30 дней',
                'price': '2990 ₽',
                'description': 'Полный пакет с гарантией результата',
                'features': [
                    '30 дней персональных тренировок',
                    'Персональный тренер',
                    'Индивидуальный план тренировок',
                    'Видео-консультации',
                    'Поддержка 24/7',
                    'Персональный план питания',
                    'Доступ к закрытому чату',
                    'Бонусные материалы',
                    'Гарантия результата',
                    'Персональные рекомендации',
                    'Анализ прогресса'
                ],
                'target': 'Для тех, кто готов инвестировать в себя и получить максимальный результат'
            }
        }
    
    def load_support_info(self) -> dict:
        """Загрузка информации о поддержке"""
        return {
            'contact_methods': [
                {
                    'name': 'Telegram',
                    'value': '@DianaLisaSupport',
                    'description': 'Быстрые ответы в чате'
                },
                {
                    'name': 'Email',
                    'value': 'support@dianalisa.com',
                    'description': 'Подробные консультации'
                },
                {
                    'name': 'Телефон',
                    'value': '+7 (999) 123-45-67',
                    'description': 'Экстренная поддержка'
                }
            ],
            'working_hours': '9:00 - 21:00 (МСК)',
            'response_time': 'Обычно отвечаем в течение 1 часа',
            'common_issues': [
                'Проблемы с оплатой',
                'Технические неполадки',
                'Вопросы по тренировкам',
                'Проблемы с доступом к материалам'
            ]
        }
    
    async def show_faq(self, query, category: str = 'general'):
        """Показ FAQ по категории"""
        try:
            if category not in self.faq_data:
                category = 'general'
            
            faq = self.faq_data[category]
            
            faq_text = f"{faq['title']}\n\n"
            
            for i, qa in enumerate(faq['questions'], 1):
                faq_text += f"{i}. ❓ {qa['question']}\n"
                faq_text += f"💡 {qa['answer']}\n\n"
            
            # Создаем клавиатуру для переключения категорий
            keyboard = [
                [
                    InlineKeyboardButton("❓ Общие", callback_data='faq_general'),
                    InlineKeyboardButton("🏋️‍♀️ Тренировки", callback_data='faq_training')
                ],
                [
                    InlineKeyboardButton("🔧 Технические", callback_data='faq_technical')
                ],
                [InlineKeyboardButton("🔙 В меню", callback_data='main_menu')]
            ]
            
            await query.edit_message_text(
                faq_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа FAQ: {e}")
            await query.edit_message_text(
                "❌ Ошибка загрузки FAQ.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def show_course_info(self, query, course_type: str):
        """Показ информации о курсе"""
        try:
            if course_type not in self.course_info:
                await query.edit_message_text(
                    "❌ Информация о курсе не найдена.",
                    reply_markup=keyboards.back_to_main()
                )
                return
            
            course = self.course_info[course_type]
            
            course_text = f"""
{course['title']}

💰 Цена: {course['price']}
⏱️ Длительность: {course['duration']}

📝 Описание:
{course['description']}

🎯 Для кого:
{course['target']}

✨ Что входит:
            """
            
            for feature in course['features']:
                course_text += f"• {feature}\n"
            
            keyboard = [
                [InlineKeyboardButton("💳 Купить курс", callback_data=f'buy_{course_type}')],
                [InlineKeyboardButton("🔙 Назад", callback_data='full_course')]
            ]
            
            await query.edit_message_text(
                course_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа информации о курсе: {e}")
            await query.edit_message_text(
                "❌ Ошибка загрузки информации о курсе.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def show_support_info(self, query):
        """Показ информации о поддержке"""
        try:
            support_text = f"""
📞 ПОДДЕРЖКА

⏰ Время работы: {self.support_info['working_hours']}
⚡ Время ответа: {self.support_info['response_time']}

📱 Способы связи:
            """
            
            for method in self.support_info['contact_methods']:
                support_text += f"• {method['name']}: {method['value']}\n"
                support_text += f"  {method['description']}\n\n"
            
            support_text += "🔧 Частые проблемы:\n"
            for issue in self.support_info['common_issues']:
                support_text += f"• {issue}\n"
            
            keyboard = [
                [InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me/DianaLisaSupport")],
                [InlineKeyboardButton("📧 Email", url="mailto:support@dianalisa.com")],
                [InlineKeyboardButton("🔙 В меню", callback_data='main_menu')]
            ]
            
            await query.edit_message_text(
                support_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа информации о поддержке: {e}")
            await query.edit_message_text(
                "❌ Ошибка загрузки информации о поддержке.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def show_about(self, query):
        """Показ информации о боте"""
        try:
            about_text = """
🤖 О БОТЕ DIANALISA

👋 Привет! Я DianaLisa - твой персональный фитнес-тренер в Telegram!

🎯 Моя цель - помочь тебе:
• Начать заниматься спортом
• Сформировать здоровые привычки
• Достичь своих целей
• Полюбить активный образ жизни

✨ Что я умею:
• Персональные тренировки
• Мотивация и поддержка
• Отслеживание прогресса
• Советы по питанию
• Напоминания о тренировках

💪 Начни свой путь к здоровой жизни прямо сейчас!

📅 Версия: 1.0.0
🕒 Обновлено: 2024
            """
            
            await query.edit_message_text(
                about_text,
                reply_markup=keyboards.back_to_main(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа информации о боте: {e}")
            await query.edit_message_text(
                "❌ Ошибка загрузки информации о боте.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def show_privacy_policy(self, query):
        """Показ политики конфиденциальности"""
        try:
            privacy_text = """
🔒 ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ

📋 Мы собираем и используем:
• Имя и контактные данные для персонализации
• Данные о тренировках для отслеживания прогресса
• Статистику использования для улучшения сервиса

🛡️ Мы защищаем:
• Все персональные данные
• Информацию о платежах
• Историю тренировок

❌ Мы НЕ передаем данные третьим лицам

✅ Ты можешь:
• Удалить свои данные
• Отозвать согласие
• Получить копию данных

📧 По вопросам: privacy@dianalisa.com
            """
            
            await query.edit_message_text(
                privacy_text,
                reply_markup=keyboards.back_to_main(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа политики конфиденциальности: {e}")
            await query.edit_message_text(
                "❌ Ошибка загрузки политики конфиденциальности.",
                reply_markup=keyboards.back_to_main()
            )
    
    async def show_terms_of_service(self, query):
        """Показ условий использования"""
        try:
            terms_text = """
📜 УСЛОВИЯ ИСПОЛЬЗОВАНИЯ

✅ Используя бота, ты соглашаешься:
• Следовать рекомендациям тренера
• Не распространять материалы
• Уважать других пользователей

🚫 Запрещено:
• Спамить или флудить
• Нарушать авторские права
• Использовать бота в коммерческих целях

⚖️ Ответственность:
• Тренируйся на свой страх и риск
• Консультируйся с врачом при необходимости
• Следуй технике безопасности

🔄 Изменения:
• Условия могут изменяться
• Уведомления о изменениях в боте

📧 Вопросы: legal@dianalisa.com
            """
            
            await query.edit_message_text(
                terms_text,
                reply_markup=keyboards.back_to_main(),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа условий использования: {e}")
            await query.edit_message_text(
                "❌ Ошибка загрузки условий использования.",
                reply_markup=keyboards.back_to_main()
            )

# Глобальный экземпляр информационной системы
info_system = InfoSystem()
