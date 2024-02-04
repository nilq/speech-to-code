FROM python:3.11-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

ENV PATH /root/.local/bin:$PATH
RUN python3.11 -m venv .venv/ \
    && poetry install --no-interaction --no-ansi --no-root

EXPOSE 8000

ENV PORT 8000

CMD ["poetry", "run", "start"]
