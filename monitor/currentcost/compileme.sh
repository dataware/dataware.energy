#!/bin/sh
cd src
javac -classpath .:../libs/RXTXcomm.jar:../libs/mysql-connector-java-5.1.26-bin.jar -d ../bin  uk/ac/nott/cs/txl/energy/Monitor.java
