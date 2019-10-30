import os
import socket
import subprocess
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
        ['ssh-keygen', '-t', 'rsa', '-N', '""', '-f', '~/.ssh/id_rsa'],
        ['service', 'ssh', 'start'],
        ['pip3', 'install', 'psutil', 'requests'],
    ]
    for command in commands:
        subprocess.Popen(command).wait()


def cluster_setup():
    """
    Set up the environment variables required for the cluster including Hadoop, Spark, Yarn, Tensorflow, and TensorflowOnSpark
    :return:
    """
    hadoop_spark_envs = [
        'PATH=$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin:/usr/local/spark/bin',
        'HADOOP_HOME="/usr/local/hadoop"',
        'HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"',
        'JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64',
        'HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop',
        'SPARK_HOME=/usr/local/spark',
    ]
    tensorflow_on_spark_envs = [
        'PYSPARK_PYTHON=/usr/bin/python3.6',
        'SPARK_YARN_USER_ENV="PYSPARK_PYTHON=/usr/bin/python3.6"',
        'LIB_HDFS=/usr/local/hadoop/lib/native',
        'LIB_JVM=$JAVA_HOME/jre/lib/amd64/server',
        'LD_LIBRARY_PATH=${LIB_HDFS}:${LIB_JVM}',
        'CLASSPATH=$(hadoop classpath --glob)',
    ]
    activate_envs = ['source', '~/.bash_profile']
    commands = [
        ['scp -r master:/usr/local/hadoop /usr/local/hadoop'],
        ['scp -r master:/usr/local/spark /usr/local/spark'],
    ]
    commands += [['echo', env, '>>', '~/.bash_profile'] for env in hadoop_spark_envs]
    commands.append(activate_envs)
    commands += [['echo', env, '>>', '~/.bash_profile'] for env in tensorflow_on_spark_envs]
    commands += [
        activate_envs,
        ['hdfs', '--daemon', 'start'],
        ['yarn', '--daemon', 'start', 'nodemanager'],
    ]
    for command in commands:
        subprocess.Popen(command).wait()


def config_yarn_resources(memory_limit, cpu_cores_limit):
    """
    :param int memory_limit: In MB
    :param int cpu_cores_limit:
    :return:
    """
    # https://docs.python.org/3.7/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
    # begin
    yarn_config_path = os.path.join(os.environ['HADOOP_CONF_DIR'], 'yarn-site.xml')
    yarn_config = ET.parse(yarn_config_path)
    root = yarn_config.getroot()
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
    # end


def register_machine(core_num, memory_size, time_period, public_key_path, authorized_key_path):
    """
    Register the user machine on the existing cluster.
    :param core_num:
    :param memory_size:
    :param time_period:
    :param public_key_path:
    :param authorized_key_path:
    :param target_hostname:
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
    memory_limit = psutil.virtual_memory().total    # in Bytes
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
    core_num = 1
    memory_size = 1024
    # [TBD] Regular user should first register a user account on our app before register their machine
    # basic_env_setup()
    # register_machine(core_num, memory_size, 10, '/root/.ssh/id_rsa.pub', '/root/.ssh/authorized_keys')
    cluster_setup()
    config_yarn_resources(core_num, memory_size)

