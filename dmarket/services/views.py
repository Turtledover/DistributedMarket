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
import datetime

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

# def login(request):
#     context = {}
#     context['status'] = True
#     context['error_code'] = 0
#     context['message'] = 'User login API'

#     return render(request, 'general_status.json', context, 
#         content_type='application/json')

##### Machine API #####
@login_required
def submit_machine(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Submit machine API'

    return render(request, 'general_status.json', context, 
        content_type='application/json')
@login_required
def remove_machine(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'user: {}'.format(request.user.username)

    id = request.GET.get('machine_id')
    machine = Machine.objects.get(machine_id=id)
    if machine.user != request.user:
        context['status'] = False
        context['message'] = 'No permission to remove this machine'
    else:
        machine.delete()

    return render(request, 'general_status.json', context, 
        content_type='application/json')
@login_required
def list_machines(request):
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'List machine API'

    all_machines = Machine.objects.all()
    context['list'] = all_machines

    return render(request, 'general_status.json', context, 
        content_type='application/json')

##### Job API #####
@login_required
def submit_job(request):
    context = {}        
    if not CreditCore.isSufficient(request):
        context['status'] = False
        context['error_code'] = 2
        context['message'] = 'no enough credit to submit a new job'
        return JsonResponse(context)

    if not 'entry_file' in request.GET:
        context['status'] = False
        context['error_code'] = 1
        context['message'] = 'missing mandatory parameter: entry_file'
        return JsonResponse(context)

    user = User.objects.get(id=request.user.id)
    # TODO: call credit is_sufficient_credit function

    job = Job()
    
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
    job.save()
    
    context['status'] = True
    context['error_code'] = 0
    context['result'] = {
        'job_id': job.job_id
    }
    # context['message'] = 'job {} create successfully'.format(job.job_id)

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
    context['result'] = {}
    context['result']['job_id'] = jobId
    context['result']['name'] = job.job_name
    context['result']['status'] = job.status
    context['result']['used_credits'] = job.used_credits
    context['result']['duration'] = job.duration
    context['result']['added'] = job.added_time
    context['result']['spark_id'] = job.spark_id

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

    # TODO: parse the logs from HTML
    for a in app['attempts']:
        att_id = a['attemptId']
        logslist = Spark.get_attempts_executors_log(job.spark_id, att_id)
        alllogs.append(logslist)

    context['status'] = True
    context['error_code'] = 0
    context['result'] = {
        'logs': alllogs
    }

    return JsonResponse(context)

##### Credit API #####

@login_required
def check_credit(request):
    user = request.user
    
    credit = Credit.objects.get(user=request.user)
    
    jobs = Job.objects.filter(user=request.user)  

    job_list = []
    for job in jobs:
        job_dict = {}
        if job.status is not 'running':
            continue;
        for machine in job:
            job_dict[machine_type] = 1
            job_dict[num_of_cores] = 1
            job_dict[duration] = job.duration
            job_list.append(job_dict)
    using_credit = CreditCore.update_usings(user, job_list, real_update=False)

    machine_list = []
    machines = Machine.objects.filter(user=request.user)

    for machine in machines:
        machine_dict = {}   
        machine_dict[machine_type] = machine.machine_type
        machine_dict[num_of_cores] = machine.core_num
        machine_dict[duration] = int(datetime.datetime.now().strftime("%s")) * 1000 - machine.start_time
        machine_list.append(machine_dict)
    sharing_credit = CreditCore.update_sharings(user, machine_list, real_update=False)
    
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

    return render(request, 'credit_status.json', context, 
        content_type='application/json')

