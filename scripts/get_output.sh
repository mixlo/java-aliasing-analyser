#!/usr/bin/env bash

#Fetch the output file generated after running Erik's program.
#The first line in that file will be binary and unable to parse, 
#but it will always be the same so it will be replaced with what 
#it is supposed to say.
output_path="../../java-alias-agent/agent/output"
output_file="./output.log"
cp $output_path $output_file
sed -i -e '1 d' -e '2 i 4 <clinit> - sun/launcher/LauncherHelper' $output_file
