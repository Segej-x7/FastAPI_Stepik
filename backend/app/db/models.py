# Импорт необходимых модулей и классов
from enum import Enum  # Для создания перечислений
from sqlalchemy import Boolean, Column, Integer, String, Text, Enum as SQLEnum  # SQLAlchemy типы для БД
from sqlalchemy.sql import select  # Для SQL запросов
from app.db.database import Base  # Базовый класс для моделей SQLAlchemy
from pydantic import BaseModel, EmailStr, Field  # Для создания моделей валидации данных
from datetime import datetime, timedelta  # Для работы с датами и временем
from typing import Optional  # Для указания необязательных полей

# Перечисление ролей пользователей
class UserRole(str, Enum):
    ADMIN = "admin"       # Администратор
    MODERATOR = "moderator"  # Модератор
    USER = "user"         # Обычный пользователь

# Модель Pydantic для создания пользователя (входные данные)
class UserCreate(BaseModel):
    username: str         # Имя пользователя
    email: EmailStr       # Email (валидируется автоматически)
    password: str         # Пароль
    role: UserRole = UserRole.USER  # Роль пользователя, по умолчанию "user"


# Модель SQLAlchemy для таблицы пользователей в БД
class DBUser(Base):
    __tablename__ = "users"  # Название таблицы в БД
    
    # Колонки таблицы:
    id = Column(Integer, primary_key=True, index=True)  # Первичный ключ
    username = Column(String(50), unique=True, index=True)  # Уникальное имя пользователя
    email = Column(String(100))  # Email пользователя
    hashed_password = Column(String(100))  # Хешированный пароль
    role = Column(SQLEnum(UserRole), default=UserRole.USER)  # Роль из перечисления
    is_active = Column(Boolean, default=True)  # Флаг активности пользователя

# Модель SQLAlchemy для таблицы обратной связи
class DBFeedback(Base):
    __tablename__ = "feedback"  # Название таблицы
    
    # Колонки таблицы:
    id = Column(Integer, primary_key=True, index=True)  # Первичный ключ
    name = Column(String(50))  # Имя отправителя
    message = Column(Text)  # Текст сообщения (длинный текст)
    email = Column(String(100))  # Email отправителя
    phone = Column(String(20))  # Телефон отправителя


# Модель Pydantic для ответа с данными пользователя
class UserResponse(BaseModel):
    id: int               # Первичный ключ
    username: str         # Имя пользователя
    email: EmailStr       # Email
    role: UserRole        # Роль
    is_active: bool       # Статус активности

    class Config:
        from_attributes = True  # Позволяет создавать модель из ORM объекта

# Модель Pydantic для создания отзыва с валидацией полей
class FeedbackCreate(BaseModel):
    name: str = Field(..., pattern=r'^[a-zA-Zа-яА-ЯёЁ0-9_\-\s]+$', min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=2000)
    email: EmailStr
    phone: str = Field(default="", pattern=r'^[\d\+\(\)\s\-]*$', min_length=0, max_length=20)

# Модель Pydantic для токена доступа
class Token(BaseModel):
    access_token: str  # JWT токен
    token_type: str    # Тип токена (обычно "bearer")

# Модель Pydantic для данных в токене
class TokenData(BaseModel):
    username: Optional[str] = None  # Имя пользователя (может быть None)
    expires: Optional[datetime] = None  # Время истечения токена (может быть None)

# Модель Pydantic для обновления данных пользователя
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None  # Новый email (необязательное поле)
    password: Optional[str] = None    # Новый пароль (необязательное поле)