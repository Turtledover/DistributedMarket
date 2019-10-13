import subprocess
import threading
import os

class Spark:

    @staticmethod
    def jobExit(proc):
        print('Job Completed.')

    @staticmethod
    def submitJob(user, entry, libs, archives, appParams):
        """
        :param string user: username to run the job
        :param string entry: the python entry program to run
        :param string libs: comma-separeted list of python dependencies
        :param string archives: comma-seperated list of file to extract to the same directory of the file
        :param list appParams: arguments pass to the entry program
        """
        print('submitJob')

        # TODO: check file exist
        if not entry:
            return

        su = ['su', '-', user, '-c']

        command = [
            os.environ['SPARK_HOME'] + '/bin/spark-submit',
            '--master', 'yarn',
            '--deploy-mode', 'cluster',
            '--queue', 'default',
            '--num-executors', '2',
            '--executor-memory', '2G',
            '--conf', 'spark.dynamicAllocation.enabled=false',
            '--conf', 'spark.yarn.maxAppAttempts=1',
            '--conf', 'spark.executorEnv.LD_LIBRARY_PATH=' + os.environ['LIB_JVM'] + ':' + os.environ['LIB_HDFS'],
            '--conf', 'spark.executorEnv.CLASSPATH=' + os.environ['CLASSPATH'],
            '--conf', 'spark.executorEnv.LIB_HDFS=' + os.environ['LIB_HDFS'],
            '--conf', 'spark.executorEnv.LIB_JVM=' + os.environ['LIB_JVM'],
            '--conf', 'spark.yarn.appMasterEnv.PYSPARK_PYTHON=' + os.environ['PYSPARK_PYTHON'],
            '--conf', 'spark.pyspark.python=' + os.environ['PYSPARK_PYTHON'],
            '--conf', 'spark.yarn.appMasterEnv.PYTHONPATH=' + os.environ['PYSPARK_PYTHON'],
            '--conf', 'spark.executorEnv.SPARK_YARN_USER_ENV=' + os.environ['SPARK_YARN_USER_ENV'],
        ]
        
        if archives:
            command.extend(['--archives', archives])

        if libs:
            command.extend(['--py-files', libs])

        command.append(entry)

        if appParams:
            command.extend(appParams)

        cmdStr = ' '.join(command)
        su.append(cmdStr)
        subprocess.Popen(su)

        return

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