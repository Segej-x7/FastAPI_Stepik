from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.db.database import init_db as db_init
from app.api.endpoints import auth, users, admin, feedback, health
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔄 Starting application initialization...")
    try:
        logger.info("🛠 Initializing database...")
        await db_init()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    yield
    logger.info("⏹ Application shutdown")

app = FastAPI(
    title="FastAPI with PostgreSQL",
    description="Пример API с PostgreSQL и асинхронными запросами",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем healthcheck первым
app.include_router(health.router, prefix="/api")

# Затем остальные роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(feedback.router)
from app.api.endpoints.moderator import router as moderator_router
app.include_router(moderator_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}