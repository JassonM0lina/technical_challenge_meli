FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENV FLASK_APP=app.py
CMD ["flask", "--app", "app.py", "run", "--host=0.0.0.0", "--port=5000"]
