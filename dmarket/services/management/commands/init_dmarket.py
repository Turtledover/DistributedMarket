from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File
from services.models import *
from services.constants import *
import getpass
import socket
import psutil
import os
import sys
import subprocess
import xml.etree.ElementTree as ET


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-email', required=False)
        parser.add_argument('-password', required=False)
        parser.add_argument('-cpu_cores', type=int, required=False)
        parser.add_argument('-memory_size', type=int, required=False)

    def handle(self, *args, **options):
        existing_users = User.objects.filter(username='admin')
        if existing_users:
            self.stdout.write('admin user exist, nothing to do.')
            return
        
        if len(Machine.objects.filter(hostname=Constants.MASTER_HOST)) > 0:
            # Could not happen
            raise
        
        email = options['email']
        if email is None:
            email = input('Enter your email: ')
        
        password = options['password']
        if password is None:
            password = getpass.getpass()

        self.stdout.write('admin user not exist, creating...')
        adminUser = User.objects.create_user('admin', email, password)
        self.create_machine(adminUser, options['cpu_cores'], options['memory_size'])

    def update_yarn_config(self, memory_limit, cpu_cores_limit):
        print('update_yarn_config')
        subprocess.Popen(['stop-yarn.sh']).wait()
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
        # end
        subprocess.Popen(['start-yarn.sh']).wait()

    def create_machine(self, adminUser, cpu_cores, memory_size):
        # The ways to access the machine data is cited from
        # https://www.pythoncircle.com/post/535/python-script-9-getting-system-information-in-linux-using-python-script/
        # https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python
        # https://stackoverflow.com/questions/22102999/get-total-physical-memory-in-python/28161352
        # https://www.geeksforgeeks.org/display-hostname-ip-address-python/
        # begin
        if len(Machine.objects.filter(hostname=Constants.MASTER_HOST)) > 0:
            # Could not happen
            raise
        print('print stdout')
        print('print stderr', file=sys.stderr)
        core_limit = os.cpu_count()
        if cpu_cores is None:
            cpu_cores = core_limit
        else:
            assert 1 <= cpu_cores <= core_limit
        memory_limit = psutil.virtual_memory().total
        if memory_size is None:
            memory_size = int(memory_limit//1024/1024)
        else:
            assert 1024 <= memory_size <= int(memory_limit//1024/1024)
        self.update_yarn_config(memory_size, cpu_cores)
        # The way to get the ip address of the user machine is cited from
        # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        # begin
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.connect(("8.8.8.8", 80))
        ip_address = my_socket.getsockname()[0]
        my_socket.close()
        # end
        public_key = File(open(os.path.join(settings.MEDIA_ROOT, Constants.MASTER_PUBKEY_PATH)))
        public_key.name = Constants.MASTER_PUBKEY_PATH
        master = Machine(ip_address=ip_address, memory_size=memory_size, core_num=cpu_cores,
                        time_period=Constants.MASTER_AVAILABLE_TIME, user=adminUser,
                        public_key=public_key, hostname=Constants.MASTER_HOST,premium_rate=1)
        master.save()
