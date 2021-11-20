FROM python:3.9-slim-buster as base

WORKDIR /app

FROM base as requirements

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM requirements as files
COPY . .


FROM files as dowork
CMD "python3 main.py"