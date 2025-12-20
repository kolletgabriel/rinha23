FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app .
CMD ["gunicorn", "--forwarded-allow-ips", "-b", "0.0.0.0:8000", "main:app"]
