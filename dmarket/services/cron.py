import subprocess
from django_cron import CronJobBase, Schedule
from django.utils.timezone import now, localtime
from django.core.files import File
from django.db.models import Q
from services.corelib.spark import *
from .models import *
import requests
import sys
from services.corelib.jobhelper import *
from .credit.credit_core import CreditCore
from .corelib.machinelib import MachineLib


class SubmitJobCron(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.submit_job_cron' # a unique code

    def do(self):
        print('cron run', file=sys.stderr)

        new_jobs = Job.objects.filter(status='new')
        if len(new_jobs) == 0:
            return
        job = new_jobs.first()
        job.status = 'pending'
        job.save()

        # TODO: check all the files does exist in HDFS.
        # TODO: check all the files are accessible by the user.

        try:
            Spark.submitJob(
                job.user.username, 
                job.job_id,
                job.entry_file,
                job.libs,
                job.archives,
                job.app_params
            )
        except Exception as e:
            print('exeption', file=sys.stderr)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message, file=sys.stderr)

        return

class ScanFinishedJobCron(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.scan_finished_job_cron' # a unique code

    spark_status_url = 'http://127.0.0.1:18080/api/v1/applications/'

    def do(self):
        jobs = Job.objects.filter(Q(status='finished') | Q(status='failed') | Q(status='killed'))

        for j in jobs:
            self.complete_job(j)
        
        return
    
    def complete_job(self, job):
        spark_id = job.spark_id

        if not spark_id and job.status == 'failed':
            self.update_submit_fail_job(job)
            return

        app = Spark.get_spark_app(spark_id)
        print(app, file=sys.stderr)
        if app is None or not 'attempts' in app:
            if job.status == 'failed' or job.status == 'killed':
                self.update_submit_fail_job(job)
            return

        start_time = 0
        end_time = 0
        for a in app['attempts']:
            if start_time == 0 or a['startTimeEpoch'] < start_time:
                start_time = a['startTimeEpoch']

            if end_time == 0 or a['lastUpdatedEpoch'] > end_time:
                end_time = a['lastUpdatedEpoch']

        machines = get_spark_app_machine_usage(spark_id, app)

        used_credit = CreditCore.update_using(job.user, machines, job, True)
        print('used_credit=' + str(used_credit), file=sys.stderr)
        job.start_time = start_time
        job.end_time = end_time
        job.duration = (end_time - start_time) / 1000 # Make it seconds
        job.used_credits = used_credit
        if job.status == 'finished':
            job.status = 'completed'
        elif job.status == 'killed':
            job.status = 'kill_completed'
        else:
            job.status = 'fail_completed'
        job.save()
        return

    def update_submit_fail_job(self, job):
        job.used_credits = 0
        if job.status == 'killed':
            job.status = 'kill_completed'
        else:
            job.status = 'fail_completed'
        job.save()
        return


class ScanAddMachine(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.add_machine_cron' # a unique code

    def do(self):
        print('cron run ScanAddMachine', file=sys.stderr)

        machine_intervals = MachineInterval.objects.filter(status="Down").order_by('start_time')
        if len(machine_intervals) == 0:
            return
        
        
        machine_interval = machine_intervals.first()

        if machine_interval.start_time > localtime().time():
            print("start time > now", "start_time:", machine_interval.start_time, "now:", localtime().time(), file=sys.stderr)
            return
        
        
        # TODO: check all the files does exist in HDFS.
        # TODO: check all the files are accessible by the user.

        try:
            print("machine_id", machine_interval.machine.machine_id)
            self.test_add_machine(machine_interval.machine.machine_id)
            machine_interval.status = 'Up'
            machine_interval.save()
            print("machine_interval to Up", machine_interval)
        except Exception as e:
            print('exeption', file=sys.stderr)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message, file=sys.stderr)
        return

    def test_add_machine(self, machine_id):
        machines = Machine.objects.filter(machine_id=machine_id)
        context = {}
        if not machines:
            context['status'] = False
            context['error_code'] = 1
            context['message'] = 'The requested machine does not exist.'
            return context
        
        machine = machines[0]
        ssh_session = subprocess.Popen(
            ['ssh', '-o', 'StrictHostKeyChecking=no', machine.hostname],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        ssh_session.stdin.write("echo 'test' > test.txt\n".encode('utf-8'))
        ssh_session.stdin.write(
            "/usr/local/hadoop/bin/yarn --daemon start nodemanager\n".encode('utf-8'))
        ssh_session.stdin.write(
            "/usr/local/hadoop/bin/hdfs --daemon start datanode\n".encode('utf-8'))
        context['message'] = ssh_session.stdout
        ssh_session.stdin.close()
        MachineLib.operate_machine(machine.hostname, MachineLib.MachineOp.ADD)
        context['status'] = True
        context['error_code'] = 0
        return context

class ScanRemoveMachine(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.remove_machine_cron' # a unique code

    def do(self):
        print('cron run ScanRemoveMachine')

        machine_intervals = MachineInterval.objects.filter(status="Up").order_by('end_time')
        if len(machine_intervals) == 0:
            return

        
        machine_interval = machine_intervals.first()

        if machine_interval.end_time > localtime().time():
            print("end time > now", "end_time:", machine_interval.end_time, "now:", localtime().time())
            return
        

        # TODO: check all the files does exist in HDFS.
        # TODO: check all the files are accessible by the user.

        try:
            print("machine_id", machine_interval.machine.machine_id)
            self.test_remove_machine(machine_interval.machine.machine_id)
            machine_interval.status = 'Down'
            machine_interval.save()
            print("machine_interval to Down", machine_interval)
        except Exception as e:
            print('exeption', file=sys.stderr)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message, file=sys.stderr)

        return

    def test_remove_machine(self, machine_id):
        machines = Machine.objects.filter(machine_id=machine_id)
        context = {}
        if not machines:
            context['status'] = False
            context['error_code'] = 1
            context['message'] = 'The requested machine does not exist.'
            return context
        
        machine = machines[0]
        print("machine.hostname", machine.hostname)
        ssh_session = subprocess.Popen(
            ['ssh', '-o', 'StrictHostKeyChecking=no', machine.hostname],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        ssh_session.stdin.write(
            "/usr/local/hadoop/bin/yarn --daemon stop nodemanager\n".encode('utf-8'))
        
        ssh_session.stdin.write(
            "/usr/local/hadoop/bin/hdfs --daemon stop datanode\n".encode('utf-8'))
        context['message'] = ssh_session.stdout
        ssh_session.stdin.close()
        MachineLib.operate_machine(machine.hostname, MachineLib.MachineOp.REMOVE)
        context['status'] = True
        context['error_code'] = 0
        return context