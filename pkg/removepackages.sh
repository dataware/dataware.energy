#!/bin/sh
apt-get -y remove --purge dataware-energy
apt-get -y remove --purge dbconfig-common mysql-common mysql-server-5.1 mysql-client-5.1 mysql-server-core-5.1
rm -rf /usr/share/pyshared/dataware-energy
rm -rf /etc/dataware/energy_config.cfg
rm -rf /etc/mysql
rm -rf /var/lib/mysql
rm -rf /etc/dbconfig-common
rm -rf /usr/share/dbconfig-common
rm -rf /tmp/dbconfig-generate-include*
rm -rf /var/log/dbconfig-common
apt-get -y --purge autoremove
ucf --purge /etc/dbconfig-common/dataware-energy.conf
ucf --purge /etc/dataware/energy_config.cfg
