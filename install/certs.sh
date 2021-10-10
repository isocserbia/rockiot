#!/bin/bash

if [[ ! -d ~/docker/certificates ]]; then
  echo 'Created certificates folder'
  mkdir -p ~/docker/certificates
fi

if [[ ! -f ~/docker/certificates/ca_certificate.pem ]];
then
  echo ''
  echo 'Generating new certificates ...'
  if [[ ! -d tls-gen ]]; then
    git clone https://github.com/michaelklishin/tls-gen tls-gen
  fi
  cd tls-gen/basic
  python3 profile.py generate --common-name rockiot.io --client-alt-name rockiot.io --server-alt-name rockiot.io --days-of-validity 3650 --key-bits 2048
  python3 profile.py verify
  cp result/* ~/docker/certificates/
  cd ../..
  rm -fR tls-gen
  cd ~/docker/certificates/
  cat server_certificate.pem server_key.pem > certificate.pem
  chmod 755 *
  echo 'New certificates generated and verified [~/docker/certificates]'
  echo ''
else
  echo 'Using existing certificates'
  echo ''
fi
