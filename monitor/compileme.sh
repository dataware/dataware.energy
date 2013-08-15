#!/bin/sh
cd src
javac -classpath .:../libs/RXTXcomm.jar:../libs/jsrpc.jar -d ../bin  uk/ac/nott/cs/txl/energy/Monitor.java
