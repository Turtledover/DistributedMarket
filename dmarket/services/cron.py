from django_cron import CronJobBase, Schedule
from django.core.files import File
from django.db.models import Q
from services.corelib.spark import *
from .models import *
import requests
import sys
from services.corelib.jobhelper import *
from .credit.credit_core import CreditCore

class SubmitJobCron(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.submit_job_cron' # a unique code

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
                job.user.username, 
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

            if end_time == 0 or a['endTimeEpoch'] > end_time:
                end_time = a['endTimeEpoch']

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