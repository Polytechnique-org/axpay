# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.

import datetime

from django import forms
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from axpay.money import models as money_models
from axpay.money import utils as money_utils


class PaymentRegisterForm(forms.Form):
    user = forms.ModelChoiceField(
        label=_("user"),
        queryset=auth.get_user_model().objects,
    )

    payment_mode_kind = forms.ChoiceField(
        label=_("payment mode"),
        choices=money_models.PaymentMode.KIND_CHOICES,
    )

    payment_mode_reference = forms.CharField(
        label=_("payment reference"),
        max_length=32,
    )

    payment_date = forms.DateField(
        label=_("payment date"),
        initial=datetime.date.today,
    )

    service = forms.ModelChoiceField(
        label=_("service"),
        queryset=money_models.ServicePrice.objects.available(),
    )

    amount = forms.DecimalField(
        label=_("amount (€)"),
        min_value=0,
        decimal_places=2,
    )

    def clean_payment_mode_reference(self):
        reference = self.cleaned_data['payment_mode_reference']
        if money_models.PaymentMode.objects.filter(reference=reference).exists():
            raise forms.ValidationError(_("A payment with reference %s already exists.") % reference)
        return reference

    def clean(self):
        cleaned_data = super(PaymentRegisterForm, self).clean()
        expected_amount = cleaned_data['service'].amount
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

        payment = money_models.Payment.objects.create(
            user=owner,
            service_price=data['service'],
            cashflow=cashflow,
            billing_date=data['payment_date'],
        )

        return {
            'owner': owner,
            'payment_mode': payment_mode,
            'cashflow': cashflow,
            'payments': [payment],
        }
