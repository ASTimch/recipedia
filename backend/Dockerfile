FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY ./recipedia_backend/. .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "recipedia_backend.wsgi"] 
