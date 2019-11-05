from ..models import * 
from django.contrib.auth.models import User
import sys

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
	def update_usings(user, jobs, real_update=False):
		new_using_credit = 0
		for job in jobs:
			new_using_credit += update_using(user, job, real_update=False)
		return new_using_credit


	@staticmethod
	def update_using(user, executors, real_update=False):
		credit = Credit.objects.get(user=user)
		new_using_credit = 0
		for e in executors:
			machine_type = executors[e]['type']
			for u in executors[e]['usage']:
				if u['isDriver']:
					continue
				num_of_cores = u['cores']
				duration = u['duration'] / 1000 / 3600
				new_using_credit += float(machine_type) * float(num_of_cores) * duration
		if real_update:
			credit.using_credit += new_using_credit
			credit.save()
		return new_using_credit
	
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
		duration = machine['duration'] / 3600
		new_sharing_credit = float(machine_type) * float(num_of_cores) * duration
		if real_update:
			cridet.sharing_credit += new_sharing_credit
			credit.save()
		return new_sharing_credit

