FROM python:3.11-slim

# Устанавливаем только необходимые зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app

# Открываем порт для HTTP сервера
EXPOSE 8000

# Запускаем бота
CMD ["python", "-m", "app"]
