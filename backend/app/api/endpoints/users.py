# Импорт необходимых модулей и классов
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.db.database import async_session  # Асинхронная сессия для работы с БД
from app.db.models import DBUser, UserResponse, UserUpdate  # Модели БД и Pydantic
from app.api.dependencies import get_current_active_user  # Зависимость для получения текущего пользователя

# Создание роутера для обработки запросов, связанных с пользователями
# prefix="/api/users" - все пути в этом роутере будут начинаться с /api/users
# tags=["users"] - для группировки в документации Swagger/OpenAPI
router = APIRouter(prefix="/api/users", tags=["users"])

# Эндпоинт для получения информации о текущем авторизованном пользователе
# response_model=UserResponse - указывает формат ответа (Pydantic модель)
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """
    Получает информацию о текущем авторизованном пользователе.
    
    Параметры:
    - current_user: словарь с данными пользователя, полученный через зависимость get_current_active_user
    
    Возвращает:
    - Объект пользователя в формате UserResponse
    """
    # Создание асинхронной сессии для работы с БД
    async with async_session() as session:
        # Выполнение запроса к БД для поиска пользователя по username
        result = await session.execute(
            select(DBUser).where(DBUser.username == current_user["username"])
        )
        # Получение первого результата (так как username уникален)
        user = result.scalars().first()
        return user

# Эндпоинт для обновления информации о текущем пользователе
# response_model=UserResponse - указывает формат ответа
@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserUpdate,  # Данные для обновления (Pydantic модель)
    current_user: dict = Depends(get_current_active_user)  # Текущий пользователь
):
    """
    Обновляет информацию о текущем авторизованном пользователе.
    
    Параметры:
    - user_data: данные для обновления (email и/или password)
    - current_user: текущий авторизованный пользователь
    
    Возвращает:
    - Обновленный объект пользователя в формате UserResponse
    """
    async with async_session() as session:
        # Поиск пользователя в БД по username
        result = await session.execute(
            select(DBUser).where(DBUser.username == current_user["username"])
        )
        user = result.scalars().first()
        
        # Обновление email, если он предоставлен в user_data
        if user_data.email:
            user.email = user_data.email
        
        # Обновление пароля, если он предоставлен в user_data
        # Пароль хешируется перед сохранением в БД
        if user_data.password:
            user.hashed_password = pwd_context.hash(user_data.password)
        
        # Фиксация изменений в БД
        await session.commit()
        # Обновление объекта пользователя из БД (чтобы получить актуальные данные)
        await session.refresh(user)
        return user
    

@router.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "OK", "database": "connected"}