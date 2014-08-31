# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.

import datetime

from django import forms
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from axpay.money import models as money_models
from axpay.money import utils as money_utils


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (#%d)" % (obj.get_full_name(), obj.pk)


class PaymentRegisterForm(forms.Form):
    user = UserChoiceField(
        label=_("User"),
        queryset=auth.get_user_model().objects,
    )

    payment_mode_kind = forms.ChoiceField(
        label=_("Payment mode"),
        choices=money_models.PaymentMode.KIND_CHOICES,
    )

    payment_mode_reference = forms.CharField(
        label=_("Payment reference"),
        max_length=32,
    )

    payment_date = forms.DateField(
        label=_("Payment date"),
        initial=datetime.date.today,
    )

    amount = forms.DecimalField(
        label=_("Payment total (€)"),
        min_value=0,
        decimal_places=2,
    )

    def __init__(self, *args, **kwargs):
        services = kwargs.pop('services')
        super(PaymentRegisterForm, self).__init__(*args, **kwargs)

        self._services_list = {}
        for service in services:
            key = 'service_%s' % service.pk
            self._services_list[key] = service
            self.fields[key] = forms.IntegerField(
                label=service.service,
                min_value=0,
            )
        # Force 'amount' at the end
        self.fields['amount'] = self.fields.pop('amount')

    def clean_payment_mode_reference(self):
        reference = self.cleaned_data['payment_mode_reference']
        if money_models.PaymentMode.objects.filter(reference=reference).exists():
            raise forms.ValidationError(_("A payment with reference %s already exists.") % reference)
        return reference

    def clean(self):
        cleaned_data = super(PaymentRegisterForm, self).clean()

        expected_amount = 0
        for field_name, service in self._services_list.items():
            expected_amount += service.price * cleaned_data.get(field_name, 0)

        if expected_amount == 0:
            raise forms.ValidationError(_("A payment must contain at least one service;"))

        if cleaned_data.get('amount', 0) * 100 != expected_amount:
            self._errors['amount'] = self.error_class([_("The amount is invalid, expected %s€") % money_utils.currency(expected_amount)])

        return cleaned_data

    def save(self):
        data = self.cleaned_data

        owner = data['user']
        payment_mode = money_models.PaymentMode.objects.create(
            owner=owner,
            kind=data['payment_mode_kind'],
            reference=data['payment_mode_reference'],
        )

        cashflow = money_models.CashFlow.objects.create(
            payment_mode=payment_mode,
            payment_date=data['payment_date'],
            amount=data['amount'] * 100,
        )

        payments = []
        for field_name, service_price in self._services_list:
            service_amount = data[field_name]
            if service_amount > 0:
                payments.append(money_models.Payment.objects.create(
                    user=owner,
                    service_price=service_price,
                    amount=service_amount,
                    cashflow=cashflow,
                    billing_date=data['payment_date'],
                ))

        return {
            'owner': owner,
            'payment_mode': payment_mode,
            'cashflow': cashflow,
            'payments': payments,
        }
