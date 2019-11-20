#!/usr/bin/env bash

pip3 install Django==2.1.*
pip3 install psycopg2-binary
pip3 install django-cron
pip3 install -U python-dotenv
pip3 install psutil
pip3 install requests

sudo apt-get install -y cron
cp conf/cron/services.cron /etc/cron.d/
chmod 0644 /etc/cron.d/services.cron
crontab /etc/cron.d/services.cron

#postgres
sudo apt-get update
sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib
sudo -u postgres psql

# CREATE DATABASE postgres;
# CREATE USER postgres WITH PASSWORD '123456';
# ALTER ROLE postgres SET client_encoding TO 'utf8';
# ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
# ALTER ROLE postgres SET timezone TO 'UTC';
# GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;
# \q