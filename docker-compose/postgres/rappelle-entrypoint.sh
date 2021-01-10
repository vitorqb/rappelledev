#!/bin/bash

function msg() { echo -e "\n[rappelle-entrypoint.sh] " "$@" ; }

msg "Starting...."
msg "POSTGRES_DB=$POSTGRES_DB POSTGRES_DB_2=$POSTGRES_DB_2 POSTGRES_USER=$POSTGRES_USER"

# Setup the second db if needed
if ! [ -z "$POSTGRES_DB_2" ]
then
    msg "Adding second database: $POSTGRES_DB_2"
    echo "CREATE DATABASE \"$POSTGRES_DB_2\";" >/docker-entrypoint-initdb.d/test-db.sql
else
    msg "No second db configured"
fi

# First, run the common setup form the dockerimage
/usr/local/bin/docker-entrypoint.sh "$@"
