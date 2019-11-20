from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .cron import *
from .spark.spark import *
from .credit.credit_core import CreditCore
from .jobhelper import *
import datetime
import sys

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
@login_required
def index(request):
    return HttpResponse("Hello {}, world. Distributed Market.".format(request.user.id))
# https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            creditCore = CreditCore()
            success = creditCore.initial_credit(user)
            if not success:
                print("initial failure!")
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = User.objects.all()

    return render(request, 'general_status.json', context, 
        content_type='application/json')


# def login(request):
#     context = {}
#     context['status'] = True
#     context['error_code'] = 0
#     context['message'] = 'User login API'
#
#     return render(request, 'general_status.json', context,
#         content_type='application/json')


##### Machine API #####
@csrf_exempt
def init_cluster(request):
    # TODO Register an admin user
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
    # TODO Get the real ip address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    public_key = File(open(Constants.MASTER_PUBKEY_PATH))
    master = Machine(ip_address=ip_address, memory_size=memory_size, core_num=core_num,
                     time_period=Constants.MASTER_AVAILABLE_TIME, user=tmp_user,
                     public_key=public_key, hostname='master')
    master.save()
    return JsonResponse("Success!", safe=False)
    # end


@login_required
def submit_machine(request):
    if request.method == "GET":
        return HttpResponse('Bad Request!')

    # https://stackoverflow.com/questions/10372877/how-to-create-a-user-in-django
    # https://stackoverflow.com/questions/45044691/how-to-serializejson-filefield-in-django
    # begin
    data = request.POST
    public_keys = []
    host_ip_mapping = {}
    premium_rate = 1 
    if not Machine.objects.filter(ip_address=data['ip_address']):
        new_machine = Machine(ip_address=data['ip_address'], core_num=data['core_num'],
                              memory_size=data['memory_size'], time_period=data['time_period'],
                              user=request.user)
        new_machine.public_key = request.FILES['public_key']
        new_machine.save()
        new_machine.hostname = 'slave{0}'.format(new_machine.machine_id)
        new_machine.save()
        premium_rate = CreditCore.get_price(request)
        new_machine.premium_rate = premium_rate
        new_machine.save()
        MachineLib.operate_machine(new_machine.hostname, MachineLib.MachineOp.ADD)

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
                         'host_ip_mapping': host_ip_mapping,
                         'premium_rate': format(job.premium_rate, '.0%')}, safe=False)


@login_required
def remove_machine(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'user: {0}'.format(request.user.username)

    machines = Machine.objects.filter(machine_id=int(request.POST.get('machine_id')))
    if not machines:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'The requested machine does not exist.'
        return render(request, 'general_status.json', context,
                      content_type='application/json')

    machine = machines[0]
    if machine.user != request.user:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'No permission to remove this machine.'
    else:
        MachineLib.operate_machine(machine.hostname, MachineLib.MachineOp.REMOVE)
        # TODO Remove the public key and hostname-ip map of the old machine from each machine in the existing cluster
        machine_info = {
            'type': machine.machine_type,
            'cores': machine.core_num,
            #credit by lyulinag
            'memory': machine.memory_size,
            'duration': int(datetime.datetime.now().strftime("%s")) - (int)(machine.start_time.strftime("%s"))
        }
        CreditCore.update_sharing(request.user, machine_info, True)
        history = HistoryMachine.create(machine)
        history.user = request.user
        history.save()
        machine.delete()

    return render(request, 'general_status.json', context, 
        content_type='application/json')


@login_required
def list_machines(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    # context['message'] = 'List machine API'

    current_user_machines = Machine.objects.filter(user=request.user)
    # context['list'] = current_user_machines

    mlist = []
    for m in current_user_machines:
        mObj = {}
        mObj['id'] = m.machine_id
        mObj['hostname'] = m.hostname
        mObj['type'] = m.machine_type
        mObj['core_num'] = m.core_num
        mObj['memory'] = m.memory_size
        mObj['starttime'] = m.start_time
        mlist.append(mObj)
    
    context['result'] = {
        'machines': mlist
    }
    
    return  JsonResponse(context)

@login_required
def get_machine_contribution_history(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'get machine contribution history API'

    current_user_history = HistoryMachine.objects.filter(user=request.user)
    context['list'] = current_user_history

    return render(request, 'general_status.json', context,
                  content_type='application/json')


##### Job API #####
@login_required
def submit_job(request):
    context = {}
    if not CreditCore.isSufficient(request):
        context['status'] = False
        context['error_code'] = 2
        context['message'] = 'not enough credit to submit a new job'
        return JsonResponse(context)

    if not 'entry_file' in request.GET:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'missing mandatory parameter: entry_file'
        return JsonResponse(context)

    user = User.objects.get(id=request.user.id)

    job = Job()
    # job.root_path = request.GET['root_path']
    
    # TODO: sanitize parameters
    if 'libs' in request.GET:
        job.libs = request.GET['libs']
    
    if 'archives' in request.GET:
        job.archives = request.GET['archives']
    
    if 'app_params' in request.GET:
        job.app_params = request.GET['app_params']

    if 'name' in request.GET:
        job.job_name = request.GET['name']

    job.entry_file = request.GET['entry_file']

    job.user = user
    job.status = 'new'
    job.premium_rate = CreditCore.get_price(request)
    job.save()
    
    context['status'] = True
    context['error_code'] = 0
    context['result'] = {
        'job_id': job.job_id,
        'premium_rate': format(job.premium_rate, '.0%')
    }

    return JsonResponse(context)

@login_required
def get_job_status(request):
    context = {}
    if not 'job_id' in request.GET:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'missing mandatory parameter: job_id'
        return JsonResponse(context)

    jobId = request.GET['job_id']
    jobs = Job.objects.filter(job_id=jobId)
    if len(jobs) == 0:
        context['status'] = False
        context['error_code'] = 2
        context['message'] = 'No such job'
        return JsonResponse(context)

    job = jobs.first()
    context['status'] = True
    context['error_code'] = 0
    context['result'] = {
        'job_id': jobId,
        'name': job.job_name,
        'status': job.status,
        'used_credits': job.used_credits,
        'duration': job.duration,
        'added': job.added_time,
        'spark_id': job.spark_id
    }

    return JsonResponse(context)

@login_required
def get_job_list(request):
    """
    Get a list of jobs of the requesting users
    Sample response:
    {
        "status": true,
        "error_code": 0,
        "result": {
            "jobs": [
                {
                    "job_id": 1,
                    "name": "",
                    "status": "finished",
                    "used_credits": 45,
                    "duration": 120000,
                    "added": "2019-10-28T18:50:54.147Z"
                },
                {
                    "job_id": 6,
                    "name": "MNIST Training",
                    "status": "running",
                    "used_credits": 0,
                    "duration": 0,
                    "added": "2019-10-28T19:10:41.184Z"
                }
            ]
        }
    }
    """
    context = {}
    jobs = Job.objects.filter(user=request.user)

    result = {}
    result['jobs'] = []
    for j in jobs:
        retj = {}
        retj['job_id'] = j.job_id
        retj['name'] = j.job_name
        retj['status'] = j.status
        retj['used_credits'] = j.used_credits
        retj['duration'] = j.duration
        retj['added'] = j.added_time
        result['jobs'].append(retj)

    context['status'] = True
    context['error_code'] = 0
    context['result'] = result
    return JsonResponse(context)

@login_required
def cancel_job(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Cancel job API'

    return render(request, 'general_status.json', context, 
        content_type='application/json')

@login_required
def get_result(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Get result API'

    return render(request, 'general_status.json', context, 
        content_type='application/json')

@login_required
def get_log(request):
    """
    Get logs, both stdout and stderr, of a job
    Sample response:
    {
        "status": true,
        "error_code": 0,
        "result": {
            "logs": [
                {
                    "attempt": 1,
                    "executors": [
                        {
                            "isDriver": true,
                            "stdout": "logloglogloglog",
                            "stderr": "loglogloglog"
                        },
                        {
                            "isDriver": false,
                            "stdout": "logloglogloglog",
                            "stderr": "loglogloglog"
                        }
                    ]
                },
                {
                    "attempt": 2,
                    "executors": [
                        {
                            "isDriver": true,
                            "stdout": "logloglogloglog",
                            "stderr": "loglogloglog"
                        },
                        {
                            "isDriver": false,
                            "stdout": "logloglogloglog",
                            "stderr": "loglogloglog"
                        }
                    ]
                }
            ]
        }
    }
    """
    context = {}
    if not 'job_id' in request.GET:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'missing mandatory parameter: job_id'
        return JsonResponse(context)

    jobId = request.GET['job_id']
    job_set = Job.objects.filter(job_id=jobId)
    if len(job_set) == 0:
        context['status'] = False
        context['error_code'] = 2
        context['message'] = 'No such job ' + jobId
        return JsonResponse(context)

    job = job_set.first()
    if not job.spark_id:
        context['status'] = True
        context['error_code'] = 0
        context['result'] = {}
        return JsonResponse(context)

    alllogs = []
    app = Spark.get_spark_app(job.spark_id)
    if app is None:
        context['status'] = True
        context['error_code'] = 0
        context['result'] = {}
        return JsonResponse(context)

    for a in app['attempts']:
        att_id = a['attemptId']
        logslist = Spark.get_attempts_executors_log(job.spark_id, att_id)

        execs = []
        for l in logslist:
            out = get_hadoop_log(l['logs']['stdout'])
            err = get_hadoop_log(l['logs']['stderr'])
            exe = {
                'isDriver': l['id'] =='driver',
                'stdout': out,
                'stderr': err
            }
            execs.append(exe)

        item = {
            'attempt': att_id,
            'executors': execs
        }
        alllogs.append(item)

    context['status'] = True
    context['error_code'] = 0
    context['result'] = {
        'logs': alllogs
    }

    return JsonResponse(context)

##### Credit API #####

@login_required
def get_price(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    res = format(CreditCore.get_price(request), '.0%') 
    context['premium_rate'] = res
    return JsonResponse(context)

@login_required
def check_credit(request):
    user = request.user

    credit = Credit.objects.get(user=request.user)

    jobs = Job.objects.filter(user=request.user)

    machiine_list = []
    using_credit = 0
    for job in jobs:
        job_dict = {}
        if job.status is not 'running':
            continue
        executors = get_job_machines_usage(job)
        machiine_list.append(executors)
        using_credit += CreditCore.update_using(user, machiine_list, job, real_update=False)

    machine_list = []
    machines = Machine.objects.filter(user=request.user)
    if machines.exists():
        for machine in machines:
            machine_dict = {}
            machine_dict['type'] = machine.machine_type
            machine_dict['cores'] = machine.core_num
            machine_dict['memory'] = machine.memory_size
            machine_dict['premium_rate'] = machine.premium_rate
            machine_dict['duration'] = int(datetime.datetime.now().strftime("%s")) - (int)(machine.start_time.strftime("%s"))
            machine_list.append(machine_dict)
        sharing_credit = CreditCore.update_sharings(user, machine_list, real_update=False)
    else:
        sharing_credit = 0

    credit.using_credit += using_credit
    credit.sharing_credit += sharing_credit

    context = {}
    context['status'] = True
    context['error_code'] = 0
    # context['credit'] = credit
    context['using_credit'] = credit.using_credit
    context['sharing_credit'] = credit.sharing_credit
    context['rate'] = credit.rate
    context['message'] = 'Get credit info'

    return JsonResponse(context)
    # return render(request, 'credit_status.json', context,
    #     content_type='application/json')

def jobtest(request):
    print('jobtest', file=sys.stderr)
    context = {}
    if not 'job_id' in request.GET:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'missing mandatory parameter: job_id'
        return JsonResponse(context)

    job_id = request.GET['job_id']
    job_set = Job.objects.filter(job_id=job_id)
    if len(job_set) == 0:
        context['status'] = False
        context['error_code'] = 2
        context['message'] = 'No such job ' + job_id
        return JsonResponse(context)

    job = job_set.first()
    usages = get_job_machines_usage(job)

    context['status'] = True
    context['error_code'] = 0
    context['result'] = usages
    return JsonResponse(context)

def completetest(request):
    scan = ScanFinishedJobCron()
    scan.do()
    return JsonResponse({})

def logtest(request):
    url = 'http://slave1:8042/node/containerlogs/container_1572410700786_0001_01_000001/root/stderr?start=-4096'
    data = get_hadoop_log(url)

    context = {}
    context['data'] = data
    return JsonResponse(context)