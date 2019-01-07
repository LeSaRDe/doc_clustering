#!/bin/bash

for file in `find /home/fcmeng/PycharmProjects/stanford/stanford-corenlp-full-2018-10-05  -name "*.jar"`; do export CLASSPATH="$CLASSPATH:`realpath $file`"; done 
