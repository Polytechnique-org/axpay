# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.

import datetime

from django import forms
from django.contrib import auth
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from axpay.money import models as money_models
from axpay.money import utils as money_utils


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (#%d)" % (obj.get_full_name(), obj.pk)


class OrderRegisterForm(forms.Form):
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

    order_date = forms.DateField(
        label=_("Order date"),
        initial=datetime.date.today,
    )

    amount = forms.DecimalField(
        label=_("Order total (€)"),
        min_value=0,
        decimal_places=2,
    )

    def __init__(self, *args, **kwargs):
        products = kwargs.pop('products')
        super(OrderRegisterForm, self).__init__(*args, **kwargs)

        self._products_list = {}
        for product in products:
            key = 'product_%s' % product.pk
            self._products_list[key] = product
            self.fields[key] = forms.IntegerField(
                label=product.product,
                min_value=0,
            )
            self.initial[key] = 0
        # Force 'amount' at the end
        self.fields['amount'] = self.fields.pop('amount')

    def clean_payment_mode_reference(self):
        reference = self.cleaned_data['payment_mode_reference']
        if money_models.PaymentMode.objects.filter(reference=reference).exists():
            raise forms.ValidationError(_("A payment with reference %s already exists.") % reference)
        return reference

    def clean(self):
        cleaned_data = super(OrderRegisterForm, self).clean()

        expected_amount = 0
        for field_name, product in self._products_list.items():
            expected_amount += product.amount * cleaned_data.get(field_name, 0)

        if expected_amount == 0:
            raise forms.ValidationError(_("An order must contain at least one product."))

        if cleaned_data.get('amount', 0) * 100 != expected_amount:
            self._errors['amount'] = self.error_class([_("The amount is invalid, expected € %s") % money_utils.currency(expected_amount)])

        return cleaned_data

    def save(self):
        data = self.cleaned_data

        owner = data['user']
        payment_mode = money_models.PaymentMode.objects.create(
            owner=owner,
            kind=data['payment_mode_kind'],
            reference=data['payment_mode_reference'],
        )

        order = money_models.Order.objects.create(
            payment_mode=payment_mode,
            payment_date=timezone.now(),
            amount=data['amount'] * 100,
        )

        order_contents = []
        for field_name, product_price in self._products_list.items():
            product_amount = data[field_name]
            if product_amount > 0:
                order_contents.append(money_models.OrderItem.objects.create(
                    user=owner,
                    product_price=product_price,
                    amount=product_amount,
                    order=order,
                    billing_date=data['order_date'],
                ))

        return {
            'owner': owner,
            'payment_mode': payment_mode,
            'order': order,
            'contents': order_contents,
        }


class OrderFilterForm(forms.Form):
    placeholders = {
        'user_search': _("user"),
        'payment_mode_kind': _("payment kind"),
    }

    user_search = forms.CharField(
        label=_("Payer name"),
        required=False,
        initial='',
    )
    payment_mode_kind = forms.ChoiceField(
        label=_("Payment mode kind"),
        choices=[('', _("(Any payment kind)"))] + list(money_models.PaymentMode.KIND_CHOICES),
        initial='',
        required=False,
    )
    product = forms.ModelChoiceField(
        label=_("Contains product"),
        queryset=money_models.Product.objects,
        empty_label=_("(Any product)"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(OrderFilterForm, self).__init__(*args, **kwargs)
        for field_name, placeholder in self.placeholders.items():
            self.fields[field_name].widget.attrs['placeholder'] = placeholder

    def filter(self, qs, initial=True):
        data = getattr(self, 'cleaned_data', {})

        if data.get('payment_mode_kind'):
            qs = qs.filter(payment_mode__kind=data['payment_mode_kind'])
        if data.get('product'):
            qs = qs.filter(items__product_price__product=data['product'])
        if data.get('user_search'):
            lookup = data['user_search']
            qs = qs.filter(
                models.Q(payment_mode__owner__username__icontains=lookup)
                | models.Q(payment_mode__owner__first_name__icontains=lookup)
                | models.Q(payment_mode__owner__last_name__icontains=lookup)
            )

        return qs.distinct()
