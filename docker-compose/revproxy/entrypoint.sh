#!/bin/bash

RAPPELLE_BE_URL=http://rappelle-be:8000
RAPPELLE_WEB_URL=http://rappelle-web:8000
PORT=80

# Argsparse
SHORT='b:w:p:'
LONG='be-url:,web-url:,port:'
OPTS="$(getopt --options $SHORT --long $LONG --name "$0" -- "$@")"
! [ "$?" = 0 ] && echo "$USAGE" 1>&2 && exit 1
eval set -- "$OPTS"

# Parses params
while [[ "$#" -gt 0 ]]
do
    case "$1" in
        -b|--be-url)
            RAPPELLE_BE_URL="$2"
            shift
            shift
            ;;
        -w|--web-url)
            RAPPELLE_WEB_URL="$2"
            shift
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift
            shift
            ;;
        --)
            # Leave args for nginx entrypoint
            shift
            break
            ;;
        *)
            { echo "UNEXPECTED ARGUMENT: $1" ; echo "$USAGE" ; } 1>&2
            exit 1
    esac
done

# Update config file setting those variables
cmd=( sed -i /etc/nginx/nginx.conf -e "s|__RAPPELLE_BE_URL__|$RAPPELLE_BE_URL|" )
echo "Running: ${cmd[@]}"
"${cmd[@]}"

cmd=( sed -i /etc/nginx/nginx.conf -e "s|__RAPPELLE_WEB_URL__|$RAPPELLE_WEB_URL|" )
echo "Running: ${cmd[@]}"
"${cmd[@]}"

cmd=( sed -i /etc/nginx/nginx.conf -e "s|__PORT__|$PORT|" )
echo "Running: ${cmd[@]}"
"${cmd[@]}"

# Normal entrypoint
cmd=( /docker-entrypoint.sh )
cmd+=( "$@" )
echo "Running: ${cmd[@]}"
"${cmd[@]}"
