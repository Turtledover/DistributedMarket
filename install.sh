# The downloaded installation package contains the following files:
# - install.sh
# - conf/
# - dmarket/
# - scripts/
# - sample/
# - scala/

# Install the required packages
sudo apt-get update
sudo apt-get install openjdk-8-jdk curl scala openssh-server -y

# Set up the environment for Hadoop & Yarn
HADOOP_VERSION="3.0.0"
{ echo "JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64"; \
  echo "HADOOP_HOME=/usr/local/hadoop"; \
  echo "HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop"; \
  echo "PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin"; \
  echo "HDFS_NAMENODE_USE=root"; \
  echo "HDFS_DATANODE_USER=root"; \
  echo "HDFS_SECONDARYNAMENODE_USER=root"; \
  echo "YARN_RESOURCEMANAGER_USER=root"; \
  echo "YARN_NODEMANAGER_USER=root"; } >> /etc/environment
source /etc/environment
# Install Hadoop
curl -sL --retry 3 \
  "http://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz" \
  | gunzip \
  | tar -x -C /usr/local \
 && mv /usr/local/hadoop-$HADOOP_VERSION $HADOOP_HOME \
 && rm -rf $HADOOP_HOME/share/doc \
 && chown -R root:root $HADOOP_HOME
cp conf/hadoop/* $HADOOP_CONF_DIR/

# TODO check if a public key has already existed
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa \
 && cat >> ~/.ssh/authorized_keys < ~/.ssh/id_rsa.pub

# Set up the environment for Spark
SPARK_VERSION="2.4.4"
SPARK_PACKAGE="spark-${SPARK_VERSION}-bin-hadoop2.7"
{ echo "SPARK_HOME=/usr/local/spark"; \
  echo "PATH=$PATH:${SPARK_HOME}/bin"; } >> /etc/environment
source /etc/environment
# Install Spark
curl -sL --retry 3 \
  "https://www-us.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz" \
  | gunzip \
  | tar x -C /usr/local \
 && mv /usr/local/$SPARK_PACKAGE $SPARK_HOME \
 && chown -R root:root $SPARK_HOME
hdfs namenode -format

cp conf/general/02_env.sh /etc/profile.d/
cp conf/spark/* $SPARK_HOME/conf/
cp scripts/* /
chmod +x /launch-master.sh
chmod +x /etc/profile.d/02_env.sh

# Install Tensorflow & TensorflowOnSpark
sudo apt-get install python3-pip zip -y \
pip3 install tensorflow tensorflowonspark==1.4.4
{ echo "PYSPARK_PYTHON=/usr/bin/python3.6"; \
  echo "LIB_HDFS=/usr/local/hadoop/lib/native"; \
  echo "LIB_JVM=$JAVA_HOME/jre/lib/amd64/server"; \
  echo "LD_LIBRARY_PATH ${LIB_HDFS}:${LIB_JVM}"; \
  echo "SPARK_YARN_USER_ENV PYSPARK_PYTHON=/usr/bin/python3.6"; \
  echo "CLASSPATH=$(hadoop classpath --glob)"; } >> /etc/environment
source /etc/environment

# Install other dependencies
pip3 install Django==2.1.* \
  && pip3 install psycopg2-binary \
  && pip3 install django-cron \
  && pip3 install -U python-dotenv \
  && pip3 install psutil \
  && pip3 install requests
sudo apt-get install -y cron
cp conf/cron/services.cron /etc/cron.d/
chmod 0644 /etc/cron.d/services.cron \
  crontab /etc/cron.d/services.cron
