# DistributedMarket
A distributed market platform designed for machine learning tasks.

# First time setup
1. Install docker
2. Clone https://github.com/Turtledover/spark-hadoop-docker to a separate folder
3. Run `./build.sh` in docker-spark folder

# Start the docker
1. Run `docker-compose up` in root folder of this project
2. You can now browse 'http://localhost:8088' for Hadoop UI and 'http://localhost:8000/services/' for Django server
3. If this is the first time you this docker, you need to run the instruction here
  1. Connect to the docker with `docker exec -it <container name> /bin/bash`
  2. Run `python3 /dmarket/manage.py migrate`

# NOTICE for testing in Docker environments (qilian branch)
* In docker environments, the initial cluster only contains 1 master node, which serves as both the datanode and namenode in Hadoop, and both the slave node and master node in Spark. You can then add the user machine to the cluster one by one.
* First cd to the root directory of this repo, and start a container by running the command `docker run -v <absolute_path_to_scripts_directory>:/scripts -it ubuntu /bin/bash`. 
* Before the user machine is added, make sure you run the command `docker network connect distributedmarket_static-network <container_id>` so that the user machine can access other docker containers.
* Install the python package in the new ubuntu container: `apt update && apt install python3-pip -y`.

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
    - entry_file (str)
    - libs (str)
    - archives (str)
    - app_params (str)
    - Core_num (int)
    - Machine_type (enum)
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