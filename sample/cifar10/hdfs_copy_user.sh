#!/bin/bash

if [ -z "$USER" ]
then
    echo "Please set USER env variable!"
    exit
fi

hdfs dfs -mkdir /user
hdfs dfs -mkdir /user/$USER/
hdfs dfs -mkdir /user/$USER/cifar
hdfs dfs -mkdir /user/$USER/cifar/input
hdfs dfs -mkdir /user/$USER/cifar/input/data
hdfs dfs -copyFromLocal code/ /user/$USER/cifar/input/
hdfs dfs -copyFromLocal data/cifar-10-batches-bin /user/$USER/cifar/input/data/

hdfs dfs -mkdir /user/$USER/cifar/output