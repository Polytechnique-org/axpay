# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

import datetime

from django import forms
from django.contrib import auth
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from axpay.money import models as money_models
from axpay.money import utils as money_utils


class ContributorFilterForm(forms.Form):
    placeholders = {
        'user_search': _("user"),
    }

    user_search = forms.CharField(
        label=_("Payer name"),
        required=False,
        initial='',
    )
    product = forms.ModelChoiceField(
        label=_("Contains product"),
        queryset=money_models.Product.objects,
        empty_label=_("(Any product)"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, placeholder in self.placeholders.items():
            self.fields[field_name].widget.attrs['placeholder'] = placeholder

    def filter(self, qs, initial=True):
        data = getattr(self, 'cleaned_data', {})

        if data.get('product'):
            qs = qs.filter(ordered_items__product_price__product=data['product'])
        if data.get('user_search'):
            lookup = data['user_search']
            qs = qs.filter(
                models.Q(username__icontains=lookup)
                | models.Q(first_name__icontains=lookup)
                | models.Q(last_name__icontains=lookup)
            )

        return qs.distinct()
