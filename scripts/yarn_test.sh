/usr/local/spark/bin/spark-submit \
    --class org.apache.spark.examples.SparkPi \
    --master yarn-cluster \
    /usr/local/spark/examples/jars/spark-examples_2.11-2.4.4.jar \
    10