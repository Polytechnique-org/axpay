# -*- coding: utf-8 -*-
# Copyright (c) 2013 AX. All rights reserved.


from django.utils.http import is_safe_url
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import check_for_language


def set_language(request, lang_code):
    """View to change site language."""
    next = request.GET.get('next')
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = HttpResponseRedirect(next)
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response

