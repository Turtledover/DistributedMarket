docker network connect distributedmarket_static-network NEW_CONTAINER
docker exec -it NEW_CONTAINTER /bin/bash

apt-get update && apt-get -y dist-upgrade # Should be sudo if it's on a regular machine
apt-get -y install openjdk-8-jdk-headless
echo "JAVA_HOME='/usr/lib/jvm/java-8-openjdk-amd64'" >> /etc/environment
source /etc/environment

# Modularize the job submission to integrate with the existing system

# Write a ssh public key distributor

# Each newly-added machine should specify one username. (we can assume everyone is root because otherwise you can't grant the system resources to others)
#   => can't simulate in docker as every one is root in Docker.
# Generate the ssh key and copy the keys to all the servers
apt-get update
apt-get install -y openssh-server
apt-get install -y openssh-client
# Check if the id_rsa key exists
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
# Set up the HDFS load balancer
# Set up the HDFS load balancer
# Add the datanode and run as dameon

echo "HADOOP_HOME='/usr/local/hadoop'" >> /etc/environment
echo "HADOOP_CONF_DIR='$HADOOP_HOME/etc/hadoop'" >> /etc/environment
source /etc/environment

# cp hosts from master to the new machine
scp -o StrictHostKeyChecking=no distributedmarket_slave1_1:/etc/hosts /etc/hosts

# install iproute2 to enable command "ip"
apt install iproute2 #Require input 'Y'
# append "hostname  ip" of the new machine to the hosts file, suppose the new machine is slave3 for now.
(ip a | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,2}\b" | grep 10.0 | tr -d '\n'; echo "     slave3") >> /etc/hosts

# cp the new hosts file to other machines ??? how to get list of other machines
scp /etc/hosts master:/etc/hosts

# cp hadoop and spark config files to new machine
scp -r slave1:/usr/local/hadoop /usr/local/hadoop
scp -r slave1:/usr/local/spark /usr/local/spark

# append "slave3" to hadoop workers file
echo -e "\nslave3" >> /usr/local/hadoop/etc/hadoop/workers
# cp the new workers file to other machines ??? how to get list of other machines
scp /usr/local/hadoop/etc/hadoop/workers master:/usr/local/hadoop/etc/hadoop/workers

# append "slave3" to hadoop workers file
echo -e "\nslave3" >> /usr/local/spark/conf/slaves
# cp the new workers file to other machines ??? how to get list of other machines
scp /usr/local/spark/conf/slaves master:/usr/local/spark/conf/slaves

# add hadoop and spark path
echo -e "\nexport PATH=\"$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin:/usr/local/spark/bin:/usr/local/spark/sbin\"" >> ~/.bashrc
source ~/.bashrc