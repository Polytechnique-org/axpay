# -*- coding: utf-8 -*-
# Copyright (c) 2013 AX. All rights reserved.


from django import template
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text


register = template.Library()


@register.simple_tag(takes_context=True)
def topnavclass(context, name):
    """Create a "top-navbar" link.

    Usage:
        {% topnavlink name='home' url='index' text=_("Home") %}

    Translates into:
    - If the 'topnav' context var equals 'home':
        <a href="{% url 'index' %}" class="active">{% trans "Home" %}</a>
    - Otherwise:
        <a href="{% url 'index' %}">{% trans "Home" %}</a>
    """
    topnav = context.get('topnav')
    if topnav == name:
        return "active"
    else:
        return "inactive"
