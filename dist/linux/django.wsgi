import os
import sys

sys.path.append('/home/mdid/rooibos')
sys.path.append('/home/mdid/rooibos/rooibos/contrib')

os.environ['DJANGO_SETTINGS_MODULE'] = 'rooibos.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
