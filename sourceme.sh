#!/usr/bin/env bash

export RINHA_BENCHMARKS="$(pwd)/benchmarks"
export RINHA_SCRIPTS="$(pwd)/scripts"

chmod +x "${RINHA_SCRIPTS}"/{adhoc.sh,start-benchmark.sh}

alias adhoc="${RINHA_SCRIPTS}/adhoc.sh"
alias bench="${RINHA_SCRIPTS}/start-benchmark.sh"
alias dcu='docker compose --progress quiet up -d'
alias dcd='docker compose --progress quiet down'
