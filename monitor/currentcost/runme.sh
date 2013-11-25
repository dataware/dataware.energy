#!/bin/sh
INSTALL_DIR="~/dataware.energy/monitor/currentcost/bin"
#cd $INSTALL_DIR 
java -classpath .:../libs/mysql-connector-java-5.1.26-bin.jar:../libs/ini4j-0.5.2.jar:../libs/RXTXcomm.jar uk/ac/nott/cs/txl/energy/Monitor $1 & 
echo -n $! " " >> /var/run/energymonitor.pid
