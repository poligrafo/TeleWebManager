FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root

COPY . .

RUN mkdir -p /app/logs/bots

CMD ["poetry", "run", "python", "bots/production_bot/bot.py"]
