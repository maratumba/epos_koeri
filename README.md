# EPOS Koeri Web Services

First time install on a new machine:

You need to supply `config.ini` files for tornado 
containers `tornado_radon` and `tornado_seis` in 
their respective directories. You also need a 
`docker-compose.yml` in the base directory in 
order to use `docker-compose`.

Examples of these files are provided.


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

Run all containers in the base directory:
```bash
docker-compose up -d
```

or use the startup script
```bash
docker_scripts/v3_mysql_docker_start.sh
```

