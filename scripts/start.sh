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
    mkdir /dmarket/medias
    cp /root/.ssh/id_rsa.pub /dmarket/medias/
    python3 /dmarket/manage.py init_dmarket -email admin@admin.com -password 1234
    rm /dmarket/medias/id_rsa.pub
    touch firstlaunch
fi
$SPARK_HOME/sbin/start-history-server.sh --properties-file $SPARK_HOME/conf/spark-defaults.conf
cron
python3 /dmarket/manage.py runserver 0.0.0.0:8000
# sleep 5
# python3 /scripts/init_cluster.py
# tail -f /dev/null
