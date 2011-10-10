import logging
from django.conf import settings

class Middleware:

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_kwargs.has_key('master_template'):
            request.master_template = view_kwargs['master_template']
            del view_kwargs['master_template']
        return None

    def process_request(self, request):
        # To support SWFUpload, copy the provided session key from POST into COOKIES
        # since Flash does not send browser cookies with its requests
        if (request.method == 'POST' and
            request.POST.get('swfupload') == 'true' and
            request.POST.has_key(settings.SESSION_COOKIE_NAME)):
            request.COOKIES[settings.SESSION_COOKIE_NAME] = request.POST[settings.SESSION_COOKIE_NAME]

    def process_response(self, request, response):
        # Remove the Vary header for content loaded into Flash, otherwise caching is broken
        if request.GET.get('flash') == '1':
            try:
                del response['Vary']
            except KeyError:
                pass
        return response



class HistoryMiddleware:

    def process_response(self, request, response):
        # Keep track of most recent URLs to allow going back after certain operations
        # (e.g. deleting a record)
        try:
            if (request.user
                and request.user.is_authenticated()
                and not request.is_ajax()
                and response.status_code == 200
                and response.get('Content-Type', '').startswith('text/html')
                ):
                history = request.session.get('page-history', [])
                history.insert(0, request.get_full_path())
                request.session['page-history'] = history[:10]
        except:
            # for some reason, with some clients, on some pages,
            # request.session does not exist and request.user throws an error
            pass

        return response

    @staticmethod
    def go_back(request, to_before, default=None):
        for h in request.session.get('page-history', []):
            if not h.startswith(to_before):
                return h
        return default

###
from django.contrib.auth.models import User
import re
import socket

class AnonymousDomainMiddleware:
    """If traffic is coming from a trusted domain, then auto sign in as an anonymous user
    Set this user is settings_local.py, as ANONYMOUS_DOMAIN_USER
    Try to use a username that is sufficiently unique
    """
    def process_request(self, request):
        log = logging.getLogger(__name__)

        user = request.user
        if not(user.is_authenticated()) and request:
            # check if they're in the trusted network
            remote = request.META["REMOTE_ADDR"]
            log.debug("Remote: "+remote)
            try:
                host = socket.gethostbyaddr(remote)[0]
                log.debug("Host: "+host)
                if re.match(".*%s$" % settings.ANONYMOUS_DOMAIN,host):
                    user_name = settings.ANONYMOUS_DOMAIN_USER
                    user = User.objects.filter(username=user_name)
                    if len(user)>0:
                        user = user[0]
                    else:
                        user = request.user
            except socket.herror:
                log.debug("No host associated")
                pass
        request.user = user
        log.debug("User: "+str(user))
        return None
###
