#!/bin/bash

if [ -z "$USER" ]
then
    echo "Please set USER env variable!"
    exit
fi

hadoop fs -mkdir /user
hadoop fs -mkdir /user/$USER/
hadoop fs -mkdir /user/$USER/mnist
hadoop fs -mkdir /user/$USER/mnist/input
hadoop fs -mkdir /user/$USER/mnist/input/data
hadoop fs -copyFromLocal code/ /user/$USER/mnist/input/
hadoop fs -copyFromLocal mnist/mnist.zip /user/$USER/mnist/input/data/

hadoop fs -mkdir /user/$USER/mnist/output