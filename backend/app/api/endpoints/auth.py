# backend/app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.core.config import settings
from app.api.dependencies import get_current_user
from app.db.models import Token, UserCreate, UserResponse, TokenData, UserRole
from app.db.database import async_session
from app.db.models import DBUser
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy import select

# Создаем роутер FastAPI с префиксом "/auth" и тегом "auth" для группировки в документации
router = APIRouter(prefix="/auth", tags=["auth"])

# Инициализируем контекст для хеширования паролей с использованием алгоритма bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Эндпоинт для получения токена доступа (аутентификации)
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Аутентификация пользователя и выдача JWT токена.
    
    Принимает:
    - username: имя пользователя
    - password: пароль
    
    Возвращает:
    - access_token: JWT токен для аутентификации
    - token_type: тип токена (bearer)
    """
    # Открываем асинхронную сессию с базой данных
    async with async_session() as session:
        # Ищем пользователя по имени пользователя
        result = await session.execute(select(DBUser).where(DBUser.username == form_data.username))
        user = result.scalars().first()
        
    # Проверяем, существует ли пользователь и совпадает ли пароль
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Устанавливаем срок действия токена из настроек
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Генерируем JWT токен с данными пользователя
    access_token = jwt.encode(
        {"sub": user.username, "role": user.role.value},  # payload токена
        settings.SECRET_KEY,                             # секретный ключ
        algorithm=settings.ALGORITHM                     # алгоритм шифрования
    )
    
    # Возвращаем токен в стандартном формате OAuth2
    return {"access_token": access_token, "token_type": "bearer"}


# Эндпоинт для регистрации новых пользователей
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    Регистрация нового пользователя в системе.
    
    Принимает:
    - username: уникальное имя пользователя
    - email: email пользователя
    - password: пароль
    - role: роль пользователя (опционально)
    
    Возвращает:
    - Данные зарегистрированного пользователя
    """
    async with async_session() as session:
        # Проверяем, что username уникален
        result = await session.execute(select(DBUser).where(DBUser.username == user.username))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Хешируем пароль перед сохранением в базу
        hashed_password = pwd_context.hash(user.password)
        
        # Создаем объект пользователя для базы данных
        db_user = DBUser(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role  # Используем значение из запроса
        )
        
        # Добавляем пользователя в сессию и сохраняем в базу
        session.add(db_user)
        await session.commit()
        
        # Обновляем объект пользователя (получаем сгенерированный ID и т.д.)
        await session.refresh(db_user)
        
        # Возвращаем данные зарегистрированного пользователя
        return db_user