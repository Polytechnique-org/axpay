# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.


from __future__ import unicode_literals

from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('include/form.html')
def post_form(form, submit_text=_("Submit"), cancel_url=None, file_upload=False):
    """Render a POST form.
    
    Usage:
        {% post_form form submit_text=_("Register") %}
    """
    return {
        'form': form,
        'submit_text': submit_text,
        'cancel_url': cancel_url,
        'file_upload': file_upload,
    }
