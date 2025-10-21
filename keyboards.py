"""
⌨️ Клавиатуры и кнопки для бота DianaLisa
Создание интерактивных клавиатур для удобного взаимодействия
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from config import BUTTONS

class Keyboards:
    """Класс для создания клавиатур бота"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Главное меню бота"""
        try:
            keyboard = [
                [InlineKeyboardButton(BUTTONS['start_training'], callback_data='start_training')],
                [InlineKeyboardButton(BUTTONS['faq'], callback_data='faq')],
                [
                    InlineKeyboardButton(BUTTONS['full_course'], callback_data='full_course'),
                    InlineKeyboardButton(BUTTONS['online_training'], callback_data='online_training')
                ],
                [InlineKeyboardButton(BUTTONS['contact_support'], callback_data='contact_support')]
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("🏋️‍♀️ Начать тренировку", callback_data='start_training')],
                [InlineKeyboardButton("❓ FAQ", callback_data='faq')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def training_menu(day: int) -> InlineKeyboardMarkup:
        """Меню тренировок с учетом прогресса пользователя"""
        try:
            # Проверяем корректность параметра day
            if not isinstance(day, int) or day < 1:
                day = 1  # Используем значение по умолчанию
            
            keyboard = []
            
            # День 1 - всегда доступен
            keyboard.append([InlineKeyboardButton("🏋️‍♀️ День 1 - Базовая разминка", callback_data='training_day_1')])
            
            # День 2 - доступен только если current_day >= 2
            if day >= 2:
                keyboard.append([InlineKeyboardButton("🏋️‍♀️ День 2 - Силовые упражнения", callback_data='training_day_2')])
            else:
                keyboard.append([InlineKeyboardButton("🔒 День 2 - Заблокирован (завершите День 1)", callback_data='noop')])
            
            # День 3 - доступен только если current_day >= 3
            if day >= 3:
                keyboard.append([InlineKeyboardButton("🏋️‍♀️ День 3 - Интенсивная тренировка", callback_data='training_day_3')])
            else:
                keyboard.append([InlineKeyboardButton("🔒 День 3 - Заблокирован (завершите День 2)", callback_data='noop')])
            
            keyboard.append([InlineKeyboardButton(BUTTONS['back_to_menu'], callback_data='main_menu')])
            
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("🏋️‍♀️ День 1 - Базовая разминка", callback_data='training_day_1')],
                [InlineKeyboardButton(BUTTONS['back_to_menu'], callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def like_dislike_menu(day: int) -> InlineKeyboardMarkup:
        """Меню для оценки тренировки (понравилось/не понравилось)"""
        try:
            # Проверяем корректность параметра day
            if not isinstance(day, int) or day < 1:
                day = 1  # Используем значение по умолчанию
            
            keyboard = [
                [InlineKeyboardButton("😊 Понравилось", callback_data=f'feedback_like_{day}')],
                [InlineKeyboardButton("😞 Не понравилось", callback_data=f'feedback_dislike_{day}')]
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("😊 Понравилось", callback_data='feedback_like_1')],
                [InlineKeyboardButton("😞 Не понравилось", callback_data='feedback_dislike_1')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def text_input_menu() -> InlineKeyboardMarkup:
        """Меню для ввода текста (отмена)"""
        try:
            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def payment_menu() -> InlineKeyboardMarkup:
        """Меню оплаты"""
        try:
            keyboard = [
                [InlineKeyboardButton(BUTTONS['buy_course'], callback_data='buy_course')],
                [InlineKeyboardButton(BUTTONS['buy_training'], callback_data='buy_training')],
                [InlineKeyboardButton(BUTTONS['back_to_menu'], callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("💳 Купить курс", callback_data='buy_course')],
                [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Админское меню"""
        try:
            keyboard = [
                [InlineKeyboardButton(BUTTONS['user_stats'], callback_data='admin_stats')],
                [InlineKeyboardButton(BUTTONS['send_message'], callback_data='admin_send_message')],
                [InlineKeyboardButton(BUTTONS['export_db'], callback_data='admin_export_db')],
                [InlineKeyboardButton("📊 Аналитика", callback_data='admin_analytics')],
                [InlineKeyboardButton("👥 Пользователи", callback_data='admin_users')],
                [InlineKeyboardButton("💰 Платежи", callback_data='admin_payments')],
                [InlineKeyboardButton("⭐ Отзывы", callback_data='admin_reviews')],
                [InlineKeyboardButton("💪 Отзывы о тренировках", callback_data='admin_training_feedback')],
                [InlineKeyboardButton("🗑 Очистить и перезапустить бота", callback_data='admin_clear_db')],
                [InlineKeyboardButton(BUTTONS['back_to_menu'], callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
                [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_main_menu() -> InlineKeyboardMarkup:
        """Главное меню для админов (включает админ-панель)"""
        try:
            keyboard = [
                [InlineKeyboardButton(BUTTONS['start_training'], callback_data='start_training')],
                [InlineKeyboardButton(BUTTONS['faq'], callback_data='faq')],
                [InlineKeyboardButton(BUTTONS['full_course'], callback_data='full_course')],
                [InlineKeyboardButton(BUTTONS['online_training'], callback_data='online_training')],
                [InlineKeyboardButton(BUTTONS['contact_support'], callback_data='contact_support')],
                [InlineKeyboardButton(BUTTONS['admin_panel'], callback_data='admin_panel')]
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("🏋️‍♀️ Начать тренировку", callback_data='start_training')],
                [InlineKeyboardButton("❓ FAQ", callback_data='faq')],
                [InlineKeyboardButton("⚙️ Админ-панель", callback_data='admin_panel')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def timezone_menu() -> InlineKeyboardMarkup:
        """Меню выбора часового пояса"""
        keyboard = [
            [
                InlineKeyboardButton("🇷🇺 Москва", callback_data='timezone_Europe/Moscow'),
                InlineKeyboardButton("🇺🇦 Киев", callback_data='timezone_Europe/Kiev')
            ],
            [
                InlineKeyboardButton("🇧🇾 Минск", callback_data='timezone_Europe/Minsk'),
                InlineKeyboardButton("🇰🇿 Алматы", callback_data='timezone_Asia/Almaty')
            ],
            [
                InlineKeyboardButton("🇺🇸 Нью-Йорк", callback_data='timezone_America/New_York'),
                InlineKeyboardButton("🇬🇧 Лондон", callback_data='timezone_Europe/London')
            ],
            [
                InlineKeyboardButton("🇩🇪 Берлин", callback_data='timezone_Europe/Berlin'),
                InlineKeyboardButton("🇫🇷 Париж", callback_data='timezone_Europe/Paris')
            ],
            [
                InlineKeyboardButton("🇯🇵 Токио", callback_data='timezone_Asia/Tokyo'),
                InlineKeyboardButton("🇦🇺 Сидней", callback_data='timezone_Australia/Sydney')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def yes_no_menu() -> InlineKeyboardMarkup:
        """Меню Да/Нет"""
        keyboard = [
            [
                InlineKeyboardButton(BUTTONS['yes'], callback_data='yes'),
                InlineKeyboardButton(BUTTONS['no'], callback_data='no')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def course_packages() -> InlineKeyboardMarkup:
        """Пакеты курсов"""
        keyboard = [
            [InlineKeyboardButton("💎 Приобрести курс - 1990₽", callback_data='package_basic')],
            [InlineKeyboardButton(BUTTONS['back_to_menu'], callback_data='main_menu')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def training_packages() -> InlineKeyboardMarkup:
        """Пакеты онлайн-тренировок"""
        keyboard = [
            [InlineKeyboardButton("💻 1 тренировка - 500₽", callback_data='training_single')],
            [InlineKeyboardButton("📅 5 тренировок - 2000₽", callback_data='training_pack5')],
            [InlineKeyboardButton("🏋️‍♀️ 10 тренировок - 3500₽", callback_data='training_pack10')],
            [InlineKeyboardButton("🔥 Безлимит на месяц - 5000₽", callback_data='training_unlimited')],
            [InlineKeyboardButton(BUTTONS['back_to_menu'], callback_data='main_menu')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def rating_menu() -> InlineKeyboardMarkup:
        """Меню оценки"""
        keyboard = [
            [
                InlineKeyboardButton("⭐", callback_data='rating_1'),
                InlineKeyboardButton("⭐⭐", callback_data='rating_2'),
                InlineKeyboardButton("⭐⭐⭐", callback_data='rating_3'),
                InlineKeyboardButton("⭐⭐⭐⭐", callback_data='rating_4'),
                InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data='rating_5')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def contact_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для отправки контакта"""
        keyboard = [
            [KeyboardButton("📱 Отправить контакт", request_contact=True)],
            [KeyboardButton("❌ Отмена")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def location_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для отправки локации"""
        keyboard = [
            [KeyboardButton("📍 Отправить локацию", request_location=True)],
            [KeyboardButton("❌ Отмена")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def admin_user_actions(user_id: int) -> InlineKeyboardMarkup:
        """Действия админа с пользователем"""
        keyboard = [
            [InlineKeyboardButton("📨 Написать сообщение", callback_data=f'admin_message_{user_id}')],
            [InlineKeyboardButton("🔙 Назад", callback_data='admin_users')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination_menu(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        """Меню пагинации"""
        keyboard = []
        
        # Кнопки навигации
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f'{prefix}_page_{current_page-1}'))
        
        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data='noop'))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f'{prefix}_page_{current_page+1}'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Кнопка назад
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='admin_menu')])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirmation_menu(action: str) -> InlineKeyboardMarkup:
        """Меню подтверждения действия"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data=f'confirm_{action}'),
                InlineKeyboardButton("❌ Отмена", callback_data='cancel_action')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    
    @staticmethod
    def start_registration_menu() -> InlineKeyboardMarkup:
        """Меню начала регистрации"""
        keyboard = [
            [InlineKeyboardButton("🚀 Начать регистрацию", callback_data='start_registration')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Простая кнопка возврата в главное меню"""
        try:
            keyboard = [
                [InlineKeyboardButton(BUTTONS['back_to_menu'], callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            # Fallback - простое меню
            keyboard = [
                [InlineKeyboardButton("🏠 В главное меню", callback_data='main_menu')]
            ]
            return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def name_input_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для ввода имени"""
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к регистрации", callback_data='back_to_registration_start')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def phone_input_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для ввода номера телефона"""
        keyboard = [
            [InlineKeyboardButton("❌ Не хочу вводить номер", callback_data='skip_phone')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def difficulty_rating_menu(day: int) -> InlineKeyboardMarkup:
        """Меню оценки сложности тренировки"""
        keyboard = [
            [InlineKeyboardButton("😊 Очень легко", callback_data=f'difficulty_1_{day}')],
            [InlineKeyboardButton("🙂 Легко", callback_data=f'difficulty_2_{day}')],
            [InlineKeyboardButton("😐 Нормально", callback_data=f'difficulty_3_{day}')],
            [InlineKeyboardButton("😰 Сложно", callback_data=f'difficulty_4_{day}')],
            [InlineKeyboardButton("😵 Очень сложно", callback_data=f'difficulty_5_{day}')],
            [InlineKeyboardButton("🔙 Назад", callback_data='main_menu')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def clarity_rating_menu(day: int) -> InlineKeyboardMarkup:
        """Меню оценки понятности тренировки"""
        keyboard = [
            [InlineKeyboardButton("😕 Совсем непонятно", callback_data=f'clarity_1_{day}')],
            [InlineKeyboardButton("😐 Сложно понять", callback_data=f'clarity_2_{day}')],
            [InlineKeyboardButton("🙂 Понятно", callback_data=f'clarity_3_{day}')],
            [InlineKeyboardButton("😊 Очень понятно", callback_data=f'clarity_4_{day}')],
            [InlineKeyboardButton("🤩 Идеально понятно", callback_data=f'clarity_5_{day}')],
            [InlineKeyboardButton("🔙 Назад", callback_data=f'difficulty_1_{day}')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def comments_menu(day: int) -> InlineKeyboardMarkup:
        """Меню для комментариев к тренировке"""
        keyboard = [
            [InlineKeyboardButton("💬 Добавить комментарий", callback_data=f'add_comment_{day}')],
            [InlineKeyboardButton("⏭️ Без комментариев", callback_data=f'finish_feedback_{day}')],
            [InlineKeyboardButton("🔙 Назад", callback_data=f'clarity_1_{day}')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def course_completion_menu() -> InlineKeyboardMarkup:
        """Меню завершения курса"""
        keyboard = [
            [InlineKeyboardButton("📊 Посмотреть результаты", callback_data='view_results')],
            [InlineKeyboardButton("💎 Полный курс", callback_data='full_course')],
            [InlineKeyboardButton("⭐ Оставить отзыв", callback_data='leave_review')],
            [InlineKeyboardButton("🔙 В меню", callback_data='main_menu')]
        ]
        return InlineKeyboardMarkup(keyboard)

# Глобальный экземпляр клавиатур
keyboards = Keyboards()
