FROM python:3.12

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y netcat-openbsd


WORKDIR /predine_backend


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
