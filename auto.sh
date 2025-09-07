#!/bin/bash

for i in $(seq 6 10); do
    echo "Starting in $i..."
    python3 main.py > "Output${i}.txt"
done

echo "Over"
