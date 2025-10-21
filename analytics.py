"""
📊 Расширенная аналитика для бота DianaLisa
Детальная аналитика пользователей, трендов и метрик
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import sqlite3
from database import db

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """Расширенная система аналитики"""
    
    def __init__(self, database=None):
        self.db = database or db
    
    def get_user_engagement_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Получает метрики вовлеченности пользователя"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Общая активность
                cursor.execute('''
                    SELECT COUNT(*) as total_events
                    FROM analytics 
                    WHERE user_id = ? AND timestamp > ?
                ''', (user_id, cutoff_date))
                total_events = cursor.fetchone()[0]
                
                # Активность по дням
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as events
                    FROM analytics 
                    WHERE user_id = ? AND timestamp > ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                ''', (user_id, cutoff_date))
                daily_activity = cursor.fetchall()
                
                # Типы событий
                cursor.execute('''
                    SELECT event_type, COUNT(*) as count
                    FROM analytics 
                    WHERE user_id = ? AND timestamp > ?
                    GROUP BY event_type
                    ORDER BY count DESC
                ''', (user_id, cutoff_date))
                event_types = cursor.fetchall()
                
                # Время активности (часы дня)
                cursor.execute('''
                    SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                    FROM analytics 
                    WHERE user_id = ? AND timestamp > ?
                    GROUP BY strftime('%H', timestamp)
                    ORDER BY count DESC
                ''', (user_id, cutoff_date))
                hourly_activity = cursor.fetchall()
                
                # Сессии (группировка событий по дням)
                active_days = len(daily_activity)
                avg_events_per_day = total_events / max(active_days, 1)
                
                # Самый активный час
                most_active_hour = hourly_activity[0][0] if hourly_activity else None
                
                return {
                    'total_events': total_events,
                    'active_days': active_days,
                    'avg_events_per_day': round(avg_events_per_day, 2),
                    'daily_activity': daily_activity,
                    'event_types': dict(event_types),
                    'hourly_activity': dict(hourly_activity),
                    'most_active_hour': most_active_hour,
                    'engagement_score': self._calculate_engagement_score(total_events, active_days, days)
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения метрик вовлеченности: {e}")
            return {}
    
    def _calculate_engagement_score(self, total_events: int, active_days: int, period_days: int) -> float:
        """Вычисляет оценку вовлеченности пользователя (0-100)"""
        try:
            # Базовые метрики
            activity_rate = active_days / period_days  # Процент активных дней
            events_per_day = total_events / max(active_days, 1)  # Среднее событий в день
            
            # Нормализация (максимальные значения для расчета)
            max_activity_rate = 1.0  # 100% активных дней
            max_events_per_day = 20.0  # Предполагаем максимум 20 событий в день
            
            # Расчет оценки
            activity_score = min(activity_rate / max_activity_rate, 1.0) * 50
            events_score = min(events_per_day / max_events_per_day, 1.0) * 50
            
            engagement_score = activity_score + events_score
            return round(min(engagement_score, 100.0), 1)
            
        except Exception as e:
            logger.error(f"Ошибка расчета оценки вовлеченности: {e}")
            return 0.0
    
    def get_training_analytics(self, user_id: int) -> Dict[str, Any]:
        """Аналитика тренировок пользователя"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Статистика тренировок из таблицы users
                user = self.db.get_user(user_id)
                completed_trainings = user.get('training_count', 0) if user else 0
                
                # Время тренировок
                cursor.execute('''
                    SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                    FROM analytics 
                    WHERE user_id = ? AND event_type = 'training_completed'
                    GROUP BY strftime('%H', timestamp)
                    ORDER BY count DESC
                ''', (user_id,))
                training_times = cursor.fetchall()
                
                # Серии тренировок
                cursor.execute('''
                    SELECT DATE(timestamp) as date
                    FROM analytics 
                    WHERE user_id = ? AND event_type = 'training_completed'
                    ORDER BY timestamp
                ''', (user_id,))
                training_dates = [row[0] for row in cursor.fetchall()]
                
                # Расчет серий
                streaks = self._calculate_training_streaks(training_dates)
                
                return {
                    'completed_trainings': completed_trainings,
                    'training_times': dict(training_times),
                    'current_streak': streaks.get('current', 0),
                    'longest_streak': streaks.get('longest', 0),
                    'total_streaks': streaks.get('total', 0)
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения аналитики тренировок: {e}")
            return {}
    
    def _calculate_training_streaks(self, training_dates: List[str]) -> Dict[str, int]:
        """Вычисляет серии тренировок"""
        try:
            if not training_dates:
                return {'current': 0, 'longest': 0, 'total': 0}
            
            # Конвертируем даты
            dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in training_dates]
            dates = sorted(set(dates))  # Убираем дубликаты и сортируем
            
            if not dates:
                return {'current': 0, 'longest': 0, 'total': 0}
            
            # Вычисляем серии
            streaks = []
            current_streak = 1
            longest_streak = 1
            
            for i in range(1, len(dates)):
                diff = (dates[i] - dates[i-1]).days
                if diff == 1:  # Следующий день
                    current_streak += 1
                    longest_streak = max(longest_streak, current_streak)
                elif diff > 1:  # Пропуск дней
                    if current_streak > 1:
                        streaks.append(current_streak)
                    current_streak = 1
            
            # Добавляем последнюю серию
            if current_streak > 1:
                streaks.append(current_streak)
            
            # Текущая серия (если последняя тренировка была вчера или сегодня)
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            current = 0
            
            if dates[-1] == today or dates[-1] == yesterday:
                current = current_streak
            
            return {
                'current': current,
                'longest': longest_streak,
                'total': len(streaks)
            }
            
        except Exception as e:
            logger.error(f"Ошибка расчета серий тренировок: {e}")
            return {'current': 0, 'longest': 0, 'total': 0}
    
    def get_retention_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Анализ удержания пользователей"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество пользователей
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                
                # Активные пользователи за период
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id) 
                    FROM analytics 
                    WHERE timestamp > ?
                ''', (cutoff_date,))
                active_users = cursor.fetchone()[0]
                
                # Новые пользователи за период
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM users 
                    WHERE registration_date > ?
                ''', (cutoff_date,))
                new_users = cursor.fetchone()[0]
                
                # Пользователи с повторной активностью
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id)
                    FROM analytics 
                    WHERE user_id IN (
                        SELECT user_id 
                        FROM analytics 
                        WHERE timestamp > ? AND timestamp <= ?
                        GROUP BY user_id 
                        HAVING COUNT(*) > 1
                    )
                ''', (cutoff_date - timedelta(days=7), cutoff_date))
                returning_users = cursor.fetchone()[0]
                
                # Расчет метрик
                retention_rate = (active_users / max(total_users, 1)) * 100
                new_user_rate = (new_users / max(total_users, 1)) * 100
                return_rate = (returning_users / max(active_users, 1)) * 100
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'new_users': new_users,
                    'returning_users': returning_users,
                    'retention_rate': round(retention_rate, 2),
                    'new_user_rate': round(new_user_rate, 2),
                    'return_rate': round(return_rate, 2)
                }
                
        except Exception as e:
            logger.error(f"Ошибка анализа удержания: {e}")
            return {}
    
    def get_feature_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Аналитика использования функций"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Использование основных функций
                cursor.execute('''
                    SELECT event_type, COUNT(*) as count, COUNT(DISTINCT user_id) as unique_users
                    FROM analytics 
                    WHERE timestamp > ?
                    GROUP BY event_type
                    ORDER BY count DESC
                ''', (cutoff_date,))
                feature_usage = cursor.fetchall()
                
                # Популярные кнопки
                cursor.execute('''
                    SELECT event_data, COUNT(*) as count
                    FROM analytics 
                    WHERE event_type = 'button_click' AND timestamp > ?
                    GROUP BY event_data
                    ORDER BY count DESC
                    LIMIT 10
                ''', (cutoff_date,))
                popular_buttons = cursor.fetchall()
                
                # Конверсия в покупки
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id) as users_with_purchases
                    FROM payments 
                    WHERE status = 'completed' AND created_at > ?
                ''', (cutoff_date,))
                users_with_purchases = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id) as total_active_users
                    FROM analytics 
                    WHERE timestamp > ?
                ''', (cutoff_date,))
                total_active_users = cursor.fetchone()[0]
                
                conversion_rate = (users_with_purchases / max(total_active_users, 1)) * 100
                
                return {
                    'feature_usage': [
                        {
                            'feature': row[0],
                            'total_uses': row[1],
                            'unique_users': row[2]
                        } for row in feature_usage
                    ],
                    'popular_buttons': dict(popular_buttons),
                    'conversion_rate': round(conversion_rate, 2),
                    'users_with_purchases': users_with_purchases
                }
                
        except Exception as e:
            logger.error(f"Ошибка анализа использования функций: {e}")
            return {}
    
    def get_user_segments(self) -> Dict[str, Any]:
        """Сегментация пользователей"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Сегменты по активности
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN activity_count >= 50 THEN 'high_activity'
                            WHEN activity_count >= 10 THEN 'medium_activity'
                            ELSE 'low_activity'
                        END as segment,
                        COUNT(*) as users
                    FROM (
                        SELECT user_id, COUNT(*) as activity_count
                        FROM analytics 
                        GROUP BY user_id
                    ) user_activity
                    GROUP BY segment
                ''')
                activity_segments = cursor.fetchall()
                
                # Сегменты по тренировкам
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN training_count >= 10 THEN 'fitness_enthusiast'
                            WHEN training_count >= 3 THEN 'regular_trainer'
                            WHEN training_count >= 1 THEN 'beginner'
                            ELSE 'inactive'
                        END as segment,
                        COUNT(*) as users
                    FROM users
                    GROUP BY segment
                ''')
                training_segments = cursor.fetchall()
                
                # Сегменты по покупкам
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN total_purchases >= 1000 THEN 'premium'
                            WHEN total_purchases >= 100 THEN 'paying'
                            WHEN total_purchases > 0 THEN 'trial'
                            ELSE 'free'
                        END as segment,
                        COUNT(*) as users
                    FROM users
                    GROUP BY segment
                ''')
                purchase_segments = cursor.fetchall()
                
                return {
                    'activity_segments': dict(activity_segments),
                    'training_segments': dict(training_segments),
                    'purchase_segments': dict(purchase_segments)
                }
                
        except Exception as e:
            logger.error(f"Ошибка сегментации пользователей: {e}")
            return {}
    
    def get_trends_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Анализ трендов"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Тренд регистраций
                cursor.execute('''
                    SELECT DATE(registration_date) as date, COUNT(*) as registrations
                    FROM users 
                    WHERE registration_date > ?
                    GROUP BY DATE(registration_date)
                    ORDER BY date
                ''', (cutoff_date,))
                registration_trend = cursor.fetchall()
                
                # Тренд активности
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as events
                    FROM analytics 
                    WHERE timestamp > ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                ''', (cutoff_date,))
                activity_trend = cursor.fetchall()
                
                # Тренд тренировок
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as trainings
                    FROM analytics 
                    WHERE event_type = 'training_completed' AND timestamp > ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                ''', (cutoff_date,))
                training_trend = cursor.fetchall()
                
                return {
                    'registration_trend': dict(registration_trend),
                    'activity_trend': dict(activity_trend),
                    'training_trend': dict(training_trend)
                }
                
        except Exception as e:
            logger.error(f"Ошибка анализа трендов: {e}")
            return {}
    
    def generate_user_report(self, user_id: int) -> str:
        """Генерирует детальный отчет о пользователе"""
        try:
            user = self.db.get_user(user_id)
            if not user:
                return "❌ Пользователь не найден"
            
            # Получаем различные метрики
            engagement = self.get_user_engagement_metrics(user_id)
            training = self.get_training_analytics(user_id)
            
            # Формируем отчет
            report = f"""
📊 <b>Детальный отчет пользователя</b>

👤 <b>Основная информация:</b>
• Имя: {user.get('username', user.get('first_name', 'Не указано'))}
• Email: {user.get('email', 'Не указан')}
• Регистрация: {user.get('registration_date', 'Не указана')}
• Текущий день: {user.get('current_day', 1)}/3

📈 <b>Метрики вовлеченности:</b>
• Общая активность: {engagement.get('total_events', 0)} событий
• Активных дней: {engagement.get('active_days', 0)} из 30
• Среднее событий в день: {engagement.get('avg_events_per_day', 0)}
• Оценка вовлеченности: {engagement.get('engagement_score', 0)}/100
• Самый активный час: {engagement.get('most_active_hour', 'Не определен')}:00

🏋️‍♀️ <b>Статистика тренировок:</b>
• Выполнено тренировок: {training.get('completed_trainings', 0)}
• Текущая серия: {training.get('current_streak', 0)} дней
• Самая длинная серия: {training.get('longest_streak', 0)} дней
• Всего серий: {training.get('total_streaks', 0)}

🎯 <b>Рекомендации:</b>
{self._generate_recommendations(engagement, training)}
            """
            
            return report.strip()
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            return "❌ Ошибка генерации отчета"
    
    def _generate_recommendations(self, engagement: Dict, training: Dict) -> str:
        """Генерирует рекомендации на основе аналитики"""
        recommendations = []
        
        # Рекомендации по вовлеченности
        if engagement.get('engagement_score', 0) < 30:
            recommendations.append("• Увеличьте активность в боте")
        elif engagement.get('engagement_score', 0) > 80:
            recommendations.append("• Отличная активность! Продолжайте в том же духе")
        
        # Рекомендации по тренировкам
        if training.get('current_streak', 0) == 0:
            recommendations.append("• Начните новую серию тренировок")
        elif training.get('current_streak', 0) >= 7:
            recommendations.append("• Отличная серия! Не прерывайте её")
        
        # Рекомендации по времени
        most_active_hour = engagement.get('most_active_hour')
        if most_active_hour:
            hour = int(most_active_hour)
            if 6 <= hour < 12:
                recommendations.append("• Вы активны утром - отличное время для тренировок")
            elif 20 <= hour <= 23:
                recommendations.append("• Вечерняя активность - попробуйте утренние тренировки")
        
        if not recommendations:
            recommendations.append("• Продолжайте использовать все функции бота")
        
        return "\n".join(recommendations)

# Глобальный экземпляр расширенной аналитики
advanced_analytics = AdvancedAnalytics()
