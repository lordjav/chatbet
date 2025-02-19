FROM python:3.12.3

WORKDIR /app

COPY requirements.txt .
COPY . /app/
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]