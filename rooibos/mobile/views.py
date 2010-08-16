from django import forms
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.utils import simplejson
from rooibos.util import json_view
from rooibos.data.models import Record, Collection
from rooibos.storage.models import Storage
from rooibos.access import accessible_ids, filter_by_access
from rooibos.contrib.tagging.models import Tag
from rooibos.contrib.tagging.utils import parse_tag_input
from rooibos.util.models import OwnedWrapper
from rooibos.solr.views import run_search
from rooibos.context_processors import selected_records as ctx_selected_records
from rooibos.presentation.models import Presentation
import random 


def test(request):
    
    return render_to_response('mobile-test.html',
                              {},
                              context_instance=RequestContext(request))

