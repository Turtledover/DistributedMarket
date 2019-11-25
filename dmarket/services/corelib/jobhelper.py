from services.corelib.spark import *
from django.db.models import Q
from services.models import Machine
from html.parser import HTMLParser
import sys

def get_job_machines_usage(job):
    """
    Get machines usage of a single job.

    :param Job job: target job model
    :return dict: Format
    {
        "host1": {
            "id": 1                     (machine id)
            "type": 1,
            "usage": [
                {
                    "cores": 2,
                    "memory": 981723,   (bytes)
                    "duration": 60573,  (millisecond)
                    "logs": {
                        "stderr": "http://host1/logs",
                        "stdout": "http://host1/logs_stdout"
                    },
                    "isDriver": false    (True if it served as driver, false otherwise)
                },
                ...
            ]
        },
        ...
    }
    """

    if job is None:
        return None

    spark_id = job.spark_id

    app = Spark.get_spark_app(spark_id)
    return get_spark_app_machine_usage(spark_id, app)

def get_spark_app_machine_usage(spark_id, app):
    print(app, file=sys.stderr)
    if app is None or not 'attempts' in app:
        print('app is None', file=sys.stderr)
        return None

    executors = {}
    for a in app['attempts']:
        att_id = None
        # 'attemptId' is only available in YARN cluster mode.
        if 'attemptId' in a:
            att_id = a['attemptId']

        execs = Spark.get_attempt_executors_list(spark_id, att_id)
        if execs is None:
            continue
        
        for e in execs:
            if not e in executors:
                executors[e] = {}
            executors[e]['usage'] = execs[e]['usage']
            executors[e]['type'] = '1'
            executors[e]['id'] = 0

    if len(executors) == 0:
        return None

    qObjs = Q()
    for host in executors:
        qObjs |= Q(hostname=host)

    machs = Machine.objects.filter(qObjs)
    for m in machs:
        executors[m.hostname]['type'] = m.machine_type
        executors[m.hostname]['id'] = m.machine_id

    return executors

class LogParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.isStart = False
        self.isDone = False
        self.data = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.isStart = True

    def handle_endtag(self, tag):
        if self.isStart and tag == 'pre':
            self.isDone = True

    def handle_data(self, data):
        if self.isStart and not self.isDone:
            self.data += data

def get_hadoop_log(url):
    """
    Parse executor log from html body.
    :param str url: url of the executor log
    :return: log in string
    """
    url = url.split('?')[0]
    url += '?start=0'

    res = requests.get(url)
    if res.status_code == 200:
        parser = LogParser()
        parser.feed(res.content.decode("utf-8"))
        return parser.data
    
    return ''