from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context
import os
import sys
import asyncio

# Добавляем путь к проекту в PYTHONPATH
sys.path.insert(0, os.getcwd())

# Импортируем Base и настройки
from app.db.database import Base
from app.core.config import settings

# Конфигурация Alembic
config = context.config

# Настройка логгирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные для autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Функция для выполнения миграций в синхронном режиме."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """Асинхронное подключение и выполнение миграций."""
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Запуск асинхронных миграций."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()