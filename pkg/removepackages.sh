#!/bin/sh
apt-get remove --purge dataware-energy dataware-resource
apt-get remove --purge dbconfig-common mysql-common mysql-server-5.1 mysql-client-5.1 mysql-server-core-5.1
rm -rf /usr/share/pyshared/dataware
rm -rf /etc/dataware
rm -rf /etc/mysql
rm -rf /var/lib/mysql
rm -rf /etc/dbconfig-common
rm -rf /usr/share/dbconfig-common
apt-get autoremove
