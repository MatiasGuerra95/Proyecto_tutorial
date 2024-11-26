FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY ./static ./static
COPY ./templates ./templates
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]