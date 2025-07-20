# Импорт необходимых модулей и классов
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.db.models import UserRole
from typing import Optional

# Создание экземпляра OAuth2PasswordBearer для обработки токенов
# tokenUrl указывает endpoint, где клиенты могут получать токены
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Асинхронная функция для получения текущего пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Создаем исключение для случаев, когда учетные данные недействительны
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем JWT токен с использованием секретного ключа и алгоритма из настроек
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Извлекаем имя пользователя (sub - стандартное поле в JWT для subject)
        username: str = payload.get("sub")
        # Извлекаем роль пользователя из payload
        role: str = payload.get("role")
        # Если имя пользователя или роль отсутствуют, вызываем исключение
        if username is None or role is None:
            raise credentials_exception
        # Возвращаем словарь с именем пользователя и его ролью (преобразованной в UserRole)
        return {"username": username, "role": UserRole(role)}  # Используем UserRole
    except JWTError:
        # Если возникает ошибка JWT (например, токен недействителен), вызываем исключение
        raise credentials_exception

# Функция для получения текущего активного пользователя
def get_current_active_user(current_user: dict = Depends(get_current_user)):
    # Здесь можно добавить дополнительную проверку активности пользователя
    # Например, проверку, что пользователь не заблокирован
    return current_user

# Функция-декоратор для проверки роли пользователя
def role_required(required_role: UserRole):  # Используем UserRole как тип
    # Вложенная функция, которая будет выполняться как зависимость
    def role_checker(current_user: dict = Depends(get_current_user)):
        # Проверяем, что роль пользователя соответствует требуемой или это ADMIN
        if current_user["role"] != required_role and current_user["role"] != UserRole.ADMIN:
            # Если проверка не пройдена, вызываем исключение о недостатке прав
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker