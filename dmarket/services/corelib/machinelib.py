import os
import logging
from enum import Enum


class MachineLib:

    class MachineOp(Enum):
        ADD = 'add'
        REMOVE = 'remove'

    @staticmethod
    def read_conf_as_set(path):
        """
        Read the configuration file and parse the content as a set.
        :param string path: path to the config file
        :return: a set of the entries in the config file
        """
        conf = set()
        with open(path, 'r') as f:
            entries = f.readlines()
            for entry in entries:
                conf.add(entry.strip('\n'))
        return conf

    @staticmethod
    def write_set_to_conf(path, confs):
        """
        Write the configurations into the target path.
        :param string path: path to the config file
        :param set<string> confs: a set of the configuration entries
        :return:
        """
        with open(path, 'w') as f:
            for conf in confs:
                f.write(conf + '\n')

    @staticmethod
    def operate_machine(machine_host, machine_op):
        """
        Add/Remove a machine to/from a cluster.
        Note that this method is expected to be called only by the master server.
        :param string machine_host: the host of the target machine
        :param MachineOp machine_op: the target operation of the machine
        :return:
        """
        if machine_op == MachineLib.MachineOp.ADD:
            logging.info('Add a new machine.')
        elif machine_op == MachineLib.MachineOp.REMOVE:
            logging.info('Remove an old machine.')
        else:
            logging.warning('Unsupported machine operations!')
            return

        hadoop_workers_path = os.path.join(os.environ['HADOOP_CONF_DIR'], 'workers')
        hadoop_workers = MachineLib.read_conf_as_set(hadoop_workers_path)
        if machine_op == MachineLib.MachineOp.ADD:
            hadoop_workers.add(machine_host)
        elif machine_op == MachineLib.MachineOp.REMOVE:
            hadoop_workers.remove(machine_host)
        MachineLib.write_set_to_conf(hadoop_workers_path, hadoop_workers)

        spark_slaves_path = os.path.join(os.environ['SPARK_HOME'], 'conf/slaves')
        spark_slaves = MachineLib.read_conf_as_set(spark_slaves_path)
        if machine_op == MachineLib.MachineOp.ADD:
            spark_slaves.add(machine_host)
        elif machine_op == MachineLib.MachineOp.REMOVE:
            spark_slaves.remove(machine_host)
        MachineLib.write_set_to_conf(spark_slaves_path, spark_slaves)
