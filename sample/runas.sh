if [ "$1" == "" ] || [ "$2" == ""]; then
    echo "Usage: runas.sh <username> <command>"
    exit 1
fi

su - $1 -s /bin/bash -c "$2"