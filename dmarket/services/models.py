from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
# Create your models here.

class Credit(models.Model):
    sharing_credit = models.FloatField()
    using_credit = models.FloatField()
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
    service_port = models.CharField(max_length=32, default='8000', blank=True)	
    hostname = models.CharField(max_length=50, default='', blank=False)
    machine_type = models.CharField(max_length=40, default='1', blank=True)
    ip_address = models.CharField(max_length=64, default='127.0.0.1', blank=True)
    core_num = models.IntegerField(default=1, blank=True)
    memory_size = models.FloatField(null=True)
    start_time = models.DateTimeField(default=timezone.now)
    time_period = models.IntegerField(null=True)
    available = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public_key = models.FileField(blank=False)
    premium_rate = models.FloatField(null=True)
    
    def __str__(self):
        return ', '.join([str(self.machine_id), str(self.ip_address), str(self.core_num), str(self.memory_size),
                          str(self.time_period), str(self.public_key)])

class MachineInterval(models.Model):
    machine_interval_id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    start_time = models.TimeField() 
    end_time = models.TimeField()
    status = models.CharField(max_length=40, default='Down', blank=True)   # Down, Up
    def __str__(self):
        return ', '.join([str(self.machine_interval_id), str(self.machine_id), str(self.start_time), str(self.end_time), str(self.status)])

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
    used_credits = models.FloatField(default=0)
    libs = models.CharField(max_length=1024, default='', blank=True)
    archives = models.CharField(max_length=1024, default='', blank=True)
    app_params = models.CharField(max_length=1024, default='', blank=True)
    entry_file = models.CharField(max_length=1024, default='')
    premium_rate = models.FloatField(null=True)

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

