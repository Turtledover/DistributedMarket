#!/bin/bash

hadoop fs -mkdir /user
hadoop fs -mkdir /user/root/
hadoop fs -mkdir /user/root/mnist
hadoop fs -mkdir /user/root/mnist/input
hadoop fs -mkdir /user/root/mnist/input/data
hadoop fs -copyFromLocal code/ /user/root/mnist/input/
hadoop fs -copyFromLocal mnist/mnist.zip /user/root/mnist/input/data/

hadoop fs -mkdir /user/root/mnist/output