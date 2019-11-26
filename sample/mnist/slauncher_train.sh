scala \
-classpath $SPARK_HOME/jars/spark-launcher_2.11-2.4.4.jar \
/scala/dmlauncher.jar \
--entry "hdfs:///user/root/mnist/input/code/spark/mnist_spark.py" \
--py-files "hdfs:///user/root/mnist/input/code/spark/mnist_dist.py" \
--jobid 1 \
--appArgs "--images mnist/output/train/images --labels mnist/output/train/labels --mode train --model mnist/output/mnist_model"
