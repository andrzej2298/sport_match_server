FROM python:3.8.1-slim
RUN apt update && apt install curl ngrep gdal-bin -y
WORKDIR /app
COPY requirements/base.txt /app/requirements/base.txt
RUN pip install -r requirements/base.txt
COPY . /app
