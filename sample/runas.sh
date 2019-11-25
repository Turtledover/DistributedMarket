if [ "$1" == "" ] || [ "$2" == ""]; then
    echo "Usage: hdfs_mnist_data_convert.sh <username> <command>"
    exit 1
fi

su - $1 -s /bin/bash -c "$2"