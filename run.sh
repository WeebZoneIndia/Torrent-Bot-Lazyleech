#!/bin/sh
touch /app/aria2.log /app/lazyleech.log
tail -f /app/aria2.log &
tail -f /app/lazyleech.log &
aria2c --enable-rpc=true -j5 -x5 > /app/aria2.log 2>&1 &
cd /app
python3 -m lazyleech > /app/lazyleech.log 2>&1
