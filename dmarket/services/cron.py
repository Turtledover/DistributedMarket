from django_cron import CronJobBase, Schedule
from django.core.files import File
from .spark.spark import *
from .models import *
import shlex

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'services.my_cron_job'    # a unique code

    def getUserName(self, job):
        #TODO: get username from database with user id
        return 'root'

    def do(self):
        print('cron run')
        new_jobs = Job.objects.filter(status='new')
        if len(new_jobs) == 0:
            return
        job = new_jobs.first()
        job.status = 'running'
        job.save()

        # TODO: check all the files does exist in HDFS.
        # TODO: check all the files are accessible by the user.

        try:
            app_params = []
            if job.app_params:
                app_params = shlex.split(job.app_params)

            Spark.submitJob(
                self.getUserName(job), 
                job.entry_file,
                job.libs,
                job.archives,
                app_params
            )
        except Exception as e:
            print(e)

        return
