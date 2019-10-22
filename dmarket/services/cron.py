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
            # app_params = []
            # if job.app_params:
            #     app_params = shlex.split(job.app_params)

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
