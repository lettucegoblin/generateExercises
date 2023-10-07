#!/bin/bash

# Get the process IDs for all processes matching "TheBloke/Wizard-Vicuna"
pids=$(ps -fA | grep "TheBloke/Wizard-Vicuna" | awk '{print $2}')

# Get the last process ID
last_pid=$(echo "$pids" | tail -n 1)

# Kill all processes except the last one
for pid in $pids; do
  if [ "$pid" != "$last_pid" ]; then
    kill "$pid"
  fi
done