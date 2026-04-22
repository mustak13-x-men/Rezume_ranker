FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m nltk.downloader stopwords

COPY project ./project

RUN mkdir -p /app/data /app/uploads /app/stored_resumes

EXPOSE 5000

CMD ["gunicorn", "--chdir", "project/backend", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
