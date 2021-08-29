FROM python:3.7-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update
RUN apk add --no-cache --virtual .build-deps-testing \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        gdal-dev \
        geos-dev
RUN apk add --no-cache geos proj gdal binutils
RUN apk add postgresql-libs
RUN apk add gcc musl-dev postgresql-dev python3-dev

COPY . /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait.sh
ADD start.sh /start.sh

RUN chmod +x /wait.sh
RUN chmod +x /start.sh

CMD /wait.sh && /start.sh