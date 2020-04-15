#!/bin/bash

# Change accordingly, anaconda bin folder 
PATH="/path/to/anaconda3/bin:$PATH"

# Change accordingly, network code/folder
declare NETWORK="FN"

run_check () {
    echo $(ps x \
    | grep "polyfemos-readconf conf/back/$NETWORK/driving_instructions.conf" \
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
    polyfemos-readconf conf/back/$NETWORK/driving_instructions.conf \
    >> ~/polyfemos/logs/back/$NETWORK/daily_logs/$today.log
fi

echo "$starttime $SECONDS $msg" \
>> ~/polyfemos_logs/back/$NETWORK/start_and_execution_times.log