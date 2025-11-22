#!/bin/env bash

set -eu
command -v curl >/dev/null 2>&1 || echo 'You need curl to use this.'
command -v jq >/dev/null 2>&1 || echo 'You need jq to use this.'


make_json() {
    local nickname="$1"
    local fullname="$2"
    local dob="$3"
    local stack="${@:4}"

    local json
    if [ -n "$stack" ]; then
        json=$(
            jq -ncM \
                --arg nn "$nickname" \
                --arg fn "$fullname" \
                --arg dt "$dob" \
                '{nickname:$nn,fullname:$fn,dob:$dt,stack:$ARGS.positional}' \
                --args $stack
        )
    else
        json=$(
            jq -ncM \
                --arg nn "$nickname" \
                --arg fn "$fullname" \
                --arg dt "$dob" \
                '{nickname:$nn,fullname:$fn,dob:$dt,stack:null}'
        )
    fi

    echo "$json"
}

curl_post() {
    local json
    read json
    curl -s -D '%' \
        -X 'POST' \
        -H 'Content-Type: application/json' \
        -d "$json" \
        --write-out '%header{Location}\n' \
        'http://localhost:9999/users'
}

curl_get() {
    local url
    read url
    curl -s -D '%' \
        -X 'GET' \
        -H 'Content-Type: application/json' \
        'http://localhost:9999'/"$url"
}

make_json "$@" | curl_post | curl_get | jq --indent 4
