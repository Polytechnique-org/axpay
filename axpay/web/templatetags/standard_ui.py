# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.



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

@register.inclusion_tag('include/filter_form.html')
def filter_form(form, submit_text=_("Filter"), form_title=_("Filtering")):
    """Render a GET filtering form.
    
    Usage:
        {% filter_form form submit_text=_("Search") %}
    """
    return {
        'form': form,
        'form_title': form_title,
        'submit_text': submit_text,
    }
