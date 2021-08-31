FROM python:3.7-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /
COPY certs /certs

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait.sh
RUN chmod +x /wait.sh
RUN chmod +x /start.sh

CMD /wait.sh && /start.sh
