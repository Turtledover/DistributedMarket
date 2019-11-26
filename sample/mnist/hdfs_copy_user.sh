#!/bin/bash

if [ -z "$USER" ]
then
    echo "Please set USER env variable!"
    exit
fi

hdfs dfs -mkdir /user
hdfs dfs -mkdir /user/$USER/
hdfs dfs -mkdir /user/$USER/mnist
hdfs dfs -mkdir /user/$USER/mnist/input
hdfs dfs -mkdir /user/$USER/mnist/input/data
hdfs dfs -copyFromLocal code/ /user/$USER/mnist/input/
hdfs dfs -copyFromLocal mnist/mnist.zip /user/$USER/mnist/input/data/

hdfs dfs -mkdir /user/$USER/mnist/output