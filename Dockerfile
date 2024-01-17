FROM python:3.12-slim

WORKDIR /app

RUN apt update


COPY requirements.txt /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /app

CMD ["python3", "app/app.py"]

