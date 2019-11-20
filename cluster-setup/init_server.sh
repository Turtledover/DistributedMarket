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