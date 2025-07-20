

Для первого запуска:

bash
# 1. Инициализация сертификатов (выполнить один раз)
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d yourdomain.com

# 2. Запуск сервисов
docker-compose up -d


===== Запустите проект:

cmd
docker-compose up -d --build
Откройте в браузере:

Панели для разных ролей:

Сайт открывается: http://localhost:8080/




API документация: http://localhost:8000/api/docs

http://localhost:8000/api/redoc


🛠 Инструкции по работе
🔄 Пересборка проекта
При изменениях в коде:

cmd
docker-compose up -d --build
⏹ Остановка контейнеров
cmd
docker-compose down
🗑 Удаление с очисткой данных (включая БД):
cmd
docker-compose down -v
🔍 Просмотр логов
Для бэкенда:

cmd
docker-compose logs -f backend
Для Nginx:

cmd
docker-compose logs -f nginx
Для PostgreSQL:

cmd
docker-compose logs -f db
🧹 Очистка Docker
Удаление всех неиспользуемых ресурсов:

cmd
docker system prune -a
🧩 Структура проекта
text
fastapi_project/
├── backend/          # FastAPI приложение
├── frontend/         # Статические файлы фронтенда
├── nginx/            # Конфигурация Nginx
├── docker-compose.yml # Конфигурация Docker
└── README.md         # Этот файл
🛑 Решение проблем
Порт уже занят:

Найдите процесс: netstat -ano | findstr :80

Завершите: taskkill /PID <PID> /F

Ошибки с БД:

Полностью пересоберите: docker-compose down -v && docker-compose up -d --build

Docker не запускается:

Перезапустите Docker Desktop

Проверьте что Hyper-V включен в BIOS

🏗 Миграции базы данных
Подключитесь к контейнеру с БД:

cmd
docker exec -it fastapi_db psql -U fastapi -d fastapi_db
Основные команды PostgreSQL:

sql
-- Показать таблицы
\dt

-- Показать содержимое таблицы
SELECT * FROM users;

-- Выйти
\q
🔧 Дополнительные команды
Пересоздать конкретный сервис:

cmd
docker-compose up -d --no-deps --build <service_name>
Просмотр работающих контейнеров:

cmd
docker ps
Зайти внутрь контейнера (например, бэкенда):

cmd
docker exec -it fastapi_backend bash
🌐 Доступные endpoints
GET /api/users/ - список пользователей

POST /api/users/ - создать пользователя

GET /api/feedback/ - список отзывов

POST /api/feedback/ - создать отзыв

/api/docs - Swagger документация

💡 Советы по разработке
Для горячей перезагрузки FastAPI (при локальной разработке):

cmd
docker-compose -f docker-compose.dev.yml up
(требуется дополнительный конфиг)

Для дебага используйте:

cmd
docker-compose logs -f
После изменений во фронтенде очистите кеш браузера (Ctrl+F5)




=================================================================
Вот дополнительный раздел для README.md с подробной последовательностью команд для отладки в Windows:

markdown
## 🐞 Пошаговая отладка проекта

### 1. Первый запуск и проверка
```cmd
:: 1. Сборка и запуск
docker-compose up -d --build

:: 2. Проверить состояние контейнеров
docker ps -a

:: 3. Проверить логи инициализации
docker-compose logs --tail=50


##           2. Если контейнеры не запускаются
cmd
:: 1. Проверить конкретный сервис (например, backend)
docker-compose logs backend

:: 2. Попробовать запустить сервис отдельно
docker-compose up -d --no-deps --build backend

:: 3. Проверить подключение к БД
docker exec -it fastapi_db psql -U fastapi -c "\conninfo"


##       3. Отладка API
cmd
:: 1. Проверить доступность API
curl -X GET http://localhost/api/users/

:: 2. Тестовый POST-запрос
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"test\",\"user_info\":\"test\"}" http://localhost/api/users/

:: 3. Проверить данные в БД
docker exec -it fastapi_db psql -U fastapi -d fastapi_db -c "SELECT * FROM users;"


##     4. Отладка фронтенда
cmd
:: 1. Проверить статические файлы в Nginx
docker exec -it fastapi_nginx ls -la /usr/share/nginx/html

:: 2. Проверить ошибки в консоли браузера
:: (F12 → Console в браузере)

:: 3. Проверить сетевые запросы
:: (F12 → Network в браузере)


##      5. Полная пересборка
cmd
:: 1. Остановить и удалить всё
docker-compose down -v

:: 2. Очистить старые образы
docker system prune -a

:: 3. Пересобрать с нуля
docker-compose up -d --build

:: 4. Проверить миграции БД
docker exec -it fastapi_db psql -U fastapi -d fastapi_db -c "\dt"


##      6. Частые проблемы и решения
Проблема: БД не принимает подключения
Решение:

cmd
docker-compose restart db
docker-compose logs db --tail=100
Проблема: Nginx возвращает 502 Bad Gateway
Решение:


cmd
:: 1. Очистить кеш Nginx
docker exec -it fastapi_nginx nginx -s reload

:: 2. Удалить статику из контейнера
docker exec -it fastapi_nginx rm -rf /usr/share/nginx/html/*
Проблема: Ошибки миграций БД
Решение:

cmd
:: 1. Сбросить БД полностью
docker-compose down -v
docker-compose up -d db

:: 2. Перезапустить миграции
docker-compose run --rm backend alembic upgrade head


##    7. Полезные команды для мониторинга
cmd
:: Показать использование ресурсов
docker stats

:: Проверить сетевые подключения
docker network inspect fastapi_fastapi_network

:: Проверить логи в реальном времени
docker-compose logs -f --tail=100


##          8. Запуск в режиме разработки
Создайте файл docker-compose.override.yml:

yaml
version: '3.8'

services:
  backend:
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Запустите:

cmd
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
text

Этот раздел добавляет в ваш README.md подробные инструкции для:
1. Поэтапного запуска и проверки
2. Диагностики распространенных проблем
3. Команды для мониторинга работы системы
4. Специальный режим для разработки с hot-reload

Все команды адаптированы для Windows CMD и PowerShell. Для каждого сценария приведены:
- Диагностические команды
- Команды для исправления проблем
- Альтернативные варианты решения