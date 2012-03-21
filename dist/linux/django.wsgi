import os
import sys

sys.path.insert(0, '/home/mdid/rooibos')
sys.path.insert(0, '/home/mdid/rooibos/rooibos')
sys.path.insert(0, '/home/mdid/rooibos/rooibos/contrib')

os.environ['DJANGO_SETTINGS_MODULE'] = 'rooibos.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
