#!/usr/bin/env bash

#Fetch the output file generated after running Erik's program.
#The first line in that file will be binary and unable to parse, 
#but it will always be the same so it will be replaced with what 
#it is supposed to say.
output_path="../../java-alias-agent/agent/output"
cp $output_path ./output
sed -i -e '1 d' -e '2 i 4 <clinit> - sun/launcher/LauncherHelper' output
