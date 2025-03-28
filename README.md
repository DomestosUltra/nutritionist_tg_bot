# Nutritionist Telegram Bot 🤖🍏

Телеграм-бот для персональных рекомендаций по питанию с использованием AI-моделей (ChatGPT/YandexGPT).

## Особенности
- 🚀 Выбор между ChatGPT и YandexGPT
- ⏱ Rate-limiting (ограничение запросов)
- 🔒 Кеширование в Redis
- 🐇 Асинхронная обработка через RabbitMQ
- 📊 Логирование взаимодействий
- 🐳 Полная Docker-поддержка

## Технологии
- Python 3.11 + FastAPI
- AIogram 3.x
- Redis + RabbitMQ
- Docker Compose
- Poetry

## Быстрый старт

### Требования
- Docker + Docker Compose
- Python 3.11+
- Telegram бот ([инструкция](https://core.telegram.org/bots#how-do-i-create-a-bot))

### Установка
1. Клонировать репозиторий:
```bash
git clone https://github.com/yourusername/nutritionist_tg_bot.git
cd nutritionist_tg_bot
```

2. Настройка окружения:
```bash
cp .env.example .env
```
Заполнить значения в `.env` (см. раздел "Конфигурация")

3. Запуск:
```bash
task build-up
```

## Конфигурация `.env`
```ini
# Основное
ENVIRONMENT=DEV
APP_PORT=8000

# Telegram
BOT_TOKEN=your_bot_token
TG_WEBHOOK_URL=https://your-domain.com/webhook/telegram/

# AI Провайдеры
OPENAI_API_KEY=sk-xxx
YANDEX_API_KEY=AQVNxxx
YANDEX_FOLDER_ID=b1gxxx

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=password

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
```

## Управление проектом (Taskfile)
| Команда           | Действие                          |
|-------------------|-----------------------------------|
| `task run`        | Запуск в dev-режиме               |
| `task build-up`   | Сборка и запуск контейнеров       |
| `task tests`      | Запуск тестов                     |
| `task format`     | Форматирование кода               |
| `task down`       | Остановка сервисов                |
| `task restart`    | Перезапуск сервисов               |

## Архитектура
```
├── Docker
│   ├── Сервис бота (FastAPI)
│   ├── Redis (кеш/сессии)
│   └── RabbitMQ (очереди задач)
├── AI Модели
│   ├── ChatGPT
│   └── YandexGPT
└── Интеграции
    ├── Telegram Webhooks
    └── Асинхронные workers
```

## Разработка
1. Установить зависимости:
```bash
poetry install
```

2. Форматирование кода:
```bash
task format
```

3. Запуск линтеров:
```bash
task pre-commit
```

## Лицензия
MIT License © 2024 [Ваше имя]
