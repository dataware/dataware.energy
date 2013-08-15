#!/bin/sh
INSTALL_DIR="/path/to/repo/monitor/bin"
cd $INSTALL_DIR 
java -classpath .:../libs/RXTXcomm.jar:../libs/jsrpc.jar uk/ac/nott/cs/txl/energy/Monitor $1 & 
echo -n $! " " >> /var/run/energymonitor.pid
