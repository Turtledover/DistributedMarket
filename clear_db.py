import os
from services.models import *

Machine.objects.all().delete()


users = User.objects.all()

for u in users:
    if u.username == 'admin':
        continue
    os.system('deluser --remove-all-files ' + u.username)


users.delete()


print("Clear the database.")
