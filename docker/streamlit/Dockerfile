FROM python:3.10-slim

WORKDIR /app

# Copy only dependency manifests first
COPY pyproject.toml poetry.lock* /app/


# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy rest of your code
COPY . /app

EXPOSE 8501
CMD ["poetry", "run", "streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
