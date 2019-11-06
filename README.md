# DistributedMarket
A distributed market platform designed for machine learning tasks.

# First time setup
1. Install docker
2. Clone https://github.com/Turtledover/spark-hadoop-docker to a separate folder
3. Run `./build.sh` in docker-spark folder

# Start the docker
1. Run `docker-compose up` in root folder of this project
2. You can now browse 'http://localhost:8088' for Hadoop UI and 'http://localhost:8000/services/' for Django server
3. You can also browse 'http://localhost:18080/' for spark history server which give you previous job status

# Run a job
Currently, the system assume code and data of a job located in HDFS. <br/>
All code and data has to be uploaded to HDFS first before it could be run. <br/>
Run the Sample MNIST Job: <br/>
1. Connect to docker with: `docker exec -it  distributedmarket_master_1 /bin/bash`
2. `cd sample`
3. `./hdfs_copy.sh`
4. Submit MNIST data convert job with API: http://127.0.0.1:8000/services/job/submit/?entry_file=hdfs%3A%2F%2F%2Fuser%2Froot%2Fmnist%2Finput%2Fcode%2Fmnist_data_setup.py&archives=hdfs%3A%2F%2F%2Fuser%2Froot%2Fmnist%2Finput%2Fdata%2Fmnist.zip%23mnist&app_params=--output%20mnist%2Foutput%20--format%20csv&name=MNIST%20Data%20Convert
5. Use job list API to get the job status: http://127.0.0.1:8000/services/job/list/

# NOTICE for testing in Docker environments (qilian branch)
* In docker environments, the initial cluster only contains 1 master node, which serves as both the datanode and namenode in Hadoop, and both the slave node and master node in Spark. You can then add the user machine to the cluster one by one.
* After the initial master has been launched and the desktop app has been installed:
  1. The user who install this app should register an admin account.
  2. After the admin account has been created, the initial master should be automatically added to the machine table.
  3. Then other users can add their machines.
* First cd to the root directory of this repo, and start a container by running the command `docker run -v <absolute_path_to_scripts_directory>:/scripts -it ubuntu /bin/bash`. 
* Before the user machine is added, make sure you run the command `docker network connect distributedmarket_static-network <container_id>` so that the user machine can access other docker containers.
* Install the python package in the new ubuntu container: `apt update && apt install python3-pip -y`.
* Manually run the `init_cluster.py` script to add the master node to the database.
* [TBD] The first connection with master node required yes/no.

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