# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.
from __future__ import unicode_literals

from django import template
from django.utils.translation import ugettext_lazy as _

from .. import money

register = template.Library()

@register.filter
def price(value):
    euros = money.to_euros(value)
    return _("€ %s") % euros
