#!/bin/bash

agency_id="KO"
datacenter_id="KO"
organization_string="KO"
enable_database_storage="yes"
# mysql:0 postresql:1 
database_backend="0"
create_database="yes"
mysql_root_password="$MYSQL_ROOT_PASSWORD"
drop_existing_database="no"
database_name="seiscomp3"
database_hostname="mysql_seiscomp"
database_read_write_user="$MYSQL_USER"
database_read_write_passwd="$MYSQL_PASSWORD"
database_public_hostname="localhost"
database_read_only_user="$MYSQL_USER"
database_read_only_password="$MYSQL_PASSWORD"

seiscomp setup<<EOF
$agency_id
$datacenter_id
$organization_string
$enable_database_storage
$database_backend
$create_database
$mysql_root_password
$drop_existing_database
$database_name
$database_hostname
$database_read_write_user
$database_read_write_passwd
$database_public_hostname
$database_read_only_user
$database_read_only_password
P

EOF

cat <<EOF> hede
$agency_id
$datacenter_id
$organization_string
$enable_database_storage
$database_backend
$create_database
$mysql_root_password
$drop_existing_database
$database_name
$database_hostname
$database_read_write_user
$database_read_write_passwd
$database_public_hostname
$database_read_only_user
$database_read_only_password
P

EOF
