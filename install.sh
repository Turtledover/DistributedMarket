# The downloaded installation package contains the following files:
# - install.sh
# - conf/
# - dmarket/
# - scripts/
# - sample/
# - scala/

# Install the required packages
apt-get update
apt-get install openjdk-8-jdk curl scala openssh-server -y

BASEDIR=$(dirname "$0")
DMARKET_ROOT="${BASEDIR}/dmarket"
echo "DMARKET_ROOT" >> /etc/environment

# Set up the environment for Hadoop & Yarn
JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"
HADOOP_VERSION="3.0.0"
HADOOP_HOME="/usr/local/hadoop"
HADOOP_CONF_DIR="${HADOOP_HOME}/etc/hadoop"
{ echo "JAVA_HOME=${JAVA_HOME}"; \
  echo "HADOOP_HOME=${HADOOP_HOME}"; \
  echo "HADOOP_CONF_DIR=${HADOOP_CONF_DIR}"; \
  echo "PATH=$PATH:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin"; \
  echo "HDFS_NAMENODE_USER=\"root\""; \
  echo "HDFS_DATANODE_USER=\"root\""; \
  echo "HDFS_SECONDARYNAMENODE_USER=\"root\""; \
  echo "YARN_RESOURCEMANAGER_USER=\"root\""; \
  echo "YARN_NODEMANAGER_USER=\"root\""; } >> /etc/environment
source /etc/environment
# Install Hadoop
curl -sL --retry 3 \
  "http://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" \
  | gunzip \
  | tar -x -C /usr/local \
 && mv /usr/local/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
 && rm -rf ${HADOOP_HOME}/share/doc \
 && chown -R root:root ${HADOOP_HOME}
cp conf/hadoop/* ${HADOOP_CONF_DIR}/

# TODO check if a public key has already existed
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa \
 && cat >> ~/.ssh/authorized_keys < ~/.ssh/id_rsa.pub

# Set up the environment for Spark
SPARK_VERSION="2.4.4"
SPARK_PACKAGE="spark-${SPARK_VERSION}-bin-hadoop2.7"
SPARK_HOME="/usr/local/spark"
{ echo "SPARK_HOME=${SPARK_HOME}"; \
  echo "PATH=$PATH:${SPARK_HOME}/bin"; } >> /etc/environment
source /etc/environment
# Install Spark
curl -sL --retry 3 \
  "https://www-us.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz" \
  | gunzip \
  | tar x -C /usr/local \
 && mv /usr/local/${SPARK_PACKAGE} ${SPARK_HOME} \
 && chown -R root:root ${SPARK_HOME}
hdfs namenode -format

cp conf/general/02_env.sh /etc/profile.d/
cp conf/spark/* ${SPARK_HOME}/conf/
cp scripts/* /
chmod +x /launch-master.sh
chmod +x /etc/profile.d/02_env.sh

# Install Tensorflow & TensorflowOnSpark
apt-get install python3-pip zip -y
pip3 install tensorflow tensorflowonspark==1.4.4
LIB_HDFS="/usr/local/hadoop/lib/native"
LIB_JVM="${JAVA_HOME}/jre/lib/amd64/server"
{ echo "PYSPARK_PYTHON=/usr/bin/python3.6"; \
  echo "LIB_HDFS=${LIB_HDFS}"; \
  echo "LIB_JVM=${LIB_JVM}"; \
  echo "LD_LIBRARY_PATH=${LIB_HDFS}:${LIB_JVM}"; \
  echo "SPARK_YARN_USER_ENV=\"PYSPARK_PYTHON=/usr/bin/python3.6\""; \
  echo "CLASSPATH=$(hadoop classpath --glob)"; } >> /etc/environment
source /etc/environment

# Install other dependencies
pip3 install Django==2.1.* \
  && pip3 install psycopg2-binary \
  && pip3 install django-cron \
  && pip3 install -U python-dotenv \
  && pip3 install psutil \
  && pip3 install requests
apt-get install -y cron
cp conf/cron/services.cron /etc/cron.d/
chmod 0644 /etc/cron.d/services.cron
crontab /etc/cron.d/services.cron

# Install the PostgreSQL
apt-get install libpq-dev postgresql postgresql-contrib -y
sudo -u postgres psql -c "CREATE DATABASE postgres;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD '123456';"
sudo -u postgres psql -c "ALTER ROLE postgres SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE postgres SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;"
