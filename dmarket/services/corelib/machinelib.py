import os


class MachineLib:

    @staticmethod
    def add_new_machine(new_machine_host):
        """
        Note: This method can only work on master node
        :param new_machine_host:
        :return:
        """
        print('[function] add_new_machine')
        hadoop_workers = set()
        hadoop_workers_path = os.path.join(os.environ['HADOOP_CONF_DIR'], 'workers')
        with open(hadoop_workers_path, 'r') as f:
            entries = f.readlines()
            for entry in entries:
                hadoop_workers.add(entry.strip('\n'))
        hadoop_workers.add(new_machine_host)
        with open(hadoop_workers_path, 'w') as f:
            for hadoop_worker in hadoop_workers:
                f.write(hadoop_worker + '\n')

        spark_slaves = set()
        spark_slaves_path = os.path.join(os.environ['SPARK_HOME'], 'conf/slaves')
        with open(spark_slaves_path, 'r') as f:
            entries = f.readlines()
            for entry in entries:
                spark_slaves.add(entry.strip('\n'))
        spark_slaves.add(new_machine_host)
        with open(spark_slaves_path, 'w') as f:
            for spark_slave in spark_slaves:
                f.write(spark_slave + '\n')

    @staticmethod
    def remove_machine(machine_host):
        hadoop_workers = set()
        hadoop_workers_path = os.path.join(os.environ['HADOOP_CONF_DIR'], 'workers')
        with open(hadoop_workers_path, 'r') as f:
            entries = f.readlines()
            for entry in entries:
                hadoop_workers.add(entry)
        hadoop_workers.remove(machine_host + '\n')
        with open(hadoop_workers_path, 'w') as f:
            for hadoop_worker in hadoop_workers:
                f.write(hadoop_worker)

        spark_slaves = set()
        spark_slaves_path = os.path.join(os.environ['SPARK_HOME'], 'conf/slaves')
        with open(spark_slaves_path, 'r') as f:
            entries = f.readlines()
            for entry in entries:
                spark_slaves.add(entry)
        spark_slaves.remove(machine_host + '\n')
        with open(spark_slaves_path, 'w') as f:
            for spark_slave in spark_slaves:
                f.write(spark_slave)
