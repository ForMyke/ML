#!/bin/bash

for i in $(seq 1 5); do
    echo "Starting in $i..."
    python3 main.py > "Output${i}.txt"
done

echo "Over"
