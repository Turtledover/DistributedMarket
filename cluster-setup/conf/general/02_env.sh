export HADOOP_HOME="/usr/local/hadoop"
export HADOOP_VERSION="3.0.0"
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"

export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"

export SPARK_VERSION="2.4.4"
export SPARK_HOME="/usr/local/spark"

export PYSPARK_PYTHON="/usr/bin/python3.6"
export LIB_HDFS="/usr/local/hadoop/lib/native"
export LIB_JVM="JAVA_HOME/jre/lib/amd64/server"
export LD_LIBRARY_PATH="$LIB_HDFS:$LIB_JVM"
export SPARK_YARN_USER_ENV="PYSPARK_PYTHON=/usr/bin/python3.6"

export PATH="$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME:/bin"

export SPARK_DIST_CLASSPATH="$(hadoop classpath)"
export CLASSPATH="$(hadoop classpath --glob)"