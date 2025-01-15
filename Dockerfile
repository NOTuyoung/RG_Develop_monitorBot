# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости (предполагается, что у вас есть requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду для запуска
CMD ["python", "main.py"]
