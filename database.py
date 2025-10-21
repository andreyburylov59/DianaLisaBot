"""
🗄️ База данных SQLite для бота DianaLisa
Управление пользователями, задачами и статистикой
"""

import sqlite3
import logging
from enhanced_logger import get_logger
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH

logger = logging.getLogger(__name__)
enhanced_logger = get_logger("database")

class Database:
    """Класс для работы с базой данных SQLite"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT UNIQUE,
                        phone TEXT UNIQUE,
                        timezone TEXT DEFAULT 'Europe/Moscow',
                        current_day INTEGER DEFAULT 1,
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_premium BOOLEAN DEFAULT FALSE,
                        premium_expires TIMESTAMP,
                        referral_code TEXT UNIQUE,
                        referred_by INTEGER,
                        total_referrals INTEGER DEFAULT 0,
                        total_purchases REAL DEFAULT 0.0,
                        training_completed BOOLEAN DEFAULT FALSE,
                        collected_tips TEXT DEFAULT '[]',
                        FOREIGN KEY (referred_by) REFERENCES users(user_id)
                    )
                ''')
                
                # Таблица задач планировщика
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scheduled_jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        job_type TEXT,
                        scheduled_time TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')
                
                # Таблица статистики
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        event_type TEXT,
                        event_data TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')
                
                # Таблица оценок тренировок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS training_feedback (
                        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        day INTEGER,
                        difficulty_rating INTEGER,
                        clarity_rating INTEGER,
                        comments TEXT,
                        timestamp TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица платежей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        amount REAL,
                        currency TEXT,
                        payment_type TEXT,
                        status TEXT,
                        transaction_id TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')
                
                # Таблица отзывов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        rating INTEGER,
                        review_text TEXT,
                        is_approved BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("База данных успешно инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None,
                last_name: str = None, email: str = None, phone: str = None, timezone: str = 'Europe/Moscow',
                referral_code: str = None, referred_by: int = None) -> bool:
        """Добавление нового пользователя"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Попытка добавления пользователя {user_id}: username={username}, first_name={first_name}, email={email}, phone={phone}, timezone={timezone}")
            
            # Логируем операцию с базой данных
            enhanced_logger.log_database_operation(
                'INSERT',
                'users',
                {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'email': email,
                    'phone': phone,
                    'timezone': timezone
                }
            )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Генерируем уникальный реферальный код
                if not referral_code:
                    referral_code = f"REF{user_id}{datetime.now().strftime('%Y%m%d')}"

                cursor.execute('''
                    INSERT OR REPLACE INTO users
                    (user_id, username, first_name, last_name, email, phone, timezone, referral_code, referred_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name, email, phone, timezone, referral_code, referred_by))

                conn.commit()
                logger.info(f"Пользователь {user_id} добавлен в базу данных")

                # Проверяем, что пользователь действительно добавлен
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if result:
                    logger.info(f"Проверка: пользователь {user_id} найден в базе данных")
                else:
                    logger.error(f"Проверка: пользователь {user_id} НЕ найден в базе данных!")

                # Логируем производительность
                duration = (datetime.now() - start_time).total_seconds()
                enhanced_logger.log_performance('add_user', duration, {'user_id': user_id})
                
                # Логируем действие пользователя
                enhanced_logger.log_user_action(user_id, 'user_registered', {
                    'username': username,
                    'first_name': first_name,
                    'email': email,
                    'timezone': timezone
                })

                return True

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            enhanced_logger.log_error(e, {
                'operation': 'add_user',
                'user_id': user_id,
                'duration': duration
            })
            logger.error(f"Ошибка добавления пользователя {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    user_data = dict(zip(columns, row))
                    
                    # Конвертируем булевые поля из SQLite (1/0) в Python (True/False)
                    boolean_fields = ['training_completed']
                    for field in boolean_fields:
                        if field in user_data:
                            user_data[field] = bool(user_data[field])
                    
                    return user_data
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {user_id}: {e}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновление информации о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Формируем запрос обновления
                set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
                values = list(kwargs.values()) + [user_id]
                
                cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
                conn.commit()
                
                logger.info(f"Пользователь {user_id} обновлен")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {user_id}: {e}")
            return False
    
    def update_user_day(self, user_id: int, day: int) -> bool:
        """Обновление дня пользователя"""
        return self.update_user(user_id, current_day=day, last_activity=datetime.now())
    
    def mark_training_completed(self, user_id: int) -> bool:
        """Отметка выполнения тренировки"""
        return self.update_user(user_id, training_completed=True)
    
    
    
    def reset_daily_marks(self, user_id: int) -> bool:
        """Сброс ежедневных отметок"""
        return self.update_user(user_id, 
                              training_completed=False)
    
    def add_scheduled_job(self, user_id: int, job_type: str, scheduled_time: datetime) -> bool:
        """Добавление задачи в планировщик"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scheduled_jobs (user_id, job_type, scheduled_time)
                    VALUES (?, ?, ?)
                ''', (user_id, job_type, scheduled_time))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления задачи: {e}")
            return False
    
    def get_scheduled_jobs(self, user_id: int = None) -> List[Dict[str, Any]]:
        """Получение задач планировщика"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if user_id:
                    cursor.execute('SELECT * FROM scheduled_jobs WHERE user_id = ? AND is_active = TRUE', (user_id,))
                else:
                    cursor.execute('SELECT * FROM scheduled_jobs WHERE is_active = TRUE')
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка получения задач: {e}")
            return []
    
    def deactivate_job(self, job_id: int) -> bool:
        """Деактивация задачи"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE scheduled_jobs SET is_active = FALSE WHERE id = ?', (job_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка деактивации задачи: {e}")
            return False
    
    def add_analytics_event(self, user_id: int, event_type: str, event_data: str = None) -> bool:
        """Добавление события аналитики"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analytics (user_id, event_type, event_data)
                    VALUES (?, ?, ?)
                ''', (user_id, event_type, event_data))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления события: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Основная информация о пользователе
                user = self.get_user(user_id)
                if not user:
                    return {}
                
                # Статистика событий
                cursor.execute('''
                    SELECT event_type, COUNT(*) as count 
                    FROM analytics 
                    WHERE user_id = ? 
                    GROUP BY event_type
                ''', (user_id,))
                events = dict(cursor.fetchall())
                
                # Статистика платежей
                cursor.execute('''
                    SELECT COUNT(*) as payments_count, SUM(amount) as total_amount
                    FROM payments 
                    WHERE user_id = ? AND status = 'completed'
                ''', (user_id,))
                payment_stats = cursor.fetchone()
                
                return {
                    'user': user,
                    'events': events,
                    'payments_count': payment_stats[0] if payment_stats[0] else 0,
                    'total_spent': payment_stats[1] if payment_stats[1] else 0.0
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Получение всех пользователей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users ORDER BY registration_date DESC')
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []
    
    def get_users_count(self) -> int:
        """Получение количества пользователей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка подсчета пользователей: {e}")
            return 0
    
    def add_payment(self, user_id: int, amount: float, currency: str, 
                   payment_type: str, status: str, transaction_id: str) -> bool:
        """Добавление платежа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payments (user_id, amount, currency, payment_type, status, transaction_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, amount, currency, payment_type, status, transaction_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления платежа: {e}")
            return False
    
    def add_review(self, user_id: int, rating: int, review_text: str) -> bool:
        """Добавление отзыва"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reviews (user_id, rating, review_text)
                    VALUES (?, ?, ?)
                ''', (user_id, rating, review_text))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления отзыва: {e}")
            return False
    
    def get_reviews(self, approved_only: bool = True) -> List[Dict[str, Any]]:
        """Получение отзывов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if approved_only:
                    cursor.execute('''
                        SELECT r.*, u.first_name, u.username 
                        FROM reviews r 
                        JOIN users u ON r.user_id = u.user_id 
                        WHERE r.is_approved = TRUE 
                        ORDER BY r.created_at DESC
                    ''')
                else:
                    cursor.execute('''
                        SELECT r.*, u.first_name, u.username 
                        FROM reviews r 
                        JOIN users u ON r.user_id = u.user_id 
                        ORDER BY r.created_at DESC
                    ''')
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка получения отзывов: {e}")
            return []
    
    def add_training_feedback(self, user_id: int, day: int, difficulty_rating: int, 
                            clarity_rating: int, comments: str = None) -> bool:
        """Добавление оценки тренировки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO training_feedback 
                    (user_id, day, difficulty_rating, clarity_rating, comments, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, day, difficulty_rating, clarity_rating, comments, 
                     datetime.now().isoformat()))
                conn.commit()
                logger.info(f"Оценка тренировки добавлена для пользователя {user_id}, день {day}")
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления оценки тренировки: {e}")
            return False
    
    def get_all_training_feedback(self) -> List[Dict[str, Any]]:
        """Получение всех оценок тренировок для админ панели"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT tf.*, u.first_name, u.username 
                    FROM training_feedback tf 
                    JOIN users u ON tf.user_id = u.user_id 
                    ORDER BY tf.timestamp DESC
                ''')
                rows = cursor.fetchall()
                
                feedback = []
                for row in rows:
                    feedback.append({
                        'user_id': row[0],
                        'day': row[1],
                        'difficulty_rating': row[2],
                        'clarity_rating': row[3],
                        'comments': row[4],
                        'timestamp': row[5],
                        'first_name': row[6],
                        'username': row[7]
                    })
                return feedback
        except Exception as e:
            logger.error(f"Ошибка получения всех оценок тренировок: {e}")
            return []
    
    def get_user_course_summary(self, user_id: int) -> Dict[str, Any]:
        """Получение сводки курса пользователя"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {}
            
            feedback = self.get_training_feedback(user_id)
            
            # Подсчитываем статистику
            total_days = user.get('current_day', 0)
            completed_trainings = sum(1 for f in feedback if f['day'] <= total_days)
            
            # Средние оценки
            avg_difficulty = sum(f['difficulty_rating'] for f in feedback) / len(feedback) if feedback else 0
            avg_clarity = sum(f['clarity_rating'] for f in feedback) / len(feedback) if feedback else 0
            
            return {
                'user_name': user.get('first_name', 'Пользователь'),
                'current_day': total_days,
                'completed_trainings': completed_trainings,
                'avg_difficulty': round(avg_difficulty, 1),
                'avg_clarity': round(avg_clarity, 1),
                'feedback_count': len(feedback),
                'registration_date': user.get('registration_date', ''),
                'feedback': feedback
            }
        except Exception as e:
            logger.error(f"Ошибка получения сводки курса: {e}")
            return {}
    
    def add_tip_to_collection(self, user_id: int, tip_type: str, tip_text: str) -> bool:
        """Добавление совета в коллекцию пользователя"""
        try:
            import json
            
            user = self.get_user(user_id)
            if not user:
                return False
            
            # Получаем текущие советы
            collected_tips = json.loads(user.get('collected_tips', '[]'))
            
            # Проверяем, нет ли уже такого совета
            tip_exists = any(tip['type'] == tip_type for tip in collected_tips)
            if tip_exists:
                return True  # Совет уже есть
            
            # Добавляем новый совет
            new_tip = {
                'type': tip_type,
                'text': tip_text,
                'timestamp': datetime.now().isoformat()
            }
            collected_tips.append(new_tip)
            
            # Сохраняем обновленные советы
            self.update_user(user_id, collected_tips=json.dumps(collected_tips, ensure_ascii=False))
            
            logger.info(f"Совет {tip_type} добавлен в коллекцию пользователя {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления совета в коллекцию: {e}")
            return False
    
    def get_collected_tips(self, user_id: int) -> List[Dict[str, str]]:
        """Получение собранных советов пользователя"""
        try:
            import json
            
            user = self.get_user(user_id)
            if not user:
                return []
            
            collected_tips = json.loads(user.get('collected_tips', '[]'))
            return collected_tips
            
        except Exception as e:
            logger.error(f"Ошибка получения собранных советов: {e}")
            return []
    
    def clear_collected_tips(self, user_id: int) -> bool:
        """Очистка собранных советов пользователя"""
        try:
            self.update_user(user_id, collected_tips='[]')
            logger.info(f"Советы пользователя {user_id} очищены")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки советов: {e}")
            return False

# Глобальный экземпляр базы данных
db = Database()
