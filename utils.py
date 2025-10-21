"""
🛠 Утилиты и вспомогательные функции для бота DianaLisa
Валидация, форматирование, работа с часовыми поясами и другие полезные функции
"""

import re
import logging
import pytz
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib
import random
import string
from telegram import InputFile
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

class Utils:
    """Класс с утилитарными функциями"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Валидация email адреса"""
        try:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        except Exception as e:
            logger.error(f"Ошибка валидации email: {e}")
            return False
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация номера телефона"""
        try:
            # Убираем все символы кроме цифр и +
            clean_phone = re.sub(r'[^\d+]', '', phone)
            
            # Проверяем формат российского номера
            if clean_phone.startswith('+7') and len(clean_phone) == 12:
                return True
            
            # Проверяем формат без +7
            if clean_phone.startswith('8') and len(clean_phone) == 11:
                return True
            
            # Проверяем формат с 7
            if clean_phone.startswith('7') and len(clean_phone) == 11:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка валидации телефона: {e}")
            return False
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Форматирование номера телефона"""
        try:
            # Убираем все символы кроме цифр
            clean_phone = re.sub(r'[^\d]', '', phone)
            
            # Приводим к формату +7XXXXXXXXXX
            if clean_phone.startswith('8'):
                clean_phone = '7' + clean_phone[1:]
            elif not clean_phone.startswith('7'):
                clean_phone = '7' + clean_phone
            
            return '+' + clean_phone
            
        except Exception as e:
            logger.error(f"Ошибка форматирования телефона: {e}")
            return phone
    
    @staticmethod
    def get_user_timezone(user_id: int) -> str:
        """Получение часового пояса пользователя"""
        try:
            from database import db
            user = db.get_user(user_id)
            return user['timezone'] if user else 'Europe/Moscow'
        except Exception as e:
            logger.error(f"Ошибка получения часового пояса: {e}")
            return 'Europe/Moscow'
    
    @staticmethod
    def format_datetime(dt: datetime, timezone_str: str = 'Europe/Moscow') -> str:
        """Форматирование даты и времени"""
        try:
            tz = pytz.timezone(timezone_str)
            local_dt = dt.astimezone(tz)
            return local_dt.strftime('%d.%m.%Y %H:%M')
        except Exception as e:
            logger.error(f"Ошибка форматирования даты: {e}")
            return dt.strftime('%d.%m.%Y %H:%M')
    
    @staticmethod
    def get_timezone_offset(timezone_str: str) -> int:
        """Получение смещения часового пояса в часах"""
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            return now.utcoffset().total_seconds() / 3600
        except Exception as e:
            logger.error(f"Ошибка получения смещения часового пояса: {e}")
            return 3  # По умолчанию UTC+3 (Москва)
    
    @staticmethod
    def generate_referral_code(user_id: int) -> str:
        """Генерация реферального кода"""
        try:
            # Создаем код на основе user_id и случайных символов
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            return f"REF{user_id}{random_part}"
        except Exception as e:
            logger.error(f"Ошибка генерации реферального кода: {e}")
            return f"REF{user_id}"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Ошибка хеширования пароля: {e}")
            return password
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """Генерация случайной строки"""
        try:
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        except Exception as e:
            logger.error(f"Ошибка генерации случайной строки: {e}")
            return "random"
    
    @staticmethod
    def format_currency(amount: float, currency: str = 'RUB') -> str:
        """Форматирование валюты"""
        try:
            if currency == 'RUB':
                return f"{amount:.2f} ₽"
            elif currency == 'USD':
                return f"${amount:.2f}"
            elif currency == 'EUR':
                return f"€{amount:.2f}"
            else:
                return f"{amount:.2f} {currency}"
        except Exception as e:
            logger.error(f"Ошибка форматирования валюты: {e}")
            return f"{amount} {currency}"
    
    @staticmethod
    def format_percentage(value: float, total: float) -> str:
        """Форматирование процентов"""
        try:
            if total == 0:
                return "0%"
            percentage = (value / total) * 100
            return f"{percentage:.1f}%"
        except Exception as e:
            logger.error(f"Ошибка форматирования процентов: {e}")
            return "0%"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Обрезка текста"""
        try:
            if len(text) <= max_length:
                return text
            return text[:max_length-3] + "..."
        except Exception as e:
            logger.error(f"Ошибка обрезки текста: {e}")
            return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Очистка текста от лишних символов"""
        try:
            # Убираем лишние пробелы и переносы строк
            cleaned = re.sub(r'\s+', ' ', text.strip())
            return cleaned
        except Exception as e:
            logger.error(f"Ошибка очистки текста: {e}")
            return text
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Извлечение упоминаний из текста"""
        try:
            pattern = r'@(\w+)'
            return re.findall(pattern, text)
        except Exception as e:
            logger.error(f"Ошибка извлечения упоминаний: {e}")
            return []
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Извлечение хештегов из текста"""
        try:
            pattern = r'#(\w+)'
            return re.findall(pattern, text)
        except Exception as e:
            logger.error(f"Ошибка извлечения хештегов: {e}")
            return []
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        try:
            pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
            return re.match(pattern, url) is not None
        except Exception as e:
            logger.error(f"Ошибка проверки URL: {e}")
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Получение расширения файла"""
        try:
            return filename.split('.')[-1].lower() if '.' in filename else ''
        except Exception as e:
            logger.error(f"Ошибка получения расширения файла: {e}")
            return ''
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Форматирование размера файла"""
        try:
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = 0
            while size_bytes >= 1024 and i < len(size_names) - 1:
                size_bytes /= 1024.0
                i += 1
            
            return f"{size_bytes:.1f} {size_names[i]}"
        except Exception as e:
            logger.error(f"Ошибка форматирования размера файла: {e}")
            return f"{size_bytes} B"
    
    @staticmethod
    def calculate_age(birth_date: datetime) -> int:
        """Вычисление возраста"""
        try:
            today = datetime.now()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        except Exception as e:
            logger.error(f"Ошибка вычисления возраста: {e}")
            return 0
    
    @staticmethod
    def get_days_until_date(target_date: datetime) -> int:
        """Получение количества дней до даты"""
        try:
            today = datetime.now().date()
            target = target_date.date()
            return (target - today).days
        except Exception as e:
            logger.error(f"Ошибка вычисления дней до даты: {e}")
            return 0
    
    @staticmethod
    def is_weekend(date: datetime = None) -> bool:
        """Проверка, является ли дата выходным днем"""
        try:
            if date is None:
                date = datetime.now()
            return date.weekday() >= 5  # 5 = суббота, 6 = воскресенье
        except Exception as e:
            logger.error(f"Ошибка проверки выходного дня: {e}")
            return False
    
    @staticmethod
    def get_season(date: datetime = None) -> str:
        """Получение сезона года"""
        try:
            if date is None:
                date = datetime.now()
            
            month = date.month
            if month in [12, 1, 2]:
                return "зима"
            elif month in [3, 4, 5]:
                return "весна"
            elif month in [6, 7, 8]:
                return "лето"
            else:
                return "осень"
        except Exception as e:
            logger.error(f"Ошибка получения сезона: {e}")
            return "неизвестно"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Форматирование длительности"""
        try:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            
            if hours > 0:
                return f"{hours}ч {minutes}м {seconds}с"
            elif minutes > 0:
                return f"{minutes}м {seconds}с"
            else:
                return f"{seconds}с"
        except Exception as e:
            logger.error(f"Ошибка форматирования длительности: {e}")
            return f"{seconds}с"
    
    @staticmethod
    def get_random_motivation() -> str:
        """Получение случайной мотивационной фразы"""
        try:
            motivations = [
                "💪 Ты можешь это сделать!",
                "🌟 Каждый день - новый шанс!",
                "🔥 Верь в себя!",
                "✨ Ты сильнее, чем думаешь!",
                "🎯 Иди к своей цели!",
                "💎 Ты уникальна!",
                "🚀 Не останавливайся!",
                "🌈 После дождя всегда радуга!",
                "⭐ Ты заслуживаешь лучшего!",
                "🎉 Празднуй каждый маленький успех!"
            ]
            return random.choice(motivations)
        except Exception as e:
            logger.error(f"Ошибка получения мотивации: {e}")
            return "💪 Ты можешь это сделать!"
    
    @staticmethod
    def get_time_greeting() -> str:
        """Получение приветствия в зависимости от времени"""
        try:
            hour = datetime.now().hour
            
            if 5 <= hour < 12:
                return "🌅 Доброе утро!"
            elif 12 <= hour < 17:
                return "☀️ Добрый день!"
            elif 17 <= hour < 22:
                return "🌆 Добрый вечер!"
            else:
                return "🌙 Доброй ночи!"
        except Exception as e:
            logger.error(f"Ошибка получения приветствия: {e}")
            return "👋 Привет!"
    
    @staticmethod
    def validate_timezone(timezone_str: str) -> bool:
        """Валидация часового пояса"""
        try:
            pytz.timezone(timezone_str)
            return True
        except Exception as e:
            logger.error(f"Ошибка валидации часового пояса: {e}")
            return False
    
    @staticmethod
    def get_common_timezones() -> List[Dict[str, str]]:
        """Получение списка популярных часовых поясов"""
        return [
            {'name': '🇷🇺 Москва', 'value': 'Europe/Moscow'},
            {'name': '🇺🇦 Киев', 'value': 'Europe/Kiev'},
            {'name': '🇧🇾 Минск', 'value': 'Europe/Minsk'},
            {'name': '🇰🇿 Алматы', 'value': 'Asia/Almaty'},
            {'name': '🇺🇸 Нью-Йорк', 'value': 'America/New_York'},
            {'name': '🇬🇧 Лондон', 'value': 'Europe/London'},
            {'name': '🇩🇪 Берлин', 'value': 'Europe/Berlin'},
            {'name': '🇫🇷 Париж', 'value': 'Europe/Paris'},
            {'name': '🇯🇵 Токио', 'value': 'Asia/Tokyo'},
            {'name': '🇦🇺 Сидней', 'value': 'Australia/Sydney'}
        ]

# Глобальный экземпляр утилит
utils = Utils()

# Функции для совместимости
def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    return utils.validate_email(email)

def validate_name(name: str) -> bool:
    """Валидация имени - только текст, без цифр"""
    if not name or len(name.strip()) < 2:
        return False
    
    import re
    # Проверяем что имя содержит только буквы, пробелы, дефисы и апострофы
    # Исключаем цифры и специальные символы
    return bool(re.match(r'^[а-яёА-ЯЁa-zA-Z\s\-\']+$', name.strip()))

def validate_phone(phone: str) -> bool:
    """Валидация номера телефона - только цифры и разрешенные символы"""
    if not phone or len(phone.strip()) < 10:
        return False
    
    import re
    # Убираем все пробелы для проверки
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Проверяем что остались только цифры и возможно один плюс в начале
    if not re.match(r'^\+?[0-9]+$', clean_phone):
        return False
    
    # Проверяем длину (от 10 до 15 цифр)
    digits_only = re.sub(r'[^\d]', '', phone)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False
    
    return True

def get_user_timezone(user_id: int) -> str:
    """Получение часового пояса пользователя"""
    return utils.get_user_timezone(user_id)

def send_motivational_message(user_id: int, message: str = None):
    """Отправка мотивационного сообщения"""
    if message is None:
        message = utils.get_random_motivation()
    return message

# Новые функции для улучшенной визуализации
import os
from telegram import InputFile
from telegram.constants import ParseMode
import logging

logger = logging.getLogger(__name__)

def get_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Создание прогресс-бара"""
    if total == 0:
        return "░" * length
    
    filled = int((current / total) * length)
    empty = length - filled
    
    return "█" * filled + "░" * empty

def get_progress_percentage(current: int, total: int) -> int:
    """Получение процента прогресса"""
    if total == 0:
        return 0
    return int((current / total) * 100)

def format_progress_text(current: int, total: int, item_name: str) -> str:
    """Форматирование текста с прогрессом"""
    percentage = get_progress_percentage(current, total)
    progress_bar = get_progress_bar(current, total)
    
    return f"""
📊 <b>{item_name}</b>
{progress_bar} {percentage}%
({current}/{total})
    """

def split_long_text(text: str, max_length: int = 1000) -> tuple[str, str]:
    """
    Разделяет длинный текст на две части для caption и отдельного сообщения
    Для тренировок старается оставить заминку и советы в основной части
    """
    if len(text) <= max_length:
        return text, ""
    
    # Специальная логика для тренировок
    if "🏋️‍♀️ ДЕНЬ" in text and "💡 Советы:" in text:
        # Ищем разделители для тренировок
        parts = text.split('\n\n')
        caption_text = ""
        message_text = ""
        
        # Собираем основную часть до заминки
        for part in parts:
            if "🧘‍♀️ Заминка" in part or "💡 Советы:" in part:
                # Заминку и советы оставляем в основной части
                if len(caption_text + part + '\n\n') <= max_length:
                    caption_text += part + '\n\n'
                else:
                    # Если не помещается, переносим в дополнительное сообщение
                    message_text += part + '\n\n'
            else:
                if len(caption_text + part + '\n\n') <= max_length:
                    caption_text += part + '\n\n'
                else:
                    message_text += part + '\n\n'
        
        return caption_text.strip(), message_text.strip()
    
    # Обычная логика для других текстов
    paragraphs = text.split('\n\n')
    caption_text = ""
    message_text = ""
    
    for paragraph in paragraphs:
        if len(caption_text + paragraph + '\n\n') <= max_length:
            caption_text += paragraph + '\n\n'
        else:
            message_text += paragraph + '\n\n'
    
    return caption_text.strip(), message_text.strip()

async def send_image_with_text(bot, chat_id: int, image_path: str, text: str, 
                             reply_markup=None, parse_mode: str = ParseMode.HTML):
    """Отправка изображения с текстом"""
    try:
        logger.info(f"Попытка отправить изображение: {image_path}")
        
        # Разделяем длинный текст
        caption_text, message_text = split_long_text(text)
        
        if not os.path.exists(image_path):
            logger.warning(f"Файл изображения не найден: {image_path}")
            # Если изображение не найдено, отправляем только текст
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return
        
        logger.info(f"Файл изображения найден, размер: {os.path.getsize(image_path)} байт")
        
        with open(image_path, 'rb') as photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=InputFile(photo),
                caption=caption_text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            logger.info("Изображение успешно отправлено")
            
            # НЕ отправляем дополнительный текст отдельным сообщением
            # Все содержимое должно быть в caption изображения
            if message_text:
                logger.info("Дополнительный текст не отправлен (убрано по требованию)")
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        # В случае ошибки отправляем только текст
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )

def get_motivational_emoji(progress_percentage: int) -> str:
    """Получение мотивационного эмодзи на основе прогресса"""
    if progress_percentage >= 100:
        return "🏆"
    elif progress_percentage >= 80:
        return "🔥"
    elif progress_percentage >= 60:
        return "💪"
    elif progress_percentage >= 40:
        return "⚡"
    elif progress_percentage >= 20:
        return "🌟"
    else:
        return "🚀"

def format_course_progress_bar(current_day: int, total_days: int = 3) -> str:
    """Создает красивую шкалу прогресса курса"""
    progress_percentage = (current_day / total_days) * 100
    
    # Создаем шкалу из эмодзи
    filled_blocks = int(progress_percentage / 20)  # 5 блоков по 20%
    empty_blocks = 5 - filled_blocks
    
    progress_bar = "🟩" * filled_blocks + "⬜" * empty_blocks
    
    # Добавляем мотивационный эмодзи
    emoji = get_motivational_emoji(int(progress_percentage))
    
    return f"{emoji} Прогресс курса: {progress_bar} {current_day}/{total_days}"

def get_user_status_text(user: dict) -> str:
    """Возвращает текст статуса пользователя"""
    if user.get('is_premium', False):
        return "💎 Премиум участник"
    else:
        current_day = user.get('current_day', 1)
        if current_day <= 3:
            return f"🎯 Бесплатный курс (День {current_day}/3)"
        else:
            return "📚 Завершил бесплатный курс"

def format_course_progress(current_day: int, total_days: int = 3) -> str:
    """Форматирование прогресса курса"""
    percentage = get_progress_percentage(current_day, total_days)
    emoji = get_motivational_emoji(percentage)
    progress_bar = get_progress_bar(current_day, total_days)
    
    return f"""
{emoji} <b>Прогресс курса</b>

{progress_bar} {percentage}%
День {current_day} из {total_days}
    """

def format_collected_tips_message(collected_tips: list, completed_count: int, total_count: int) -> str:
    """Форматирование сообщения с собранными советами"""
    if not collected_tips:
        return "💡 Советы появятся по мере выполнения тренировок!"
    
    # Определяем эмодзи в зависимости от прогресса
    if completed_count == total_count:
        emoji = "🏆"
        title = "Поздравляем! Все советы собраны!"
    elif completed_count >= total_count * 0.75:
        emoji = "🔥"
        title = "Отлично! Почти все советы собраны!"
    elif completed_count >= total_count * 0.5:
        emoji = "💪"
        title = "Хорошо! Половина советов собрана!"
    else:
        emoji = "🌟"
        title = "Начало положено! Советы собираются!"
    
    message = f"""
{emoji} <b>{title}</b>

📊 Прогресс: {completed_count}/{total_count} советов собрано

💡 <b>Ваши собранные советы:</b>
"""
    
    # Добавляем советы с соответствующими эмодзи
    tip_emojis = {
        'training': '🏋️‍♀️'
    }
    
    for tip in collected_tips:
        tip_emoji = tip_emojis.get(tip['type'], '💡')
        message += f"\n{tip_emoji} {tip['text']}"
    
    if completed_count < total_count:
        remaining = total_count - completed_count
        message += f"\n\n🎯 Осталось собрать {remaining} совет(ов)!"
    
    return message

def get_tip_type_from_action(action: str) -> str:
    """Получение типа совета из действия"""
    tip_mapping = {
        'mark_training': 'training'
    }
    return tip_mapping.get(action, 'general')
