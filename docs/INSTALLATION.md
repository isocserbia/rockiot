Installation guide
===

Installation scripts are placed Inside `install` folder. Currently, two options are supported.

- Single server setup

This option installs required system libraries, docker and docker compose. All other dependencies are configured and installed using docker images.
```shell
cd ./install/application
chmod +x install.sh
sudo ./install.sh
```

- Separate database and application server

This option considers dedicated servers for database and for the application. Database is installed with all required extensions, configured automatically, including the database backup.

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