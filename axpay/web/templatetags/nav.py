# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


from django import template


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


@register.simple_tag(takes_context=True)
def sidenavclass(context, name):
    """Create a "side-navbar" link.

    Usage:
        {% sidenavlink name='home' url='index' text=_("Home") %}

    Translates into:
    - If the 'sidenav' context var equals 'home':
        <a href="{% url 'index' %}" class="active">{% trans "Home" %}</a>
    - Otherwise:
        <a href="{% url 'index' %}">{% trans "Home" %}</a>
    """
    sidenav = context.get('sidenav')
    if sidenav == name:
        return "active"
    else:
        return "inactive"
