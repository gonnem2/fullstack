from python:3.13-slim

WORKDIR /src
RUN pip install uv


COPY ./app ./app
COPY pyproject.toml uv.lock ./


RUN uv sync --frozen


COPY alembic.ini /src/

