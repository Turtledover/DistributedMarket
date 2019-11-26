#!/bin/bash

hadoop fs -mkdir /user
hadoop fs -mkdir /user/root/
hadoop fs -mkdir /user/root/cifar
hadoop fs -mkdir /user/root/cifar/input
hadoop fs -mkdir /user/root/cifar/input/data
hadoop fs -copyFromLocal code/ /user/root/cifar/input/
hadoop fs -copyFromLocal data/cifar-10-batches-bin /user/root/cifar/input/data/

hadoop fs -mkdir /user/root/cifar/output