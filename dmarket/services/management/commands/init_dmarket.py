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

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-email', required=False)
        parser.add_argument('-password', required=False)

    def handle(self, *args, **options):
        existing_users = User.objects.filter(username='admin')
        if existing_users:
            self.stdout.write('admin user exist, nothing to do.')
            return
        
        if len(Machine.objects.filter(hostname='master1')) > 0:
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
        self.create_machine(adminUser)
    
    def create_machine(self, adminUser):
        # The ways to access the machine data is cited from
        # https://www.pythoncircle.com/post/535/python-script-9-getting-system-information-in-linux-using-python-script/
        # https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python
        # https://stackoverflow.com/questions/22102999/get-total-physical-memory-in-python/28161352
        # https://www.geeksforgeeks.org/display-hostname-ip-address-python/
        # begin
        if len(Machine.objects.filter(hostname='master1')) > 0:
            # Could not happen
            raise

        core_num = os.cpu_count()
        memory_size = psutil.virtual_memory().total
        # [TBD] Get the real ip address
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        public_key = File(open(os.path.join(settings.MEDIA_ROOT, Constants.MASTER_PUBKEY_PATH)))
        public_key.name = Constants.MASTER_PUBKEY_PATH
        master = Machine(ip_address=ip_address, memory_size=memory_size, core_num=core_num,
                        time_period=Constants.MASTER_AVAILABLE_TIME, user=adminUser,
                        public_key=public_key, hostname='master1')
        master.save()
