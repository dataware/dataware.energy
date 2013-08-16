#!/bin/sh
INSTALL_DIR="pathtorepo/dataware.energy/monitor/currentcost/bin"
cd $INSTALL_DIR 
java -classpath .:../libs/mysql-connector-java-5.1.26-bin.jar:../libs/RXTXcomm.jar uk/ac/nott/cs/txl/energy/Monitor $1 & 
echo -n $! " " >> /var/run/energymonitor.pid
