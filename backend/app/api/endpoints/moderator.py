# Импорт необходимых модулей и зависимостей
from fastapi import APIRouter, Depends
from app.api.dependencies import role_required, UserRole
from app.db.database import async_session
from app.db.models import DBFeedback
from sqlalchemy import select

# Создание роутера для модераторских эндпоинтов
# prefix="/api/moderator" - все пути в этом роутере будут начинаться с /api/moderator
# tags=["moderator"] - для группировки в документации Swagger/OpenAPI
router = APIRouter(prefix="/api/moderator", tags=["moderator"])

# Тестовый эндпоинт для проверки работы модераторского раздела
@router.get("/test")
async def test_endpoint():
    # Просто возвращает JSON-ответ, подтверждающий что эндпоинт работает
    return {"message": "Moderator endpoint works"}

# Эндпоинт для получения всех отзывов (доступен только модераторам)
@router.get("/feedbacks")
async def get_all_feedbacks(_ = Depends(role_required(UserRole.MODERATOR))):
    """
    Получает список всех отзывов из базы данных.
    Доступ разрешен только пользователям с ролью MODERATOR.
    Зависимость role_required проверяет права доступа.
    """
    
    # Создание асинхронной сессии для работы с базой данных
    async with async_session() as session:
        # Выполнение SQL-запроса для выборки всех записей из таблицы отзывов
        result = await session.execute(select(DBFeedback))
        
        # Преобразование результата в список объектов Python
        feedbacks = result.scalars().all()
        
        # Преобразование каждого объекта отзыва в словарь и возврат списка таких словарей
        return [
            {
                "id": fb.id,           # ID отзыва
                "name": fb.name,       # Имя отправителя
                "message": fb.message,  # Текст отзыва
                "email": fb.email,      # Email отправителя
                "phone": fb.phone       # Телефон отправителя
            } for fb in feedbacks       # Генератор списка для всех отзывов
        ]