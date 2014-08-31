# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

from __future__ import unicode_literals, print_function

from django.contrib import admin

from . import models


class ProductAdmin(admin.ModelAdmin):
    list_display = ['kind', 'name']
    search_fields = ['kind', 'name']
    list_filter = ['kind']

admin.site.register(models.Product, ProductAdmin)


class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'amount', 'available_since', 'available_until']
    search_fields = ['product__kind', 'product__name']
    list_filter = ['product', 'available_since', 'available_until']
    date_hierarchy = 'available_since'

admin.site.register(models.ProductPrice, ProductPriceAdmin)


class PaymentModeAdmin(admin.ModelAdmin):
    list_display = ['reference', 'owner', 'kind']
    search_fields = ['reference', 'owner__first_name', 'owner__last_name']
    list_filter = ['kind']

admin.site.register(models.PaymentMode, PaymentModeAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['payment_mode', 'payment_date', 'amount']
    search_fields = ['payment_mode__owner__first_name', 'payment_mode__owner__last_name']
    list_filter = ['payment_mode__kind', 'payment_date']
    date_hierarchy = 'payment_date'

admin.site.register(models.Order, OrderAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['product_price', 'order', 'user', 'billing_date']
    list_filter = ['product_price__product', 'product_price', 'order__payment_mode__kind', 'billing_date']
    search_fields = [
        'product_price__product__name', 'product_price__product__kind',
        'user__first_name', 'user__last_name',
        'order__payment_mode__owner__first_name', 'order__payment_mode__owner__last_name',
    ]
    date_hierarchy = 'billing_date'

admin.site.register(models.Payment, PaymentAdmin)

