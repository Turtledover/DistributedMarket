#!/bin/bash

/etc/init.d/ssh start
stop-dfs.sh
start-dfs.sh
start-yarn.sh

if [ ! -f /firstlaunch ]; then
    hdfs dfs -mkdir /shared
    hdfs dfs -mkdir /shared/log
    python3 /dmarket/manage.py makemigrations --merge
    python3 /dmarket/manage.py migrate
    touch firstlaunch
fi
$SPARK_HOME/sbin/start-history-server.sh --properties-file $SPARK_HOME/conf/spark-defaults.conf
cron
python3 /dmarket/manage.py runserver 0.0.0.0:8000
python3 /scripts/init_cluster.py
