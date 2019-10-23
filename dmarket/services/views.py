from django.shortcuts import render
from django.http import HttpResponse
from .models import * 
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
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
            success = initial_credit(request)
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
    context['message'] = 'Remove machine API'

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
    job.user = User.objects.get(id=request.user.id)
    job.status = 'new'
    job.save()
    
    context['status'] = True
    context['error_code'] = 0
    context['message'] = "job {} create successfully, all jobs:{}".format(job.job_id, Job.objects.all())

    return render(request, 'general_status.json', context, 
        content_type='application/json')
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
    context['status'] = True
    context['error_code'] = 0
    context['message'] = 'Get log API'

    return render(request, 'general_status.json', context, 
        content_type='application/json')

##### Credit API #####

def initial_credit(request):
    try:
        credit = Credit()
        credit.sharing_credit = 15
        credit.using_credit = 0
        credit.rate = 0.0
        credit.user = User.objects.get(id=request.user.id)
        credit.save()
    except:
        return False
    return True

@login_required
def check_credit(request):
    credit_info = Credit.objects.all().get(user=request.user)   
    
    context = {}
    context['status'] = True
    context['error_code'] = 0
    context['credit_status'] = credit_info
    context['message'] = 'Get sharing credit info'

    return render(request, 'credit_status.json', context, 
        content_type='application/json')

# Need to discuss the pass in API of update credit
# @login_required
# def update_credit(request):
#     credit_info = Credit.objects.all().get(user=request.user)   
    
#     context = {}
#     context['status'] = True
#     context['error_code'] = 0
#     context['credit_status'] = credit_info['sharing_credit']
#     context['message'] = 'Get sharing credit info'

#     return render(request, 'credit_status.json', context, 
#         content_type='application/json')

