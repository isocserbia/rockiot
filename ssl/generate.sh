#!/bin/sh

openssl req -new -newkey rsa:4096 -nodes -keyout decazavazduh.key -out decazavazduh.csr

# Country Name                RS
# State or Province Name      Beogradski okrug
# Locality Name               Beograd
# Organization Name           Internet drustvo Srbije (ISOC)
# Organizational Unit Name    Deca za vazduh
# Common Name                 *.decazavazduh.rs
# Email Address               secretariat@isoc.rs
# A challenge password        af5Vvn2etXhxpTTQmPBJ
