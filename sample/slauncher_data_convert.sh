scala \
-classpath $SPARK_HOME/jars/spark-launcher_2.11-2.4.4.jar \
/scala/main.scala \
--entry "hdfs:///user/root/mnist/input/code/mnist_data_setup.py" \
--jobid 1 \
--archives "hdfs:///user/root/mnist/input/data/mnist.zip#mnist" \
--appArgs "--output mnist/output --format csv"

# Version with update database
scala \
-classpath $SPARK_HOME/jars/spark-launcher_2.11-2.4.4.jar \
/scala/db/target/scala-2.11/dmlauncher-assembly-1.0.jar \
--entry "hdfs:///user/root/mnist/input/code/mnist_data_setup.py" \
--jobid 1 \
--archives "hdfs:///user/root/mnist/input/data/mnist.zip#mnist" \
--appArgs "--output mnist/output --format csv"