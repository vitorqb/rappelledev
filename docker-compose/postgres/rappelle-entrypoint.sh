#!/bin/bash

# Setup the second db if needed
if ! [ -z "$POSTGRES_DB_2" ]
then
    echo "CREATE DATABASE \"$POSTGRES_DB_2\";" >/docker-entrypoint-initdb.d/test-db.sql
fi

# First, run the common setup form the dockerimage
/usr/local/bin/docker-entrypoint.sh "$@"
