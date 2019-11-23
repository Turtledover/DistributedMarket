import subprocess
import threading
import os
import sys
import requests

class Spark:
    spark_status_url = 'http://127.0.0.1:18080/api/v1/applications/'
    
    @staticmethod
    def get_attempts_executors_log(spark_id, att_id):
        url = Spark.spark_status_url + spark_id + '/' + att_id + '/executors'

        try:
            res = requests.get(url)
            if res.status_code == 200:
                print('status is 200', file=sys.stderr)
                result = []
                executors = res.json()
                print(executors, file=sys.stderr)
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
        :param string user: username to run the job
        :param int jobId: Job ID
        :param string entry: the python entry program to run
        :param string libs: comma-separeted list of python dependencies
        :param string archives: comma-seperated list of file to extract to the same directory of the file
        :param string appParams: arguments pass to the entry program
        """

        logfile = open('/submit-out', 'a+')
        errorfile = open('/submit-err', 'a+')
        logfile.write('submitJob id=' + str(jobId) + '\n')

        # TODO: check file exist
        if not entry:
            return

        su = ['su', '-', user, '-c']

        if not 'SPARK_HOME' in os.environ:
            logfile.write('SPARK_HOME is not found in environment\n')
            logfile.close()
            return

        # TODO: make jars path and main path configurable
        command = [
            '/usr/bin/scala',
            '-classpath', os.environ['SPARK_HOME'] + '/jars/spark-launcher_2.11-2.4.4.jar',
            '/scala/dmlauncher-assembly-1.0.jar',
            '--entry', entry,
            '--jobid', str(jobId)
        ]
        
        if archives:
            command.extend(['--archives', archives])

        if libs:
            command.extend(['--py-files', libs])

        if appParams:
            command.extend(['--appArgs', appParams])

        # cmdStr = ' '.join(command)
        # su.append(cmdStr)
        # subprocess.Popen(su)
        logfile.write('before subprocess call\n')
        subprocess.Popen(command)
        
        logfile.write('after subprocess call\n')
        logfile.close()
        errorfile.close()

        return

if __name__ == '__main__':
    Spark.submitJob(
        '1',
        '2',
        'hdfs:///user/root/mnist/input/code/spark/mnist_spark.py',
        'hdfs:///user/root/mnist/input/code/spark/mnist_dist.py',
        '',
        '--images mnist/output/test/images --labels mnist/output/test/labels --mode inference --model mnist/output/mnist_model --output mnist/output/predictions'
    )
    print('Finish submitJob')
