from django_cron import CronJobBase, Schedule
from django.core.files import File
from django.db.models import Q
from .spark.spark import *
from .models import *
import requests
import sys

class SubmitJobCron(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.submit_job_cron' # a unique code

    def getUserName(self, job):
        #TODO: get username from database with user id
        return 'root'

    def do(self):
        log = open('/submit-out', 'a+')
        log.write('cron run\n')

        new_jobs = Job.objects.filter(status='new')
        if len(new_jobs) == 0:
            log.close()
            return
        job = new_jobs.first()
        job.status = 'pending'
        job.save()

        # TODO: check all the files does exist in HDFS.
        # TODO: check all the files are accessible by the user.

        try:
            Spark.submitJob(
                self.getUserName(job), 
                job.job_id,
                job.entry_file,
                job.libs,
                job.archives,
                job.app_params
            )
        except Exception as e:
            log.write('exeption\n')
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            log.write(message)

        log.close()
        return

class ScanFinishedJobCron(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.scan_finished_job_cron' # a unique code

    spark_status_url = 'http://127.0.0.1:18080/api/v1/applications/'

    def do(self):
        jobs = Job.objects.filter(status='finished')

        for j in jobs:
            self.complete_job(j)
        
        return
    
    def complete_job(self, job):
        spark_id = job.spark_id

        app = self.get_spark_app(spark_id)
        print(app, file=sys.stderr)
        if app is None or not 'attempts' in app:
            # TODO: update retry count and remove it after certain threshold
            print('app is None', file=sys.stderr)
            return

        start_time = 0
        end_time = 0
        executors = {}
        for a in app['attempts']:
            att_id = a['attemptId']

            if start_time == 0 or a['startTimeEpoch'] < start_time:
                start_time = a['startTimeEpoch']

            if end_time == 0 or a['endTimeEpoch'] > end_time:
                end_time = a['endTimeEpoch']

            execs = self.get_attempt_executors(spark_id, att_id)
            if execs is None:
                continue
            
            for e in execs:
                if not e in executors:
                    executors[e] = []
                
                executors[e].extend(execs[e])

        if len(executors) == 0:
            return

        qObjs = Q()
        for host in executors:
            qObjs |= Q(ip_address=host)

        macslist = []
        machs = Machine.objects.filter(qObjs)
        for m in machs:
            elist = executors[m.ip_address]
            for e in elist:
                e['type'] = m.machine_type
                macslist.append(e)
        
        info = {}
        info['machines'] = macslist
        # TODO: change to actual credit function
        used_credit = self.update_using(job.user, info)

        job.start_time = start_time
        job.end_time = end_time
        job.used_credits = used_credit
        job.status = 'completed'
        job.save()
        return
    
    def update_using(self, user, info):
        print('user id=' + str(user.id), file=sys.stderr)
        print(info, file=sys.stderr)
        return 10

    def get_attempt_executors(self, spark_id, att_id):
        url = ScanFinishedJobCron.spark_status_url + spark_id + '/' + att_id + '/executors'

        try:
            res = requests.get(url)
            if res.status_code == 200:
                print('status is 200', file=sys.stderr)
                execs = {}
                executors = res.json()
                print(executors, file=sys.stderr)
                for e in executors:
                    if e['id'] == 'driver':
                        continue
                    
                    host = e['hostPort'].split(':')[0]
                    if not host in execs:
                        execs[host] = []
                    
                    execs[host].append({
                        'cores': e['totalCores'],
                        'memory': e['maxMemory'],
                        'duration': e['totalDuration']
                    })
                return execs
            
        except Exception as e:
            print('get_attempt_executors exception', file=sys.stderr)
            print(e, file=sys.stderr)

        return None
        
    def get_spark_app(self, spark_id):
        url = ScanFinishedJobCron.spark_status_url + spark_id
        try:
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print('exception')
        
        return None