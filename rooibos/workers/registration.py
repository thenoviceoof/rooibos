import sys
from django.conf import settings
from gearman import GearmanWorker, GearmanClient

# misnomer, local dictionary keeping track of work tasks
workers = dict()

if settings.GEARMAN_SERVERS:
    client = GearmanClient(settings.GEARMAN_SERVERS)
else:
    client = None

def register_worker(id):
    def register(worker):
        workers[id] = worker
        return worker
    return register

def discover_workers():
    """Populates the workers dict"""
    if not workers:
        for app in settings.INSTALLED_APPS:
            try:
                module = __import__(app + ".workers")
            except ImportError:
                pass

def create_worker():
    """Create a gearman worker, register all possible functions with it"""
    discover_workers()
    worker = GearmanWorker(settings.GEARMAN_SERVERS)
    for id, func in workers.iteritems():
        worker.register_task(id, func)
    return worker

def run_worker(worker, arg, **kwargs):
    discover_workers()
    if client:
        request = client.submit_job(worker, arg)
        # specific check if we want it asynchronously or not
        if kwargs.get("background", None):
            return request
        else:
            return request.result
    else:
        # presume this assumes workers is a set of functions
        if workers.has_key(worker):
            return workers[worker](dict(task=worker, data=arg))
        else:
            raise NotImplementedError()
