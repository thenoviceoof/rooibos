import os
from threading import Thread
from django.core.management.base import BaseCommand
from django.conf import settings
from rooibos.workers.registration import create_worker
from optparse import make_option
import rooibos.contrib.djangologging.middleware # does not get loaded otherwise
import logging


class Command(BaseCommand):
    help = 'Starts Gearman compatible workers'

    option_list = BaseCommand.option_list + (
        make_option('--server', action='store_true',
            help='Run a simple Gearman compatible server'),
        )

    def handle(self, *commands, **options):

        verbosity = options.get('verbosity', 1)
        server = options.get('server', False)

        if server:
            logging.warning("Server option is deprecated, you must run your own gearmand")

        worker = create_worker()
        if verbosity > 0:
            logging.info("Starting workers: " + ', '.join(worker.worker_abilities.keys()))
        worker.work()
