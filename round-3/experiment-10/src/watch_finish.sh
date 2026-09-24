#!/usr/bin/env bash
# Run the final analysis chain as soon as generation + judging are complete.
cd "$(dirname "$0")"
while [ ! -f results/GEN_DONE ]; do sleep 20; done
bash finish.sh
