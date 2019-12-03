from ..models import * 
from django.contrib.auth.models import User
import sys
from django.db.models import Q

class CreditCore:

	def initial_credit(self, user):
		try:
			self.credit = Credit()
			self.credit.sharing_credit = 15
			self.credit.using_credit = 0
			self.credit.rate = 0.0
			self.credit.user = User.objects.get(id=user.id)
			self.credit.save()
		except:
			return False
		return True

	@staticmethod
	def isSufficient(request):
		credit = Credit.objects.get(user=request.user)
		if credit.sharing_credit <= credit.using_credit:
			return False
		return True

	@staticmethod
	def get_price(request):
		alive_jobs = Job.objects.filter(~Q(status='completed') & ~Q(status='fail_completed') & ~Q(status='kill_completed'))
		if alive_jobs.exists():
			num_of_jobs = len(alive_jobs)			
		else:
			num_of_jobs = 0
		
		existing_machines = Machine.objects.all() 

		if existing_machines.exists():
			num_of_machines = len(existing_machines)		
		else:
			num_of_machines = 0
		if num_of_jobs <= num_of_machines:
			res = 1
		elif num_of_machines * 2 < num_of_jobs:
			res = 2
		else:
			res = round(num_of_jobs / num_of_machines, 4)
		return res


	@staticmethod
	def update_using(user, executors, job, real_update=False):
		credit = Credit.objects.get(user=user)
		new_using_credit = 0
		for e in executors:
			machine_type = executors[e]['type']
			for u in executors[e]['usage']:
				if u['isDriver']:
					continue
				num_of_cores = u['cores']
				memory_size = u['memory']
				premium_rate = job.premium_rate
				duration = u['duration'] / 1000 / 3600
				new_using_credit += (float(machine_type) * float(num_of_cores) + memory_size / 1073741824 * 0.004) * duration * premium_rate
		if real_update:
			credit.using_credit += round(new_using_credit, 2)
			credit.save()
		return round(new_using_credit, 2)
	
	@staticmethod
	def update_sharings(user, machines, real_update=False):
		new_sharing_credit = 0
		for machine in machines:
			new_sharing_credit += CreditCore.update_sharing(user, machine, real_update=False)
		return new_sharing_credit


	@staticmethod
	def update_sharing(user, machine, real_update=False):
		credit = Credit.objects.get(user=user)
		machine_type = machine['type']
		num_of_cores = machine['cores']
		memory_size = machine['memory']
		premium_rate = machine['premium_rate']
		duration = machine['duration'] / 3600
		new_sharing_credit = (float(machine_type) * float(num_of_cores) + memory_size / 1024 * 0.004) * duration * premium_rate
		if real_update:
			credit.sharing_credit += round(new_sharing_credit, 2)
			credit.save()
		return round(new_sharing_credit, 2)

