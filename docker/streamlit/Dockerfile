FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# system deps for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# install poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# copy only pyproject first for layer caching
COPY pyproject.toml poetry.lock* /app/

# configure poetry to not create virtualenv (install into container env)
RUN poetry config experimental.new-installer false || true
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# copy app code
COPY . /app

EXPOSE 8501

CMD ["poetry", "run", "streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
