# EPOS Koeri Web Services

First time install on a new machine:



```bash
mkdir /opt/local/server/epos && cd /opt/local/server/epos
git clone https://github.com/maratumba/epos_koeri.git
cd tornado_radon
docker build -t base_tornado .
cd ../tornado_vpvs
docker build -t tornado_vpvs .
cd ../mysql_docker
docker build -t mysql_koeri .
```

Run `mysql_koeri` container, source all `.sql`'s 
into the database.  
```bash
docker run -i -t mysql_docker /bin/bash
mysql -p -u root
# enter mysql password
# add radon data 
source mysql_dump/radon_create_db_add_data.sql
```

Run all containers
```bash
docker_scripts/v3_mysql_docker_start.sh
```