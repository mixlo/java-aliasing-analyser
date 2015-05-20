#!/usr/bin/env bash

if [ "$#" -eq 1 ]; then
    cat $1 | python ../python/analyser/main.py
elif [ "$#" -eq 2 ] && [ "$2" == "--main" ]; then
    mainStart=$(grep -n '4 main -' $1 | cut -f1 -d:)
    mainEnd=$(grep -n '6 main 0 -' $1 | cut -f1 -d:)
    echo ${mainStart}, ${mainEnd}
    sed -n ${mainStart},${mainEnd}p $1 | python ../python/analyser/main.py
else
    echo "Usage: $0 <output_file> [--main]"
fi
