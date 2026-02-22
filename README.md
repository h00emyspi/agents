# Moltbook AI Agent 🤖

Автономный AI-агент для социальной сети [Moltbook](https://www.moltbook.com/) - платформы для AI-агентов.

## Возможности

- 📥 Сбор постов из ленты Moltbook
- ✍️ Автогенерация постов с помощью LLM (OpenAI GPT)
- 💬 Автоматические комментарии к постам
- 👍 Голосование за посты
- 📊 Анализ обратной связи (upvotes/downvotes)
- 🗃️ Локальное хранение данных в SQLite

## Требования

- Python 3.9+
- OpenAI API ключ (для генерации контента)
- Moltbook агент API ключ

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/h00emyspi/agents.git
cd agents
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
copy .env.example .env
# Отредактируйте .env файл, добавив ваши ключи
```

## Настройка .env

```env
MOLTBOOK_SUPABASE_URL=https://ваш_проект.supabase.co
MOLTBOOK_PUBLIC_KEY=sb_publishable_...
MOLTBOOK_AGENT_NAME=ваше_имя_агента
MOLTBOOK_AGENT_API_KEY=ваш_api_ключ_агента
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./moltbook_agent.db
POLL_INTERVAL=300
```

## Получение ключей Moltbook

1. Зарегистрируйтесь на https://www.moltbook.com/
2. Перейдите в раздел для разработчиков
3. Создайте нового агента
4. Получите API ключ агента

## Запуск

```bash
python -m src.main
```

Агент будет запускать цикл каждые 5 минут (настраивается через POLL_INTERVAL).

## Структура проекта

```
moltbook-ai-agent/
├── src/
│   ├── config.py          # Конфигурация
│   ├── db.py              # Работа с БД
│   ├── main.py            # Главный цикл агента
│   ├── moltbook/
│   │   └── client.py      # API клиент Moltbook
│   └── llm/
│       └── generator.py   # Генерация контента LLM
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## Как это работает

1. **Сбор данных** - агент получает последние посты из ленты
2. **Генерация** - LLM создаёт новый контент на основе трендов
3. **Взаимодействие** - агент комментирует и голосует за посты
4. **Обучение** - анализирует feedback (upvotes/downvotes) для улучшения

## Лицензия

MIT
