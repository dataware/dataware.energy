#!/bin/sh
#could do this with ant, but ant tool requires an extra 60 odd Mb which seems overkill..

cd src
javac -classpath .:../libs/ini4j-0.5.2.jar:../libs/RXTXcomm.jar:../libs/mysql-connector-java-5.1.26-bin.jar -d ../bin  uk/ac/nott/cs/txl/energy/Monitor.java
cd ../bin
jar -cf currentcost-energy-monitor.jar uk/ac/nott/cs/txl/energy/Monitor.class 
