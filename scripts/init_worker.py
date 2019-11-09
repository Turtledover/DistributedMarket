import os
import socket
import subprocess
import argparse
import xml.etree.ElementTree as ET


def basic_env_setup():
    """
    Install the required packages on the user machine
    :return:
    """
    commands = [
        ['apt-get', 'update'],
        ['apt-get', '-y', 'dist-upgrade'],
        ['apt-get', 'install', 'openjdk-8-jdk', 'openssh-server', 'openssh-client', 'python3-pip', 'zip', '-y'],
        # [TBD] Check if keys have already existed:
        ['ssh-keygen', '-t', 'rsa', '-N', '', '-f', '/root/.ssh/id_rsa'],
        ['service', 'ssh', 'start'],
        ['pip3', 'install', 'psutil', 'requests'],
    ]
    for command in commands:
        subprocess.Popen(command).wait()
    print("[INFO] finish basic_env_setup")


def cluster_setup():
    """
    Set up the environment variables required for the cluster including Hadoop, Spark, Yarn, Tensorflow, and TensorflowOnSpark
    :return:
    """
    scp_commands = [
        ['scp', '-o', 'StrictHostKeyChecking=no', '-r', 'master:/usr/local/hadoop', '/usr/local/hadoop'],
        ['scp', '-o', 'StrictHostKeyChecking=no', '-r', 'master:/usr/local/spark', '/usr/local/spark'],
    ]
    for command in scp_commands:
        subprocess.Popen(command).wait()

    print("[INFO] finish scp")

    envs = {
        'PATH': '{0}:/usr/local/hadoop/bin:/usr/local/hadoop/sbin:/usr/local/spark/bin'.format(os.environ['PATH']),
        'HADOOP_HOME': '/usr/local/hadoop',
        'JAVA_HOME': '/usr/lib/jvm/java-8-openjdk-amd64',
        'SPARK_HOME': '/usr/local/spark',
        'PYSPARK_PYTHON': '/usr/bin/python3.6',
        'SPARK_YARN_USER_ENV': 'PYSPARK_PYTHON=/usr/bin/python3.6',
        'LIB_HDFS': '/usr/local/hadoop/lib/native',
        'LIB_JVM': '$JAVA_HOME/jre/lib/amd64/server',
    }
    for key in envs:
        os.environ[key] = envs[key]
    extra_envs = {
        'HADOOP_CONF_DIR': '{0}/etc/hadoop'.format(os.environ['HADOOP_HOME']),
        'LD_LIBRARY_PATH': '{0}:{1}'.format(os.environ['LIB_HDFS'], os.environ['LIB_JVM']),
    }
    for key in extra_envs:
        os.environ[key] = extra_envs[key]

    os.environ['CLASSPATH'] = subprocess.check_output(['hadoop', 'classpath', '--glob']).decode().strip('\n')
    envs['CLASSPATH'] = os.environ['CLASSPATH']
    print("[INFO] finish python env setup")
    print(os.environ)

    rm_commands = [
        ['rm', '-rf', os.path.join(os.environ['HADOOP_HOME'], 'data/dataNode/')],
        ['rm', '-rf', os.path.join(os.environ['HADOOP_HOME'], 'logs')],
    ]
    for rm_command in rm_commands:
        subprocess.Popen(rm_command).wait()
    print("[INFO] finish remove the logs and old dataNode directory")

    with open('/root/.bashrc', 'a') as f:
        for key in envs:
            f.write('{0}={1}\n'.format(key, envs[key]))
    with open('/root/.bash_profile', 'a') as f:
        for key in envs:
            f.write('{0}={1}\n'.format(key, envs[key]))
    print("[INFO] finish bash env setup")


def config_yarn_resources(cpu_cores_limit, memory_limit):
    """
    :param int cpu_cores_limit:
    :param int memory_limit: In MB
    :return:
    """
    # https://docs.python.org/3.7/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
    # begin
    yarn_config_path = os.path.join(os.environ['HADOOP_CONF_DIR'], 'yarn-site.xml')
    yarn_config = ET.parse(yarn_config_path)
    root = yarn_config.getroot()
    # [TBD] Check if the memory & cpu limit values have already existed
    memory_config = ET.Element('property')
    memory_config_name = ET.SubElement(memory_config, 'name')
    memory_config_name.text = 'yarn.nodemanager.resource.memory-mb'
    memory_config_value = ET.SubElement(memory_config, 'value')
    memory_config_value.text = str(memory_limit)
    root.append(memory_config)
    cpu_config = ET.Element('property')
    cpu_config_name = ET.SubElement(cpu_config, 'name')
    cpu_config_name.text = 'yarn.nodemanager.resource.cpu-vcores'
    cpu_config_value = ET.SubElement(cpu_config, 'value')
    cpu_config_value.text = str(cpu_cores_limit)
    root.append(cpu_config)
    yarn_config.write(yarn_config_path)
    print("[INFO] finish the yarn config setup")
    hadoop_commands = [
        ['hdfs', '--daemon', 'start', 'datanode'],
        ['yarn', '--daemon', 'start', 'nodemanager'],
    ]
    for command in hadoop_commands:
        subprocess.Popen(command).wait()
    print("[INFO] finish the daemon launching")
    # end


def register_machine(core_num, memory_size, time_period, public_key_path, authorized_key_path, session_id, csrf_token):
    """
    Register the user machine on the existing cluster.
    :param core_num:
    :param memory_size:
    :param time_period:
    :param public_key_path:
    :param authorized_key_path:
    :return:
    """
    import psutil
    import requests
    # The ways to access the machine data is cited from
    # https://www.pythoncircle.com/post/535/python-script-9-getting-system-information-in-linux-using-python-script/
    # https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python
    # https://stackoverflow.com/questions/22102999/get-total-physical-memory-in-python/28161352
    # begin

    core_limit = os.cpu_count()
    assert core_num <= core_limit
    memory_limit = psutil.virtual_memory().total  # in Bytes
    assert memory_size <= memory_limit

    # TBD: There should be a user assigned to these three initial machines.

    # https://stackoverflow.com/questions/22567306/python-requests-file-upload
    # https://stackoverflow.com/questions/13567507/passing-csrftoken-with-python-requests
    # https://www.geeksforgeeks.org/display-hostname-ip-address-python/
    # begin
    url = 'http://master:8000/services/machine/submit/'
    client = requests.session()
    # client.get(url)
    # if 'csrftoken' in client.cookies:
    #     csrf_token = client.cookies['csrftoken']
    # else:
    #     csrf_token = client.cookies['csrf']
    files = {
        'public_key': open(public_key_path, 'r')
    }
    # [TBD] Get the real ip address (Docker version different from the real machine)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    data = {
        'ip_address': ip_address,
        'core_num': core_num,
        'memory_size': memory_size,
        'time_period': time_period,
        # 'csrftoken': csrf_token,
    }
    response = client.post(url, data=data, files=files, headers=dict(Referer=url))
    public_keys = response.json()['public_keys']
    with open(authorized_key_path, 'a') as f:
        for public_key in public_keys:
            f.write(public_key)
    host_ip_mapping = response.json()['host_ip_mapping']
    with open('/etc/hosts', 'a') as f:
        for host in host_ip_mapping:
            f.write('{0}\t{1}\n'.format(host_ip_mapping[host], host))
    # end
    # end


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize the worker server.')
    parser.add_argument('--cpu-cores', type=int, help='The number of cpu cores to be contributed to the cluster.',
                        required=True)
    parser.add_argument('--memory-size', type=int, help='The memory size to be contributed to the cluster.',
                        required=True)
    parser.add_argument('--session-id', type=str, help='The id of the current user session.',
                        required=True)
    parser.add_argument('--csrf-token', type=str, help='The csrf_token for the purpose of security.',
                        required=True)
    args = vars(parser.parse_args())

    basic_env_setup()
    register_machine(args['cpu_cores'], args['memory_size'], 10, '/root/.ssh/id_rsa.pub', '/root/.ssh/authorized_keys',
                     args['session_id'], args['csrf_token'])
    cluster_setup()
    config_yarn_resources(args['cpu_cores'], args['memory_size'])
