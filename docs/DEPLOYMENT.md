Deployment guide
===

Deployment is currently performed using docker and docker-compose. Compose files are available for several environments, and they all have respective `.env` configuration files.

# Available services

Depending on environment, available services are:

#### Base
- Rabbit MQ
- RockIOT APP
- RockIOT Worker
- RockIOT Beat
- RockIOT Listener
- RockIOT Ingest
  
#### Dev
- `(All Base)`
- Timescale DB
- RockIOT Analysis
- RockIOT Monitor
- RockIOT Demo
- PG Admin
- Prometheus
- Loki
- Promtail
- Grafana

#### AWS
- `(All Base)`
- Timescale DB
- RockIOT Demo
- PG Admin

#### Prod
- `(All Base)`
- Timescale DB is expected to be running on dedicated DB server


# Environment setup

Example configuration files `.env.example` are located in the root folder of this project. Those should be copied for each environment and kept secret. 

#### Dev
- db.env
- django.env

#### AWS
- db.env
- django.env
- rockiot.aws.env

#### Prod
- db.prod.env
- django.env
- rockiot.prod.env

# Application start

Application is started by running base compose file and supplying appropriate compose override file.

#### Dev
```
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

#### AWS
```
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d
```

#### Prod
```
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```