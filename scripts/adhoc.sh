#!/bin/env bash

set -euo pipefail

command -v curl >/dev/null 2>&1 || { echo 'You need curl to use this.'; exit 1; }
command -v jq >/dev/null 2>&1 || { echo 'You need jq to use this.'; exit 1; }

BASE_URL='http://localhost:9999'


_exit_on_curl7() {
    [ "$?" -eq 7 ] \
        && echo "No server listening on ${BASE_URL}." 1>&2 \
        && exit
}


_make_json() {
    IFS=','
    local fields=($1)
    [ "${#fields[@]}" -lt 3 ] \
        && echo 'You must provide at least 3 fields.' 1>&2\
        && exit 1

    local nickname="${fields[0]}"
    local fullname="${fields[1]}"
    local dob="${fields[2]}"
    local stack="${fields[@]:3}"

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

    unset IFS
    echo "$json"
}


_post_to_get() {
    local json && read json

    local loc
    loc=$(
        curl "${BASE_URL}/users" -s \
            -D '%' \
            -X 'POST' \
            -H 'Content-Type: application/json' \
            -d "$json" \
            -o >(jq --indent 4) \
            -w '%header{Location}'
    ) || _exit_on_curl7

    [ -n "$loc" ] \
        && curl "${BASE_URL}${loc}" -s \
            -D '%' \
            -X 'GET' \
            -H 'Accept: application/json' \
        | jq --indent 4
}


_post() {
    local json && read json
    curl "${BASE_URL}/users" -s \
        -D '%' \
        -X 'POST' \
        -H 'Content-Type: application/json' \
        -d "$json" \
    | jq --indent 4 \
    || _exit_on_curl7
}


get_user() {
    curl "${BASE_URL}/users/${1}" -s \
        -D '%' \
        -X 'GET' \
        -H 'Accept: application/json' \
    | jq --indent 4 \
    || _exit_on_curl7
}


count_users() {
    curl "${BASE_URL}/users-count" -s \
        -D '%' \
        -X 'GET' \
    | jq --indent 4 \
    || _exit_on_curl7
}


search_users() {
    curl "${BASE_URL}/users" -s \
        -D '%' \
        -X 'GET' \
        --url-query "q=${1}"  \
    | jq --indent 4 \
    || _exit_on_curl7
}


print_usage() {
    cat <<END 1>&2

Usage: $0 ( -n | -N ) <FIELDS>
       $0 -g <UUID>
       $0 -s <QUERY-TERM>
       $0 -c
       $0 -h

Run \`$0 -h\` for further detail.

END
}


print_help() {
    cat <<'END' 1>&2

TL;DR: curl's output piped to jq.

Usage: adhoc.sh ( -n | -N ) <FIELDS>
       adhoc.sh -g <UUID>
       adhoc.sh -s <QUERY-TERM>
       adhoc.sh -c
       adhoc.sh -h

Arguments:

    These are the arguments which should be provided to the script given the
    correct options:

    <FIELDS>:     A comma-separated list of values for "nickname", "fullname",
                  "dob" and "stack", respectively. The values must be given in
                  this exact order, and every value after the 3rd will be
                  considered part of the "stack" array. If the "stack" should be
                  `null` instead, then only 3 values must be given. This argument
                  must be enclosed by quotes.

    <UUID>:       Any valid UUID.

    <QUERY-TERM>: The string which will be processed by the API's search
                  functionality. This argument must be encolosed by quotes.

    Note that this script itself doesn't try to validate anything according to
    the specifications of the challenge. The descriptions for the arguments
    listed above consist solely on what they SHOULD be, but as long as the script
    can properly parse them to assemble a valid curl command it is up to the API
    to deal with whatever it recieves.

Options:

    -n <FIELDS>:     Make a POST request on `/users`, sending data in json format
                     whose fields "nickname", "fullname", "dob" and (optionally)
                     "stack" are provided by the <FIELDS> string. With this
                     option a second (GET) request on the endpoint provided by
                     the Location header from the previous response is
                     automatically made to retrieve the newly created resource,
                     but only if said resource was successfully created.

    -N <FIELDS>:     Make a POST request on `/users`, sending data in json format
                     whose fields "nickname", "fullname", "dob" and (optionally)
                     "stack" are provided by the <FIELDS> string. With this
                     option, no subsequent requests are made.

    -g <UUID>:       Make a GET request on `/users/<UUID>`.

    -s <QUERY-TERM>: Make a GET request on `/users?q=<QUERY-TERM>`.

    -c:              Make a GET request on `/users-count`.

    -h:              Display this help message.

END
}


while getopts ':n:N:g:s:ch' opt; do
    case $opt in
        n)
            _make_json "$OPTARG" | _post_to_get
            exit
            ;;
        N)
            _make_json "$OPTARG" | _post
            exit
            ;;
        g)
            get_user "$OPTARG"
            exit
            ;;
        s)
            search_users "$OPTARG"
            exit
            ;;
        c)
            count_users
            exit
            ;;
        h)
            print_help
            exit
            ;;
        :)
            echo -e "\nOption -${OPTARG} requires an argument." 1>&2
            print_usage
            exit 1
            ;;
        ?)
            echo -e "\nOption -${OPTARG} doesn't exist" 1>&2
            print_usage
            exit 1
            ;;
    esac
done

if [ -z "$@" ] || [ "${1:0:1}" != '-' ]; then
     echo -e '\nYou must provide a valid option.'
     print_usage
     exit 1
fi
