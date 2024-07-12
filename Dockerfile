# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы requirements.txt в рабочую директорию
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем все файлы из текущей директории в рабочую директорию контейнера
COPY . .
EXPOSE 3000
# Указываем команду для запуска Flask-приложения
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:3000", "app:app"]