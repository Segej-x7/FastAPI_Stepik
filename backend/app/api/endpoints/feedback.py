# Импорт необходимых модулей и зависимостей
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from app.api.dependencies import get_current_active_user, role_required, UserRole
from app.db.models import FeedbackCreate, DBFeedback
from app.db.database import async_session

# Создание роутера FastAPI с префиксом '/api/feedback' и тегом 'feedback' для документации
router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Эндпоинт для создания нового отзыва
@router.post("/", response_model=FeedbackCreate)
async def create_feedback(
    feedback: FeedbackCreate,  # Получаем данные отзыва из тела запроса
    current_user: dict = Depends(get_current_active_user)  # Проверяем авторизацию пользователя
):
    async with async_session() as session:  # Открываем асинхронную сессию с БД
        # Создаем новый объект отзыва для базы данных
        db_feedback = DBFeedback(
            name=feedback.name,
            message=feedback.message,
            email=feedback.email,
            phone=feedback.phone
        )
        session.add(db_feedback)  # Добавляем отзыв в сессию
        await session.commit()  # Сохраняем изменения в БД
        await session.refresh(db_feedback)  # Обновляем объект для получения данных из БД (например, ID)
        return feedback  # Возвращаем исходные данные отзыва (без ID)

# Эндпоинт для получения списка всех отзывов
@router.get("/")
async def get_feedbacks(current_user: dict = Depends(get_current_active_user)):
    async with async_session() as session:  # Открываем асинхронную сессию с БД
        # Выполняем запрос на выбор всех записей из таблицы отзывов
        result = await session.execute(select(DBFeedback))
        feedbacks = result.scalars().all()  # Получаем все результаты
        # Преобразуем результаты в список словарей для ответа
        return [
            {
                "id": fb.id,
                "name": fb.name,
                "message": fb.message,
                "email": fb.email,
                "phone": fb.phone
            } for fb in feedbacks
        ]

# Эндпоинт для удаления отзыва по ID
@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,  # ID отзыва из URL пути
    current_user: dict = Depends(get_current_active_user)  # Проверяем авторизацию пользователя
):
    # Проверяем права пользователя - только ADMIN или MODERATOR могут удалять
    if current_user["role"] not in [UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    async with async_session() as session:  # Открываем асинхронную сессию с БД
        # Выполняем запрос на удаление отзыва с указанным ID
        result = await session.execute(
            delete(DBFeedback).where(DBFeedback.id == feedback_id)
        )
        await session.commit()  # Сохраняем изменения в БД
        
        # Проверяем, была ли удалена хотя бы одна запись
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Возвращаем сообщение об успешном удалении
        return {"message": "Feedback deleted successfully"}