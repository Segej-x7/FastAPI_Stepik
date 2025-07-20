# Импорт необходимых модулей и зависимостей
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from app.db.database import async_session
from app.db.models import DBUser, UserResponse, UserCreate, UserRole
from app.api.dependencies import role_required
from passlib.context import CryptContext

# Создание роутера для админских эндпоинтов с префиксом /api/admin
router = APIRouter(prefix="/api/admin", tags=["admin"])

# Инициализация контекста для хеширования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Эндпоинт для получения списка всех пользователей
@router.get("/users", response_model=list[UserResponse])
async def get_all_users(_ = Depends(role_required(UserRole.ADMIN))):
    """
    Получение списка всех пользователей.
    Доступно только для пользователей с ролью ADMIN.
    Возвращает список пользователей в формате UserResponse.
    """
    async with async_session() as session:
        # Выполнение SQL-запроса для получения всех пользователей
        result = await session.execute(select(DBUser))
        # Преобразование результата в список объектов и возврат
        return result.scalars().all()

# Эндпоинт для получения конкретного пользователя по ID
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, _ = Depends(role_required(UserRole.ADMIN))):
    """
    Получение информации о конкретном пользователе по его ID.
    Доступно только для пользователей с ролью ADMIN.
    Если пользователь не найден, возвращает 404 ошибку.
    """
    async with async_session() as session:
        # Выполнение SQL-запроса для поиска пользователя по ID
        result = await session.execute(select(DBUser).where(DBUser.id == user_id))
        user = result.scalars().first()
        # Проверка существования пользователя
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

# Эндпоинт для обновления информации о пользователе
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_data: UserCreate,
    _ = Depends(role_required(UserRole.ADMIN))
):
    """
    Обновление информации о пользователе.
    Доступно только для пользователей с ролью ADMIN.
    """
    try:
        async with async_session() as session:
            result = await session.execute(select(DBUser).where(DBUser.id == user_id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Обновляем только переданные поля
            if user_data.username:
                user.username = user_data.username
            if user_data.email:
                user.email = user_data.email
            if user_data.password:
                user.hashed_password = pwd_context.hash(user_data.password)
            if user_data.role:
                user.role = user_data.role
            if hasattr(user_data, 'is_active'):
                user.is_active = user_data.is_active
            
            await session.commit()
            await session.refresh(user)
            return user
            
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Update failed: {str(e)}"
        )

# Эндпоинт для удаления пользователя
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, _ = Depends(role_required(UserRole.ADMIN))):
    """
    Удаление пользователя по ID.
    Доступно только для пользователей с ролью ADMIN.
    Если пользователь не найден, возвращает 404 ошибку.
    При успешном удалении возвращает сообщение об успехе.
    """
    async with async_session() as session:
        # Поиск пользователя для удаления
        result = await session.execute(select(DBUser).where(DBUser.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Удаление пользователя и сохранение изменений
        await session.delete(user)
        await session.commit()
        return {"message": "User deleted successfully"}