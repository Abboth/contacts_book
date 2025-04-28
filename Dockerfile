FROM python:3.12

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --only main --no-root

COPY . /app

CMD ["uvicorn", "theregram_proj.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]