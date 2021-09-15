
# RockIOT platform

Data ingest platform for IOT devices with analytics capabilities for Scientific institutions.

---
## Docs
[Development setup](./docs/DEVELOPMENT.md)

---
## Run

Example configuration is avaiable in `.env` files. Copy them and rename, or introduce new environment profiles.

### Local profile

Run complete platform or separate services py adding service name at the end:
```
docker compose up
```
or
```
docker compose up rockiot_demo
```

### AWS profile

For AWS profile there are separate compose and `.env` files.
```
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d
```
or
```
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d rockiot_demo
```