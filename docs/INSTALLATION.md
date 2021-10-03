Installation guide
===

Installation scripts are placed inside [install](../install) folder.

## Generating certificates

Certificates are used to secure MQTT communication between RabbitMQ and MQTT Clients, such as [Rockiot demo](../rockiot_demo). Certificates can be generated using provided [certs](../install/certs.sh) script:
```shell
chmod +x ./install/certs.sh
./install/certs.sh
```
Output path is mounted as volume to docker containers.

## Installing servers

Currently, two scripts are supported.

#### Single server setup

This option installs required system libraries, docker and docker compose, and generates certificates. All other dependencies are configured and installed using docker images.
```shell
cd ./install/application
chmod +x install.sh
sudo ./install.sh
```

#### Separate database and application server

This option considers dedicated servers for the database and the application. Database is installed with all required extensions, configured automatically, including the database backup.

On database server:
```shell
cd ./install/database
chmod +x install.sh
sudo ./install.sh
```

On application server:
```shell
cd ./install/application
chmod +x install.sh
sudo ./install.sh
```

