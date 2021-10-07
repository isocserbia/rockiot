#!/bin/bash

cp ./docker-compose@.service /etc/systemd/system/
systemctl enable docker-compose@rockiot_project
systemctl start docker-compose@rockiot_project