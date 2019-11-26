# set environment variables (if not already done)
${SPARK_HOME}/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--queue default \
--py-files hdfs:///user/root/cifar/input/code/cifar10.zip \
--conf spark.dynamicAllocation.enabled=false \
--conf spark.executorEnv.LD_LIBRARY_PATH=$LIB_JVM:$LIB_HDFS \
--conf spark.executorEnv.CLASSPATH=$(hadoop classpath --glob) \
--conf spark.executorEnv.LIB_HDFS=$LIB_HDFS \
--conf spark.executorEnv.LIB_JVM=$LIB_JVM \
--conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=$PYSPARK_PYTHON \
--conf spark.pyspark.python=$PYSPARK_PYTHON \
--conf spark.yarn.appMasterEnv.PYTHONPATH=$PYSPARK_PYTHON \
--conf spark.executorEnv.SPARK_YARN_USER_ENV=$SPARK_YARN_USER_ENV \
--conf spark.yarn.maxAppAttempts=1 \
--conf spark.eventLog.enabled=true \
--conf spark.eventLog.dir=hdfs://master:9000/shared/log/ \
--conf spark.ui.enabled=true \
--conf spark.ui.port=4040 \
hdfs:///user/root/cifar/input/code/cifar10_train.py \
--data_dir hdfs:///user/root/cifar/input/data/ \
--train_dir hdfs:///user/root/cifar/output/train \
--max_steps 50