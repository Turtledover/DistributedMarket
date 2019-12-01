#!/bin/bash

hdfs dfs -mkdir /user
hdfs dfs -mkdir /user/root/
hdfs dfs -mkdir /user/root/cifar
hdfs dfs -mkdir /user/root/cifar/input
hdfs dfs -mkdir /user/root/cifar/input/data
hdfs dfs -copyFromLocal code/ /user/root/cifar/input/
hdfs dfs -copyFromLocal data/cifar-10-batches-bin /user/root/cifar/input/data/

hdfs dfs -mkdir /user/root/cifar/output