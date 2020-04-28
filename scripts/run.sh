#!/usr/bin/env bash

PYSCRIPT="../analyser/test.py"

if [ "$#" -eq 1 ]; then
    cat $1 | python $PYSCRIPT
elif [ "$#" -ge 2 ] && [ "$2" == "--main" ]; then
    main_start=$(grep -n '4 main -' $1 | cut -f1 -d:)
    main_end=$(grep -n '6 main 0 -' $1 | cut -f1 -d:)
    echo ${main_start}, ${main_end}
    sed -n ${main_start},${main_end}p $1 | python $PYSCRIPT
else
    echo "Usage: $0 <output_file> [--main]"
fi
