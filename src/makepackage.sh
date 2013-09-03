#!/bin/sh
cd /home/vagrant/dataware-resource-package/src
sudo rm -rf deb_dist
sudo python setup.py --command-packages=stdeb.command sdist_dsc
cd deb_dist/dataware-resource-0.1/debian
sudo cp /home/vagrant/package_files/control ./
sudo cp /home/vagrant/package_files/config ./
sudo cp /home/vagrant/package_files/postinst ./
sudo cp /home/vagrant/package_files/rules ./
sudo cp /home/vagrant/package_files/dirs ./
cd ..
sudo cp /home/vagrant/package_files/mysql.sql ./
sudo dpkg-buildpackage -rfakeroot -uc -us
cd debian/dataware-resource/
sudo mkdir -p var/dataware/
sudo mkdir -p etc/dataware
sudo mkdir -p var/log/prefstore
sudo chmod -R 777 var/log/prefstore
sudo mv ../../dataware/static ./var/dataware
sudo mv ../../dataware/views  ./var/dataware
sudo mv ../../dataware/config_tom.cfg ./etc/dataware/sample_config.cfg
cd ..
sudo dpkg --build dataware-resource dataware-resource.deb
sudo cp dataware-resource.deb /vagrant

