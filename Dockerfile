from python:3.13-slim


WORKDIR /src

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app ./app

COPY alembic.ini /src/

