from .spark.spark import *
from django.db.models import Q
from .models import Machine

def get_job_machines_usage(job):
    """
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
    
    # print(app, file=sys.stderr)
    # if app is None or not 'attempts' in app:
    #     print('app is None', file=sys.stderr)
    #     return None

    # executors = {}
    # for a in app['attempts']:
    #     att_id = a['attemptId']
    #     execs = Spark.get_attempt_executors_list(spark_id, att_id)
    #     if execs is None:
    #         continue
        
    #     for e in execs:
    #         if not e in executors:
    #             executors[e] = {}
    #         executors[e]['usage'] = execs[e]['usage']

    # if len(executors) == 0:
    #     return None

    # qObjs = Q()
    # for host in executors:
    #     qObjs |= Q(ip_address=host)

    # machs = Machine.objects.filter(qObjs)
    # for m in machs:
    #     executors[m.ip_address]['type'] = m.machine_type
    #     executors[m.ip_address]['id'] = m.machine_id
    
    # return executors

def get_spark_app_machine_usage(spark_id, app):
    print(app, file=sys.stderr)
    if app is None or not 'attempts' in app:
        print('app is None', file=sys.stderr)
        return None

    executors = {}
    for a in app['attempts']:
        att_id = a['attemptId']
        execs = Spark.get_attempt_executors_list(spark_id, att_id)
        if execs is None:
            continue
        
        for e in execs:
            if not e in executors:
                executors[e] = {}
            executors[e]['usage'] = execs[e]['usage']

    if len(executors) == 0:
        return None

    qObjs = Q()
    for host in executors:
        qObjs |= Q(ip_address=host)

    machs = Machine.objects.filter(qObjs)
    for m in machs:
        executors[m.ip_address]['type'] = m.machine_type
        executors[m.ip_address]['id'] = m.machine_id
    
    return executors