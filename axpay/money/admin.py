# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

from __future__ import unicode_literals, print_function

from django.contrib import admin

from . import models


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['kind', 'name']
    search_fields = ['kind', 'name']
    list_filter = ['kind']

admin.site.register(models.Service, ServiceAdmin)


class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ['service', 'amount', 'available_since', 'available_until']
    search_fields = ['service__kind', 'service__name']
    list_filter = ['service', 'available_since', 'available_until']
    date_hierarchy = 'available_since'

admin.site.register(models.ServicePrice, ServicePriceAdmin)


class PaymentModeAdmin(admin.ModelAdmin):
    list_display = ['reference', 'owner', 'kind']
    search_fields = ['reference', 'owner__first_name', 'owner__last_name']
    list_filter = ['kind']

admin.site.register(models.PaymentMode, PaymentModeAdmin)


class CashFlowAdmin(admin.ModelAdmin):
    list_display = ['payment_mode', 'payment_date', 'amount']
    search_fields = ['payment_mode__owner__first_name', 'payment_mode__owner__last_name']
    list_filter = ['payment_mode__kind', 'payment_date']
    date_hierarchy = 'payment_date'

admin.site.register(models.CashFlow, CashFlowAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['service_price', 'cashflow', 'user', 'billing_date']
    list_filter = ['service_price__service', 'service_price', 'cashflow__payment_mode__kind', 'billing_date']
    search_fields = [
        'service_price__service__name', 'service_price__service__kind',
        'user__first_name', 'user__last_name',
        'cashflow__payment_mode__owner__first_name', 'cashflow__payment_mode__owner__last_name',
    ]
    date_hierarchy = 'billing_date'

admin.site.register(models.Payment, PaymentAdmin)

