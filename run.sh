#!/bin/bash

# Function to kill all child processes
cleanup() {
    echo "Cleaning up..."
    # Kill all child processes
    pkill -P $$
}

# Trap the EXIT signal to call the cleanup function
trap cleanup EXIT

# Start the subprocesses
python3.10 api-wrapper.py &
npm run chat &

# Wait for all subprocesses to finish
wait