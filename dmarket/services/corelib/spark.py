import subprocess
import threading
import os
import sys
import requests

class Spark:
    # Url of Spark History Server
    spark_status_url = 'http://127.0.0.1:18080/api/v1/applications/'
    
    @staticmethod
    def get_attempts_executors_log(spark_id, att_id):
        """
        Retrieve url of all logs from all executors from an application attempt.

        :param string spark_id: Spark application ID.
        :param string att_id: AttemptID. None if not running in YARN cluster mode.
        :return: a list of all executors and their log url.
        """

        url = Spark.spark_status_url + spark_id + '/executors'
        if att_id != None:
            url = Spark.spark_status_url + spark_id + '/' + att_id + '/executors'

        try:
            res = requests.get(url)
            if res.status_code == 200:
                result = []
                executors = res.json()
                for e in executors:
                    r = {}
                    r['id'] = e['id']
                    r['logs'] = e['executorLogs']
                    result.append(r)
                    
                return result
            
        except Exception as e:
            print('get_attempt_executors exception', file=sys.stderr)
            print(e, file=sys.stderr)

        return None
    
    @staticmethod
    def get_spark_app(spark_id):
        """
        Retrieve a Spark application status from Spark History Server.
        Reference: https://spark.apache.org/docs/latest/monitoring.html

        :param string spark_id: Spark application ID
        :return: the application json object from Spark History Server
        """

        print('get_spark_app', file=sys.stderr)
        url = Spark.spark_status_url + spark_id
        try:
            res = requests.get(url)
            print(res.content, file=sys.stderr)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print('exception')
        
        return None

    @staticmethod
    def get_attempt_executors_list(spark_id, att_id):
        """
        Retrieve all executors of an application attempt.

        :param string spark_id: Application ID provided by Spark
        :param string att_id: AttemptID. None if not running in YARN cluster mode
        """

        url = Spark.spark_status_url + spark_id + '/executors'
        if att_id != None:
            url = Spark.spark_status_url + spark_id + '/' + att_id + '/executors'

        try:
            res = requests.get(url)
            if res.status_code == 200:
                print('status is 200', file=sys.stderr)
                execs = {}
                executors = res.json()
                print(executors, file=sys.stderr)
                for e in executors:
                    host = e['hostPort'].split(':')[0]
                    if not host in execs:
                        execs[host] = {}
                        execs[host]['usage'] = []
                    
                    execs[host]['usage'].append({
                        'cores': e['totalCores'],
                        'memory': e['maxMemory'],
                        'duration': e['totalDuration'],
                        'logs': e['executorLogs'],
                        'isDriver': e['id'] == 'driver'
                    })
                return execs
            
        except Exception as e:
            print('get_attempt_executors exception', file=sys.stderr)
            print(e, file=sys.stderr)

        return None

    @staticmethod
    def submitJob(user, jobId, entry, libs, archives, appParams):
        """
        Launch a SparkLauncher in a jar and pass the parameter to it to submit
        application to spark. We used SparkLauncher so that we could monitor the
        status of an application.

        :param string user: username to run the job
        :param int jobId: Job ID
        :param string entry: the python entry program to run
        :param string libs: comma-separeted list of python dependencies
        :param string archives: comma-seperated list of file to extract to the same directory of the file
        :param string appParams: arguments pass to the entry program
        """

        print('submitJob id=' + str(jobId), file=sys.stderr)

        # TODO: check file exist
        if not entry:
            return

        print('run as user = ' + user, file=sys.stderr)
        su = ['su', '-', user, '-s', '/bin/bash', '-c']

        if not 'SPARK_HOME' in os.environ:
            print('SPARK_HOME is not found in environment', file=sys.stderr)
            return

        # TODO: make jars path and main path configurable
        command = [
            '/usr/bin/scala',
            '-classpath', os.environ['SPARK_HOME'] + '/jars/spark-launcher_2.11-2.4.4.jar',
            '/scala/dmlauncher.jar',
            '--entry', entry,
            '--jobid', str(jobId)
        ]
        
        if archives:
            command.extend(['--archives', '"' + archives + '"'])

        if libs:
            command.extend(['--py-files', '"' + libs + '"'])

        if appParams:
            command.extend(['--appArgs', '"' + appParams + '"'])

        cmdStr = ' '.join(command)
        su.append(cmdStr)
        print('before subprocess call', file=sys.stderr)
        subprocess.Popen(su, stderr=sys.stderr, stdout=sys.stderr)
        print('after subprocess call', file=sys.stderr)

        return
