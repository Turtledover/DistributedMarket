# Steps of commands to create User in linux and HDFS

# One time setup
hdfs dfs -mkdir /tmp
hdfs dfs -chmod -R 1777 /tmp
chmod 777 /hadooptmp/
hdfs dfs -chmod 777 /shared/log/

# Each user
useradd -M -s /usr/sbin/nologin user2
hdfs dfs -mkdir /user
hdfs dfs -mkdir /user/user2
hdfs dfs -chown user2:user2 /user/user2

hdfs dfs -mkdir /shared/log/user2
hdfs dfs -chown user2:user2 /shared/log/user2

hdfs dfsadmin -refreshUserToGroupsMappings

# Run job Sample
su - test -s /bin/bash -c "cd sample && ./hdfs_copy_user.sh"
su - user2 -s /bin/bash -c "/usr/bin/scala -classpath /usr/local/spark/jars/spark-launcher_2.11-2.4.4.jar /scala/dmlauncher-assembly-1.0.jar --entry hdfs:///user/user2/mnist/input/code/mnist_data_setup.py --appArgs '--output mnist/output --format csv' --archives 'hdfs:///user/user2/mnist/input/data/mnist.zip#mnist' --jobid 1"