kill -9 `jps | grep "NameNode" | cut -d " " -f 1`
kill -9 `jps | grep "ResourceManager" | cut -d " " -f 1`
kill -9 `jps | grep "NodeManager" | cut -d " " -f 1`
kill -9 `jps | grep "SecondaryNameNode" | cut -d " " -f 1`
kill -9 `jps | grep "DataNode" | cut -d " " -f 1`
kill -9 `jps | grep "HistoryServer" | cut -d " " -f 1`
rm -rf /usr/local/hadoop
rm -rf /usr/local/spark
rm -rf /hadooptmp
rm /etc/environment
touch /etc/environment
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/local/games" >> /etc/environment
source /etc/environment
rm -rf ~/.ssh
rm firstlaunch
rm -rf dmarket/medias
python3 dmarket/manage.py shell < clear_db.py
apt remove postgresql-contrib -y
apt remove postgresql -y

echo "!!!Remember to manually remove hosts for /etc/hosts!!!"

