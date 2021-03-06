#!/bin/sh
ROOT_DIR=~/dataware.energy
PKG_DIR=$ROOT_DIR/pkg/package_files
#first build the java monitor code
cd $ROOT_DIR/monitor/currentcost
./compileme.sh
cd $ROOT_DIR/src
rm -rf deb_dist
python setup.py --command-packages=stdeb.command sdist_dsc
cd deb_dist/dataware-energy-0.1/debian
cp $PKG_DIR/control ./
cp $PKG_DIR/config ./
cp $PKG_DIR/postinst ./
cp $PKG_DIR/rules ./
cp $PKG_DIR/dirs ./
cp $PKG_DIR/dataware-energy.init ./
cd ..
cp $PKG_DIR/mysql.sql ./
dpkg-buildpackage -rfakeroot -uc -us
cd debian/dataware-energy
mkdir -p var/dataware-energy
mkdir -p etc/dataware
mkdir -p var/log/dataware
#make the directory for the java monitor code
mkdir -p usr/share/java
#and for the auto start using udev
mkdir -p etc/udev/rules.d
chmod -R 777 var/log/dataware
mv ../../dataware-energy/static ./var/dataware-energy
mv ../../dataware-energy/views  ./var/dataware-energy
cp ../../dataware-energy/__init__.py ./usr/share/pyshared/dataware-energy
cp ../../dataware-energy/config.cfg ./usr/share/pyshared/dataware-energy
cp $ROOT_DIR/monitor/currentcost/bin/currentcost-energy-monitor.jar usr/share/java 
cp $ROOT_DIR/monitor/currentcost/libs/ini4j-0.5.2.jar usr/share/java
cp $ROOT_DIR/monitor/currentcost/01UsbAdded.rules etc/udev/rules.d
cd ..
dpkg --build dataware-energy dataware-energy.deb
cp dataware-energy.deb $ROOT_DIR 
