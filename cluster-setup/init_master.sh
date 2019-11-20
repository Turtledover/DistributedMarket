#!/usr/bin/env bash

# Install packages
sudo apt-get update
sudo apt-get install -y openjdk-8-jre
sudo apt-get install -y curl
sudo apt-get install -y scala
sudo apt-get install -y openssh-server

#JAVA
echo export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 >> ~/.bashrc

#HADOOP
echo "Start setting up Hadoop"
if [ $HADOOP_VERSION ];then
	echo "HADOOP_VERSION = $HADOOP_VERSION"
else
	echo "HADOOP_VERSION IS NOT EXISTS"
fi
env=(
    HADOOP_VERSION,2.5.0
    HADOOP_HOME,/usr/local/hadoop
    HADOOP_CONF_DIR,$HADOOP_HOME/etc/hadoop
    PATH,$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
)
for i in "${env[@]}"; do
    IFS=","; set -- $i;
    echo export $1=$2 >> ~/.bashrc;
    echo export $1=$2 >> ~/.bash_profile;
done
source ~/.bashrc

HADOOP_VERSION=3.0.0
HADOOP_HOME=/usr/local/hadoop
HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

echo "http://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz"

curl -sL --retry 3 \
  "http://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz" \
  | gunzip \
  | tar -xv -C /usr/local
mv /usr/local/hadoop-$HADOOP_VERSION $HADOOP_HOME
rm -rf $HADOOP_HOME/share/doc
chown -R root:root $HADOOP_HOME

# Hadoop Config
cp conf/hadoop/core-site.xml $HADOOP_CONF_DIR/core-site.xml
cp conf/hadoop/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
cp conf/hadoop/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
cp conf/hadoop/yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml
cp conf/hadoop/masters $HADOOP_CONF_DIR/masters
cp conf/hadoop/workers $HADOOP_CONF_DIR/workers
cp conf/hadoop/hadoop-env.sh $HADOOP_CONF_DIR/hadoop-env.sh

echo "Finish setting up Hadoop"

# HDFS & YARN Config
env=(
    HDFS_NAMENODE_USER,root
    HDFS_DATANODE_USER,root
    HDFS_SECONDARYNAMENODE_USER,root
    YARN_RESOURCEMANAGER_USER,root
    YARN_NODEMANAGER_USER,root
)
for i in "${env[@]}"; do
    IFS=","; set -- $i;
    echo export $1=$2 >> ~/.bashrc;
    echo export $1=$2 >> ~/.bash_profile;
done
source ~/.bashrc

echo "Start setting up SSH"
# SSH config
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
cat >> ~/.ssh/authorized_keys < ~/.ssh/id_rsa.pub
echo "Finish setting up SSH"

# SPARK
echo "Start setting up Spark"
env=(
    SPARK_VERSION,2.4.4
    SPARK_PACKAGE,spark-${SPARK_VERSION}-bin-hadoop2.7
    SPARK_HOME,/usr/local/spark
    PATH,$PATH:${SPARK_HOME}/bin
)
for i in "${env[@]}"; do
    IFS=","; set -- $i;
    echo export $1=$2 >> ~/.bashrc;
    echo export $1=$2 >> ~/.bash_profile;
done
source ~/.bashrc

SPARK_VERSION=2.4.4
SPARK_PACKAGE=spark-${SPARK_VERSION}-bin-hadoop2.7
SPARK_HOME=/usr/local/spark
curl -sL --retry 3 \
  "https://www-us.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz" \
  | gunzip \
  | tar -xv -C /usr/local
mv /usr/local/$SPARK_PACKAGE $SPARK_HOME
chown -R root:root $SPARK_HOME

hdfs namenode -format

cp conf/general/02_env.sh /etc/profile.d/
cp conf/spark/spark-env.sh $SPARK_HOME/conf/spark-env.sh
cp conf/spark/spark-defaults.conf $SPARK_HOME/conf/spark-defaults.conf
cp conf/spark/slaves $SPARK_HOME/conf/slaves
cp scripts/launch-master.sh /launch-master.sh
cp scripts/launch-worker.sh /launch-worker.sh
chmod +x /launch-master.sh
chmod +x /launch-worker.sh
chmod +x /etc/profile.d/02_env.sh

echo "Finish setting up Spark"

# Tensorflow on spark
echo "Start setting up Tensorflow"
sudo apt-get install -y python3-pip
sudo apt-get install -y zip
pip3 install tensorflow
pip3 install tensorflowonspark==1.4.4
echo "Finish setting up Tensorflow"


env=(
    PYSPARK_PYTHON,/usr/bin/python3.6
    LIB_HDFS,/usr/local/hadoop/lib/native
    LIB_JVM,$JAVA_HOME/jre/lib/amd64/server
    LD_LIBRARY_PATH,${LIB_HDFS}:${LIB_JVM}
    SPARK_YARN_USER_ENV,PYSPARK_PYTHON=/usr/bin/python3.6
    CLASSPATH,/usr/local/hadoop/etc/hadoop:/usr/local/hadoop/share/hadoop/common/lib/curator-client-2.12.0.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-logging-1.1.3.jar:/usr/local/hadoop/share/hadoop/common/lib/re2j-1.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jackson-core-2.7.8.jar:/usr/local/hadoop/share/hadoop/common/lib/jsp-api-2.1.jar:/usr/local/hadoop/share/hadoop/common/lib/woodstox-core-5.0.3.jar:/usr/local/hadoop/share/hadoop/common/lib/netty-3.10.5.Final.jar:/usr/local/hadoop/share/hadoop/common/lib/jersey-servlet-1.19.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-identity-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/xz-1.0.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-util-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/jaxb-api-2.2.11.jar:/usr/local/hadoop/share/hadoop/common/lib/kerby-asn1-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/snappy-java-1.0.5.jar:/usr/local/hadoop/share/hadoop/common/lib/accessors-smart-1.2.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-collections-3.2.2.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-client-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-configuration2-2.1.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jackson-xc-1.9.13.jar:/usr/local/hadoop/share/hadoop/common/lib/jersey-json-1.19.jar:/usr/local/hadoop/share/hadoop/common/lib/curator-framework-2.12.0.jar:/usr/local/hadoop/share/hadoop/common/lib/kerby-xdr-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-http-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/jcip-annotations-1.0-1.jar:/usr/local/hadoop/share/hadoop/common/lib/avro-1.7.7.jar:/usr/local/hadoop/share/hadoop/common/lib/jersey-server-1.19.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-webapp-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/kerby-util-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-lang3-3.4.jar:/usr/local/hadoop/share/hadoop/common/lib/javax.servlet-api-3.1.0.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-server-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-simplekdc-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/gson-2.2.4.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-xml-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/zookeeper-3.4.9.jar:/usr/local/hadoop/share/hadoop/common/lib/jaxb-impl-2.2.3-1.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-io-2.4.jar:/usr/local/hadoop/share/hadoop/common/lib/metrics-core-3.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-lang-2.6.jar:/usr/local/hadoop/share/hadoop/common/lib/paranamer-2.3.jar:/usr/local/hadoop/share/hadoop/common/lib/htrace-core4-4.1.0-incubating.jar:/usr/local/hadoop/share/hadoop/common/lib/hamcrest-core-1.3.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-codec-1.4.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-beanutils-1.9.3.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-server-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-servlet-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/jettison-1.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jersey-core-1.19.jar:/usr/local/hadoop/share/hadoop/common/lib/token-provider-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/slf4j-log4j12-1.7.25.jar:/usr/local/hadoop/share/hadoop/common/lib/kerby-config-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/protobuf-java-2.5.0.jar:/usr/local/hadoop/share/hadoop/common/lib/asm-5.0.4.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-security-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/jackson-mapper-asl-1.9.13.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-cli-1.2.jar:/usr/local/hadoop/share/hadoop/common/lib/jackson-core-asl-1.9.13.jar:/usr/local/hadoop/share/hadoop/common/lib/junit-4.11.jar:/usr/local/hadoop/share/hadoop/common/lib/slf4j-api-1.7.25.jar:/usr/local/hadoop/share/hadoop/common/lib/hadoop-annotations-3.0.0.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-crypto-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/log4j-1.2.17.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-admin-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-math3-3.1.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jsr311-api-1.1.1.jar:/usr/local/hadoop/share/hadoop/common/lib/mockito-all-1.8.5.jar:/usr/local/hadoop/share/hadoop/common/lib/jsch-0.1.54.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-util-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jul-to-slf4j-1.7.25.jar:/usr/local/hadoop/share/hadoop/common/lib/hadoop-auth-3.0.0.jar:/usr/local/hadoop/share/hadoop/common/lib/json-smart-2.3.jar:/usr/local/hadoop/share/hadoop/common/lib/curator-recipes-2.12.0.jar:/usr/local/hadoop/share/hadoop/common/lib/httpcore-4.4.4.jar:/usr/local/hadoop/share/hadoop/common/lib/guava-11.0.2.jar:/usr/local/hadoop/share/hadoop/common/lib/jackson-databind-2.7.8.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-common-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jackson-annotations-2.7.8.jar:/usr/local/hadoop/share/hadoop/common/lib/httpclient-4.5.2.jar:/usr/local/hadoop/share/hadoop/common/lib/nimbus-jose-jwt-4.41.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jackson-jaxrs-1.9.13.jar:/usr/local/hadoop/share/hadoop/common/lib/jsr305-3.0.0.jar:/usr/local/hadoop/share/hadoop/common/lib/kerby-pkix-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/lib/jetty-io-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/common/lib/stax2-api-3.1.4.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-net-3.1.jar:/usr/local/hadoop/share/hadoop/common/lib/commons-compress-1.4.1.jar:/usr/local/hadoop/share/hadoop/common/lib/kerb-core-1.0.1.jar:/usr/local/hadoop/share/hadoop/common/hadoop-common-3.0.0-tests.jar:/usr/local/hadoop/share/hadoop/common/hadoop-nfs-3.0.0.jar:/usr/local/hadoop/share/hadoop/common/hadoop-kms-3.0.0.jar:/usr/local/hadoop/share/hadoop/common/hadoop-common-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs:/usr/local/hadoop/share/hadoop/hdfs/lib/curator-client-2.12.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-logging-1.1.3.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/re2j-1.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jackson-core-2.7.8.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/woodstox-core-5.0.3.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/netty-3.10.5.Final.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jersey-servlet-1.19.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-identity-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/xz-1.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-util-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jaxb-api-2.2.11.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerby-asn1-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/snappy-java-1.0.5.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/accessors-smart-1.2.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-collections-3.2.2.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-client-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-configuration2-2.1.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jackson-xc-1.9.13.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jersey-json-1.19.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/curator-framework-2.12.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerby-xdr-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-http-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/netty-all-4.0.23.Final.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/okio-1.4.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jcip-annotations-1.0-1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/avro-1.7.7.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jersey-server-1.19.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-webapp-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerby-util-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-lang3-3.4.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/javax.servlet-api-3.1.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-server-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-simplekdc-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/gson-2.2.4.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-xml-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/zookeeper-3.4.9.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jaxb-impl-2.2.3-1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-io-2.4.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-lang-2.6.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/paranamer-2.3.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/htrace-core4-4.1.0-incubating.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-util-ajax-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-codec-1.4.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-beanutils-1.9.3.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-server-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-servlet-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jettison-1.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jersey-core-1.19.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/token-provider-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/okhttp-2.4.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerby-config-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/protobuf-java-2.5.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/asm-5.0.4.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-security-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jackson-mapper-asl-1.9.13.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-cli-1.2.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jackson-core-asl-1.9.13.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/hadoop-annotations-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-crypto-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/log4j-1.2.17.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-admin-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-math3-3.1.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jsr311-api-1.1.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/json-simple-1.1.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/leveldbjni-all-1.8.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jsch-0.1.54.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-util-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/hadoop-auth-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/json-smart-2.3.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/curator-recipes-2.12.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/httpcore-4.4.4.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/guava-11.0.2.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jackson-databind-2.7.8.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-common-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jackson-annotations-2.7.8.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/httpclient-4.5.2.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-daemon-1.0.13.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/nimbus-jose-jwt-4.41.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jackson-jaxrs-1.9.13.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jsr305-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerby-pkix-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/jetty-io-9.3.19.v20170502.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/stax2-api-3.1.4.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-net-3.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/commons-compress-1.4.1.jar:/usr/local/hadoop/share/hadoop/hdfs/lib/kerb-core-1.0.1.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-native-client-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-nfs-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-3.0.0-tests.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-httpfs-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-native-client-3.0.0-tests.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-client-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-3.0.0.jar:/usr/local/hadoop/share/hadoop/hdfs/hadoop-hdfs-client-3.0.0-tests.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-nativetask-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-core-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-app-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-hs-plugins-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-hs-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-common-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.0.0-tests.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-shuffle-3.0.0.jar:/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn:/usr/local/hadoop/share/hadoop/yarn/lib/jsp-2.1-6.1.14.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-client-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jamon-runtime-2.4.1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-prefix-tree-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jasper-runtime-5.5.23.jar:/usr/local/hadoop/share/hadoop/yarn/lib/htrace-core-3.1.0-incubating.jar:/usr/local/hadoop/share/hadoop/yarn/lib/joni-2.1.2.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jersey-guice-1.19.jar:/usr/local/hadoop/share/hadoop/yarn/lib/metrics-core-2.2.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-common-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/ehcache-3.3.1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-hadoop2-compat-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/json-io-2.5.1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/commons-httpclient-3.1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jersey-client-1.19.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jasper-compiler-5.5.23.jar:/usr/local/hadoop/share/hadoop/yarn/lib/commons-csv-1.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/servlet-api-2.5-6.1.14.jar:/usr/local/hadoop/share/hadoop/yarn/lib/java-util-1.9.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-server-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/metrics-core-3.0.1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/findbugs-annotations-1.3.9-1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-protocol-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/geronimo-jcache_1.0_spec-1.0-alpha-1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/commons-math-2.2.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jcodings-1.0.8.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-procedure-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/guice-4.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/aopalliance-1.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/javax.inject-1.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-hadoop-compat-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/fst-2.50.jar:/usr/local/hadoop/share/hadoop/yarn/lib/hbase-annotations-1.2.6.jar:/usr/local/hadoop/share/hadoop/yarn/lib/mssql-jdbc-6.2.1.jre7.jar:/usr/local/hadoop/share/hadoop/yarn/lib/HikariCP-java7-2.4.12.jar:/usr/local/hadoop/share/hadoop/yarn/lib/disruptor-3.3.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jackson-jaxrs-json-provider-2.7.8.jar:/usr/local/hadoop/share/hadoop/yarn/lib/guice-servlet-4.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/commons-el-1.0.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jsp-api-2.1-6.1.14.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jackson-jaxrs-base-2.7.8.jar:/usr/local/hadoop/share/hadoop/yarn/lib/jackson-module-jaxb-annotations-2.7.8.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-api-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-timelineservice-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-timelineservice-hbase-tests-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-applications-unmanaged-am-launcher-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-client-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-router-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-timelineservice-hbase-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-applicationhistoryservice-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-registry-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-sharedcachemanager-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-web-proxy-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-timeline-pluginstorage-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-tests-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-common-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-common-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-nodemanager-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-server-resourcemanager-3.0.0.jar:/usr/local/hadoop/share/hadoop/yarn/hadoop-yarn-applications-distributedshell-3.0.0.jar
    USER,root
)
for i in "${env[@]}"; do
    IFS=","; set -- $i;
    echo export $1=$2 >> ~/.bashrc;
    echo export $1=$2 >> ~/.bash_profile;
done
source ~/.bashrc

#echo IP    master >> /etc/hosts
mkdir /tmp/spark-events

echo "Finish setting up cluster"