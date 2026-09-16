from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Модель пользователя (заказчик/исполнитель)"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    district = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    rating = db.Column(db.Float, default=5.0)
    completed_tasks = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    tasks_created = db.relationship('Task', backref='creator', lazy='dynamic', foreign_keys='Task.user_id')
    tasks_executed = db.relationship('Task', backref='executor_user', lazy='dynamic', foreign_keys='Task.executor_id')
    payments = db.relationship('Payment', backref='payer', lazy='dynamic')
    
    def set_password(self, password):
        """Установить хешированный пароль"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password_hash, password)
    
    def get_masked_phone(self):
        """Получить маскированный номер телефона"""
        if len(self.phone) >= 10:
            return self.phone[:2] + '****' + self.phone[-2:]
        return '***'
    
    def __repr__(self):
        return f'<User {self.name} ({self.phone})>'


class Task(db.Model):
    """Модель задачи/заказа"""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    urgency = db.Column(db.String(20), nullable=False, default='планово')
    status = db.Column(db.String(20), nullable=False, default='active')
    phone_hidden = db.Column(db.String(20), nullable=False)
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Связи
    payments = db.relationship('Payment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_phone_unlocked_for(self, user_id):
        """Проверить, разблокирован ли телефон для конкретного пользователя"""
        if self.user_id == user_id:
            return True
        payment = Payment.query.filter_by(
            task_id=self.id,
            executor_id=user_id,
            status='paid'
        ).first()
        return payment is not None
    
    def get_display_phone(self, user_id):
        """Получить номер телефона (полный или маскированный)"""
        if self.is_phone_unlocked_for(user_id):
            return self.creator.phone
        return self.phone_hidden
    
    def __repr__(self):
        return f'<Task {self.title} ({self.status})>'


class Payment(db.Model):
    """Модель платежа за доступ к номеру телефона"""
    
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False, default=50)
    qr_code_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Payment {self.id} for Task {self.task_id} ({self.status})>'
