#!/bin/sh
ROOT_DIR=~/dataware.energy
PKG_DIR=$ROOT_DIR/pkg/package_files
cd $ROOT_DIR/src
rm -rf deb_dist
python setup.py --command-packages=stdeb.command sdist_dsc
cd deb_dist/dataware-energy-0.1/debian
cp $PKG_DIR/control ./
cp $PKG_DIR/config ./
cp $PKG_DIR/postinst ./
cp $PKG_DIR/rules ./
cp $PKG_DIR/dirs ./
cd ..
cp $PKG_DIR/mysql.sql ./
dpkg-buildpackage -rfakeroot -uc -us
cd debian/dataware-energy
mkdir -p var/dataware/
mkdir -p etc/dataware
mkdir -p var/log/dataware
chmod -R 777 var/log/dataware
mv ../../dataware/static ./var/dataware
mv ../../dataware/views  ./var/dataware
mv ../../dataware/config.cfg ./etc/dataware/sample_config.cfg
cd ..
dpkg --build dataware-energy dataware-energy.deb
cp dataware-energy.deb $ROOT_DIR 
