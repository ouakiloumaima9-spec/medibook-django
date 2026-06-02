FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=100

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --retries 10 --timeout 100 -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "medibook.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--graceful-timeout", "30"]