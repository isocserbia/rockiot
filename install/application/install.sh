#!/bin/bash

apt-get update
apt-get install -y curl unzip git
apt-get install -y docker.io

chown ubuntu:docker /var/run/docker.sock
usermod -aG docker ubuntu

systemctl start docker

curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

source ../certs.sh

chmod 766 /home/ubuntu/docker/certificates/*
