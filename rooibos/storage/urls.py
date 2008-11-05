from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^retrieve/(?P<record>[-\w]+)/(?P<media>[-\w]+)/$', retrieve, name='storage-retrieve'),
    url(r'^thumbnail/(?P<record>[-\w]+)/$', thumbnail, name='storage-thumbnail'),
)