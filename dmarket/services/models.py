from django.db import models
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import datetime
# Create your models here.

class Credit(models.Model):
    sharing_credit = models.IntegerField()
    using_credit = models.IntegerField()
    rate = models.FloatField(null=True)
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.user

class Profile(models.Model):
    # user_id, password, email_address in User
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='', blank=False)
    credit = models.OneToOneField(Credit, on_delete=models.CASCADE)

    def __str__(self):
        return self.user

class Machine(models.Model):
    machine_id = models.AutoField(primary_key=True)
    machine_type = models.CharField(max_length=40, default='GPU', blank=True)	
    ip_address = models.CharField(max_length=64, default='127.0.0.1', blank=True)	
    service_port = models.CharField(max_length=32, default='8000', blank=True)	
    core_num = models.IntegerField(default=1, blank=True)
    memory_size = models.FloatField(null=True)
    start_time = models.DateTimeField(default=datetime.datetime.now())
    time_period = models.IntegerField(null=True)
    available = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.machine_id

class HistoryMachine(models.Model):
    history_id = models.AutoField(primary_key=True)

    machine_id = models.IntegerField(default=0)
    machine_type = models.CharField(max_length=40, default='GPU', blank=True)
    core_num = models.IntegerField(default=1, blank=True)
    memory_size = models.FloatField(null=True)

    start_time = models.DateTimeField(auto_now_add=False)
    end_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.history_id

    @classmethod
    def create(cls, machine):
        history = cls()
        history.machine_id = machine.machine_id
        history.machine_type = machine.machine_type
        history.memory_size = machine.memory_size
        history.core_num = machine.core_num
        history.start_time = machine.start_time
        history.end_time = datetime.datetime.now()

        return history

class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    # root_path = models.CharField(max_length=128, default='', blank=True)
    job_name = models.CharField(max_length=64, default='', blank=True)
    added_time = models.DateTimeField(auto_now_add=True, blank=True)
    start_time = models.BigIntegerField(default=0)
    end_time = models.BigIntegerField(default=0)
    duration = models.IntegerField(default=0)
    used_credits = models.IntegerField(default=0)
    libs = models.CharField(max_length=1024, default='', blank=True)
    archives = models.CharField(max_length=1024, default='', blank=True)
    app_params = models.CharField(max_length=1024, default='', blank=True)
    entry_file = models.CharField(max_length=1024, default='')

    # core_num = models.IntegerField()
    # machine_type = models.CharField(max_length=40, default='GPU', blank=True)
    status = models.CharField(max_length=40, default='Available', blank=True)
    spark_id = models.CharField(max_length=64, default='', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.job_id


# class Metadata(models.Model):
#     machine_info = models.ListCharField(
#         base_field = models.CharField(max_length=100),
#         size=100,
#     )

