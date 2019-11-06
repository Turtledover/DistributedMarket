from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.db import models
from .corelib.machinelib import MachineLib
from .constants import *
import subprocess
import psutil
import os
import socket


##### User API #####

def index(request):
    return HttpResponse("Hello, world. Distributed Market.")


def register(request):
    username = request.GET['username']
    email = request.GET['email']
    password = request.GET['password']
    user = User.objects.create_user(username, email, password)
    user.save()

    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = User.objects.all()

    return render(request, 'general_status.json', context,
                  content_type='application/json')


def login(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'User login API'

    return render(request, 'general_status.json', context,
                  content_type='application/json')


##### Machine API #####
@csrf_exempt
def init_cluster(request):
    print("hahaha===>")
    # [TBD] Register an admin user
    # https://stackoverflow.com/questions/10372877/how-to-create-a-user-in-django
    # https://stackoverflow.com/questions/45044691/how-to-serializejson-filefield-in-django
    # begin
    existing_users = User.objects.filter(username='tmp')
    if not existing_users:
        tmp_user = User.objects.create_user('tmp', 'tmp@tmp.com', 'tmp')
        tmp_user.save()
    else:
        tmp_user = existing_users[0]
    # end
    # The ways to access the machine data is cited from
    # https://www.pythoncircle.com/post/535/python-script-9-getting-system-information-in-linux-using-python-script/
    # https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python
    # https://stackoverflow.com/questions/22102999/get-total-physical-memory-in-python/28161352
    # https://www.geeksforgeeks.org/display-hostname-ip-address-python/
    # begin
    if len(Machine.objects.filter(hostname='master')) > 0:
        return JsonResponse("The master node has existed.", safe=False)

    core_num = os.cpu_count()
    memory_size = psutil.virtual_memory().total
    # [TBD] Get the real ip address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    public_key = File(open(Constants.MASTER_PUBKEY_PATH))
    master = Machine(ip_address=ip_address, memory_size=memory_size, core_num=core_num,
                     time_period=Constants.MASTER_AVAILABLE_TIME, user=tmp_user,
                     public_key=public_key, hostname='master')
    master.save()
    return JsonResponse("Success!", safe=False)
    # end


@csrf_exempt
def submit_machine(request):
    if request.method == "GET":
        return HttpResponse('Bad Request!')

    # https://stackoverflow.com/questions/10372877/how-to-create-a-user-in-django
    # https://stackoverflow.com/questions/45044691/how-to-serializejson-filefield-in-django
    # begin
    existing_users = User.objects.filter(username='tmp')
    if not existing_users:
        tmp_user = User.objects.create_user('tmp', 'tmp@tmp.com', 'tmp')
        tmp_user.save()
    else:
        tmp_user = existing_users[0]

    data = request.POST
    public_keys = []
    host_ip_mapping = {}
    if not Machine.objects.filter(ip_address=data['ip_address']):
        new_machine = Machine(ip_address=data['ip_address'], core_num=data['core_num'],
                              memory_size=data['memory_size'], time_period=data['time_period'],
                              user=tmp_user)
        new_machine.public_key = request.FILES['public_key']
        new_machine.save()
        new_machine.hostname = 'slave{0}'.format(new_machine.machine_id)
        new_machine.save()
        MachineLib.add_new_machine(new_machine.hostname)

        # Add the public key to the authorized keys of the master node
        with open('/root/.ssh/authorized_keys', 'a') as f:
            f.write(new_machine.public_key.read().decode())
        with open('/etc/hosts', 'a') as f:
            f.write('{0}\t{1}\n'.format(new_machine.ip_address, new_machine.hostname))

        existing_machines = Machine.objects.all()
        for machine in existing_machines:
            public_keys.append(machine.public_key.read().decode())
            host_ip_mapping[machine.hostname] = machine.ip_address
            if machine.ip_address != new_machine.ip_address and machine.hostname != 'master':
                # Add all the public key and host info of the new machine to other servers in the current cluster
                # https://stackoverflow.com/questions/19900754/python-subprocess-run-multiple-shell-commands-over-ssh
                # begin
                ssh_session = subprocess.Popen(
                    ['ssh', '-o', 'StrictHostKeyChecking=no', machine.hostname],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                ssh_session.stdin.write(
                    "echo '{0}\t{1}\n' >> /etc/hosts\n".format(new_machine.ip_address, new_machine.hostname).encode(
                        'utf-8'))
                ssh_session.stdin.write(
                    "echo '{0}' >> ~/.ssh/id_rsa.pub\n".format(new_machine.public_key.read().decode()).encode('utf-8'))
                ssh_session.stdin.close()
                # end

    # end
    return JsonResponse({'public_keys': public_keys,
                         'host_ip_mapping': host_ip_mapping}, safe=False)


def remove_machine(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Remove machine API'

    return render(request, 'general_status.json', context,
                  content_type='application/json')


def list_machines(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'List machine API'

    return render(request, 'general_status.json', context,
                  content_type='application/json')


##### Job API #####
def submit_job(request):
    context = {}
    if not 'entry_file' in request.GET:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'missing mandatory parameter: entry_file'
        return render(request, 'general_status.json', context,
                      content_type='application/json')

    job = Job()
    # job.root_path = request.GET['root_path']

    # TODO: sanitize parameters
    if 'libs' in request.GET:
        job.libs = request.GET['libs']

    if 'archives' in request.GET:
        job.archives = request.GET['archives']

    if 'app_params' in request.GET:
        job.app_params = request.GET['app_params']

    job.entry_file = request.GET['entry_file']

    job.core_num = int(request.GET['core_num'])
    job.user = User.objects.get(id=request.GET['id'])
    job.status = 'new'
    job.save()

    context['status'] = True
    context['error_code'] = 0
    context['message'] = "job {} create successfully, all jobs:{}".format(job.job_id, Job.objects.all())

    return render(request, 'general_status.json', context,
                  content_type='application/json')


def cancel_job(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Cancel job API'

    return render(request, 'general_status.json', context,
                  content_type='application/json')


def get_result(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Get result API'

    return render(request, 'general_status.json', context,
                  content_type='application/json')


def get_log(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Get log API'

    return render(request, 'general_status.json', context,
                  content_type='application/json')


##### Credit API #####
def get_credit(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Get credit API'

    return render(request, 'general_status.json', context,
                  content_type='application/json')
