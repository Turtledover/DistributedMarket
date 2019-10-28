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