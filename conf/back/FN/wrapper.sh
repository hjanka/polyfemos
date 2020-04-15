#!/bin/bash

# Path to anaconda binary, change this if needed
PATH="~/anaconda3/bin:$PATH"


run_check () {
    echo $(ps x \
    | grep "polyfemos-readconf conf/back/FN/driving_instructions.conf" \
    | grep -v -e "grep")
}


SECONDS=0
declare starttime=$(date -u +%Y-%m-%dT%H:%M:%SZ)
declare today=$(date -u +%Y.%j)
declare msg=""

if [[ $(run_check) ]]; then
    msg="call skipped, process already running"
else
    source activate polyfemos_env
    cd ~/polyfemos
    polyfemos-readconf conf/back/FN/driving_instructions.conf \
    >> ~/polyfemos/logs/back/FN/daily_logs/$today.log
fi

echo "$starttime $SECONDS $msg" \
>> ~/polyfemos_logs/back/FN/start_and_execution_times.log