#!/bin/sh

# Step 1
# Generate CSR and submit to register

mkdir -p ./keys ./certs
openssl req -new -newkey rsa:4096 -nodes -keyout ./keys/decazavazduh.key -out decazavazduh.csr

# Country Name                RS
# State or Province Name      Beogradski okrug
# Locality Name               Beograd
# Organization Name           Internet drustvo Srbije (ISOC)
# Organizational Unit Name    Deca za vazduh
# Common Name                 *.decazavazduh.rs
# Email Address               secretariat@isoc.rs
# A challenge password        af5Vvn2etXhxpTTQmPBJ

# Step 2
# Download ca-bundle and public key from register

# Step 3
# Append "STAR_decazavazduh_rs.crt" to "My_CA_Bundle.ca-bundle" and rename to "./certs/fullchain.pem"

# Step 4
# Save "STAR_decazavazduh_rs.crt" as "./certs/decazavazduh.crt"

# Step 5
# Distribute ./keys and ./certs to other locations in the repository

rsync -rP ./certs/ ../docker/nginx/ssl/certs/ --delete-after
rsync -rP ./keys/ ../docker/nginx/ssl/keys/ --delete-after
