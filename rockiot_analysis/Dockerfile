FROM aristarhys/luminaire

RUN install_packages postgresql

COPY . /
RUN pip install -r requirements.txt
RUN mkdir -p /data

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait.sh

RUN chmod +x /wait.sh