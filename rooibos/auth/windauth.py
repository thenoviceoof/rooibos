from django.contrib.auth.models import User, Group
from django.conf import settings
from baseauth import BaseAuthenticationBackend
import requests
import logging

class WindAuthenticationBackend(BaseAuthenticationBackend):
    def authenticate(self, token=None):
        # after the redirect
        url = "https://wind.columbia.edu/validate?ticketid={0}".format(token)
        ret = requests.get(url).content.split("\n")
        if ret[0] == "yes":
            uni = ret[1]
            # generate a username
            username = "Columbian_{0}".format(uni)   
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # get the default group: fails fast (before user creation)
                if uni in settings.WIND_PROF_UNI:
                    if settings.WIND_PROF_GROUP:
                        g = Group.objects.get(name=settings.WIND_PROF_GROUP)
                else:
                    if settings.WIND_DEFAULT_GROUP:
                        g = Group.objects.get(name=settings.WIND_DEFAULT_GROUP)
                # generates a random password
                user = self._create_user(username)
                user.groups.add(g)
            if self._post_login_check(user):
                return user
        return None

