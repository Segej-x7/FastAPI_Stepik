# Импорт необходимых модулей из SQLAlchemy для асинхронной работы
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
import logging
from contextlib import asynccontextmanager

# Инициализация логгера для текущего модуля
logger = logging.getLogger(__name__)

# Инициализация подключения к базе данных
# URL подключения к PostgreSQL с использованием asyncpg драйвера

from app.core.config import Settings

settings = Settings()
DATABASE_URL = settings.DATABASE_URL

# Создание асинхронного движка SQLAlchemy
# echo=True включает логирование SQL-запросов (полезно для отладки)
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики сессий для работы с БД
# expire_on_commit=False - объекты не будут терять свои атрибуты после коммита
# class_=AsyncSession указывает, что нужно использовать асинхронные сессии
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

async def init_db():
    """
    Асинхронная функция для инициализации базы данных.
    Создает все таблицы, определенные в моделях, и проверяет их существование.
    """
    try:
        # Создаем соединение с БД и начинаем транзакцию
        async with engine.begin() as conn:
            # Синхронный вызов для создания всех таблиц из метаданных Base
            # run_sync используется для вызова синхронного кода в асинхронном контексте
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Таблицы успешно созданы")
            
            # Проверка существования конкретной таблицы 'users'
            # Выполняем SQL-запрос для проверки регистрации таблицы в PostgreSQL
            result = await conn.execute(text("SELECT to_regclass('public.users')"))
            
            # Если таблица существует (result.scalar() возвращает не None)
            if result.scalar():
                logger.info("✔ Таблица 'users' существует")
            else:
                logger.error("❌ Таблица 'users' не создана")
                
    except Exception as e:
        # Логируем любые ошибки, возникающие при инициализации БД
        logger.error(f"❌ Ошибка при инициализации БД: {e}")
        raise  # Пробрасываем исключение дальше

@asynccontextmanager
async def get_db():
    """
    Асинхронный контекстный менеджер для работы с сессией БД.
    Обеспечивает автоматическое управление сессией (коммит/ролбэк) и ее закрытие.
    """
    # Создаем новую сессию
    async with async_session() as session:
        try:
            # Возвращаем сессию вызывающему коду
            yield session
            # Если исключений не было, коммитим транзакцию
            await session.commit()
        except Exception:
            # При возникновении исключения откатываем транзакцию
            await session.rollback()
            raise  # Пробрасываем исключение дальше