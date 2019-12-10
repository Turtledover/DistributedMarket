# DistributedMarket
A distributed market platform designed for machine learning tasks. <br/>
The platform consists of one central server and many number of clients. <br/>
This repo is the central server, repo of clients could be found at <br/>
https://github.com/Turtledover/Desktop-Application <br/>

# Project Structure
* ./conf/: All configurations files for Dockerfile to build a docker image
* ./dmarket/: Django web services with API and logic to manage machines, jobs and credits
  * services/views.py: Entry function for all APIs.
  * services/cron.py: Function that run periodically by cron.
* ./doc/: More documentations
* ./sample/: Sample code and data to test submitting a ML job to the system
* ./scala/: Scala code that used by the Django services to submit job to spark and get job status
* ./scripts/: Contain scripts that startup the system in docker as well as actual computers

# Setup
The project could be setup in docker for development as well as 
in actual computers for deployment. Instructions to setup in each environment is 
in the following sections.

## Setup in Docker
Follow these instructions to setup the central server, after the central server
up, you could follow the instructions at https://github.com/Turtledover/Desktop-Application
to connect any number of client to server.

### First time setup
1. Install docker
2. Clone https://github.com/Turtledover/spark-hadoop-docker to a separate folder
3. Run `./build.sh` in spark-hadoop-docker (This will build our base docker image with hadoop, spark, tensorflow and tensorflowOnSpark)
4. Change back to this directory, run `./build.sh` in this directory

### Start the docker
1. Run `docker-compose up` in root folder of this project
2. You can now browse 'http://localhost:8088' for Hadoop UI and 'http://localhost:8000/services/' for Django server
3. You can also browse 'http://localhost:18080/' for spark history server which give you previous job status

### Submit sample MNIST training jobs
Currently, the system assume code and data of a job located in HDFS. <br/>
All code and data has to be uploaded to HDFS first before it could be run. <br/>
Run the Sample MNIST Job: <br/>
1. Connect to docker with: `docker exec -it distributedmarket_master_1 /bin/bash`
2. `cd /sample/mnist`
3. Run `download.sh` to download the datasets (Only need to download once)
4. `./hdfs_copy.sh`
5. `./hdfs_mnist_data_convert.sh` to submit the job to prepare MNIST data for training
6. `./hdfs_mnist_train.sh` to submit a job to train on MNIST datasets
7. `./hdfs_mnist_test.sh` to submit a job to evaluate the training result 

### NOTES for testing in Docker environments
* In docker environments, the initial cluster only contains 1 master node, which serves as both the datanode and namenode in Hadoop, and both the slave node and master node in Spark. You can then add the user machine to the cluster one by one.
* After the initial master has been launched and the desktop app has been installed:
  1. You should have default "admin" account setup. (You can change its password in ./scripts/start.sh before setup)
  2. The initial master node should be automatically added to the machine table.
  3. Other users can add their machines. (See https://github.com/Turtledover/Desktop-Application)

### Use the API
1. Submit MNIST data convert job with API: http://localhost:8000/services/job/submit/?entry_file=hdfs%3A%2F%2F%2Fuser%2Froot%2Fmnist%2Finput%2Fcode%2Fmnist_data_setup.py&archives=hdfs%3A%2F%2F%2Fuser%2Froot%2Fmnist%2Finput%2Fdata%2Fmnist.zip%23mnist&app_params=--output%20mnist%2Foutput%20--format%20csv&name=MNIST%20Data%20Convert
2. Use job list API to get the job status: http://localhost:8000/services/job/list/

## Setup on real machines
Follow these instructions to setup the central server on a real machine. This will allow you to setup the DistributedMarket system on your own machines. You could follow the instructions at https://github.com/Turtledover/Desktop-Application to connect any number of client to server.

### Initialize the cluster and the central server
On the machine that you would like to use as the master server,
1. First, run `ifconfig` to get the IP address of your computer.
2. Add the following two entries in /etc/hosts
   - [your ip]  master
   - 127.0.0.1  db
3. Go to the directory of the project, execute `sudo su` and then `./install.sh` with root permission. This will automatically install required files for Spark, Hadoop, Django, Postgres and TensorFlowOnSpark. This will also setup the Spark and HDFS/YARN cluster, and setup the Django server on this machine.

### Start the server
On the central server, start a new terminal and run `sudo su`. And then, go to this directory, run `./scripts/start_central_server.sh`. This will start the Spark and HDFS/YARN cluster, and start running the Django server.

### Uninstall the system
To uninstall the system from the central server machine, 
1. run `./uninstall.sh`
2. Edit /etc/hosts and remove all entries of slave hosts. (Only applicable when you have added any machines)

# Troubleshooting
1. FileNotFoundError: No such file or directory: 'executor_id' when running MNIST training sample
   - Currently, the number of executors used by Spark is hardcoded as 5 in the file dmarket/services/corelib/spark.py. Set "--cluster_size" parameter for the application to 4 may help, or else do not set the "--cluster_size" parameter at all.
   

# DB model design
1. User
   - User_id (uuid (random hash 32))
   - User_name (str 32 limit)
   - Password (hash_code 64)
   - Email_address (str)
   - Credit (credit instance)
2. Machine
    - Machine_id (hash_code)
    - Machine_type (enum)
    - IP_address (str)
    - Service_port (int)
    - Core_count (int)
    - Memory_size (double)
    - Time_period (int)
    - Availability (enum)
    - User_id (foreign key)
3. Job
    - Job_id (hash_code)
    - Job_name (str)
    - Added_time (datetime)
    - Start_time (big int)
    - End_time (bit int)
    - Duration (int)
    - Used_credit (int)
    - entry_file (str)
    - libs (str)
    - archives (str)
    - app_params (str)
    - Status (enum)
    - User_id (foreign key)
4. Metadata
    - Machine_info (dict)
5. Credit
    - Sharing_credit
    - Using_credit
    - Rate
    - User_id (uuid (random hash 32))

# API stub design

1. register(username, password, email)
2. Login (username, password)
3. Submit_machine (core_count, machine_type, memory_size, Time_period [ip_address, port]) -> Success (json: {status, machine_id})
4. Remove_machine (machine_id) -> Success (json: {status})
5. List_machines () -> (json:[machines]})
6. Submit_job (root_path, Core_num, Machine_type) -> Success (json: {status, job_id})
7. Cancel_job (job_id) -> Success (json: {status, job_id})
8. Get_result (job_id) -> Success (json: {files})
9. Get_log (job_id) -> Success (json: {files})
10. get_credits (user_id) -> Success (json: {Sharing_credit, Using_credit, Rate})
11. get_job_list() -> Success(json)
