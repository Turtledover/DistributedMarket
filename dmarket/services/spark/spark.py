import subprocess
import threading
import os

class Spark:

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

    # @staticmethod
    # def submitJob(user, entry, libs, archives, appParams):
    #     """
    #     :param string user: username to run the job
    #     :param string entry: the python entry program to run
    #     :param string libs: comma-separeted list of python dependencies
    #     :param string archives: comma-seperated list of file to extract to the same directory of the file
    #     :param list appParams: arguments pass to the entry program
    #     """

    #     logfile = open('/submit-out', 'a+')
    #     errorfile = open('/submit-err', 'a+')

    #     logfile.write('submitJob\n')

    #     # TODO: check file exist
    #     if not entry:
    #         return

    #     su = ['su', '-', user, '-c']

    #     if not 'SPARK_HOME' in os.environ:
    #         logfile.write('SPARK_HOME is not found in environment\n')
    #         logfile.close()
    #         return

    #     command = [
    #         os.environ['SPARK_HOME'] + '/bin/spark-submit',
    #         '--master', 'yarn',
    #         '--deploy-mode', 'cluster',
    #         '--queue', 'default',
    #         '--num-executors', '2',
    #         '--executor-memory', '2G',
    #         '--conf', 'spark.dynamicAllocation.enabled=false',
    #         '--conf', 'spark.yarn.maxAppAttempts=1',
    #         '--conf', 'spark.executorEnv.LD_LIBRARY_PATH=' + os.environ['LIB_JVM'] + ':' + os.environ['LIB_HDFS'],
    #         '--conf', 'spark.executorEnv.CLASSPATH=' + os.environ['CLASSPATH'],
    #         '--conf', 'spark.executorEnv.LIB_HDFS=' + os.environ['LIB_HDFS'],
    #         '--conf', 'spark.executorEnv.LIB_JVM=' + os.environ['LIB_JVM'],
    #         '--conf', 'spark.yarn.appMasterEnv.PYSPARK_PYTHON=' + os.environ['PYSPARK_PYTHON'],
    #         '--conf', 'spark.pyspark.python=' + os.environ['PYSPARK_PYTHON'],
    #         '--conf', 'spark.yarn.appMasterEnv.PYTHONPATH=' + os.environ['PYSPARK_PYTHON'],
    #         '--conf', 'spark.executorEnv.SPARK_YARN_USER_ENV=' + os.environ['SPARK_YARN_USER_ENV'],
    #         '--conf', 'spark.eventLog.enabled=true',
    #         '--conf', 'spark.eventLog.dir=hdfs://master:9000/shared/log/'
    #     ]
        
    #     if archives:
    #         command.extend(['--archives', archives])

    #     if libs:
    #         command.extend(['--py-files', libs])

    #     command.append(entry)

    #     if appParams:
    #         command.extend(appParams)

    #     # cmdStr = ' '.join(command)
    #     # su.append(cmdStr)
    #     # subprocess.Popen(su)
    #     logfile.write('before subprocess call\n')
    #     subprocess.Popen(command)
        
    #     logfile.write('after subprocess call\n')
    #     logfile.close()
    #     errorfile.close()

    #     return
    
    # @staticmethod
    # def jobExit(proc):
    #     print('Job Completed.')

    # def runInThread(onExit):
    #     proc = subprocess.Popen(
    #         [
    #             '/usr/spark-2.4.1/bin/spark-submit',
    #             '/usr/spark-2.4.1/examples/src/main/python/pi.py',
    #             '10' 
    #         ]
    #     )
    #     proc.wait()
    #     onExit(proc)
    #     return
    # thread = threading.Thread(target=runInThread,
    #                         args=(Spark.jobExit,))
    # thread.start()
    # return

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
