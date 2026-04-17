# ==========================================
# Этап 1: Сборка (Builder)
# ==========================================
FROM python:3.13-slim AS builder

# Устанавливаем переменные окружения, чтобы Python не писал .pyc файлы
# и не буферизовал stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Создаем виртуальное окружение
RUN python -m venv /opt/venv

# Обновляем PATH, чтобы все команды использовали venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем только файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости внутрь виртуального окружения
# Параметр --no-cache-dir не обязателен в builder-этапе, но хорош для чистоты
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Этап 2: Финальный образ (Runtime)
# ==========================================
FROM python:3.13-slim AS runtime

# Твики для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Создаем пользователя без прав root для безопасности
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Копируем готовое виртуальное окружение из этапа builder
COPY --from=builder /opt/venv /opt/venv

# Копируем исходный код нашего бота
COPY bot.py .

# Меняем владельца файлов на нашего непривилегированного пользователя
RUN chown -R appuser:appuser /home/appuser/app

# Переключаемся на безопасного пользователя
USER appuser

# Указываем команду для запуска
CMD ["python", "bot.py"]