# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

import collections

from django.core.urlresolvers import reverse
from django.db import models

from axpay.accounts import models as accounts_models
from axpay.money import models as money_models
from axpay.web.views import generic

from . import forms


class ContributionsIndexView(generic.TemplateView):
    topnav = 'contributions'
    sidenav = 'index'
    template_name = 'contributions/index.html'

    def get_context_data(self, **kwargs):
        ctxt = super(ContributionsIndexView, self).get_context_data(**kwargs)
        return ctxt


class ContributorsListView(generic.FilterListView):
    # Global
    topnav = 'contributions'
    sidenav = 'contributors'

    # Form
    form_class = forms.ContributorFilterForm

    # Template
    context_object_name = 'contributors'
    template_name = 'contributions/contributor_list.html'

    # List
    model = accounts_models.Contributor

    select_related = ['contributor_profile']

    def enrich_queryset(self, qs):
        order_items = (money_models.OrderItem.objects
            .filter(user__in=qs)
            .order_by('order__payment_date')
            .select_related(
                'order',
                'product_price__product',
            )
        )

        last_order_items = collections.defaultdict(lambda: None)
        nb_products = collections.defaultdict(int)

        for item in order_items:
            last_order_items[item.user_id] = item
            nb_products[item.user_id] += 1

        users = []
        for user in qs:
            user.last_order_item = last_order_items[user.pk]
            user.nb_products = nb_products[user.pk]
            users.append(user)
        return users


class GroupedItems():
    def __init__(self, items, total):
        self.items = items
        self.total = total

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return 'GroupedItems(%r, %d)' % (self.items, self.total)


def group_by_year(items, year_getter, desc=True):
    items_per_year = collections.defaultdict(list)
    total = 0
    for item in items:
        items_per_year[year_getter(item)].append(item)
        total += 1

    return GroupedItems(
        sorted(items_per_year.items(), reverse=desc),
        total,
    )


class ContributorDetailView(generic.DetailView):
    topnav = 'contributions'
    sidenav = 'contributors'

    context_object_name = 'contributor'
    template_name = 'contributions/contributor_detail.html'

    model = accounts_models.Contributor

    def get_context_data(self, **kwargs):
        ctxt = super(ContributorDetailView, self).get_context_data(**kwargs)
        contributor = ctxt['contributor']

        ordered_items = (contributor.ordered_items
            .order_by('-billing_date')
            .select_related(
                'product_price__product',
                'order__payment_mode__owner',
            )
        )

        payment_modes = (contributor.payment_modes
            .order_by('-pk')
            .annotate(orders_count=models.Count('orders'))
            .distinct()
        )

        orders = (money_models.Order.objects
            .filter(payment_mode__owner=contributor)
            .select_related('payment_mode')
            .annotate(nb_items=models.Count('items'))
            .distinct()
        )

        ctxt.update(
            ordered_items=group_by_year(ordered_items, lambda item: item.billing_year),
            orders=group_by_year(orders, lambda order: order.payment_date.year),
            payment_modes=payment_modes,
            up_to_date=money_models.up_to_date(contributor),
            jr_subscribed=money_models.jr_subscribed(contributor),
        )
        return ctxt


class ExportView(generic.TemplateView):
    topnav = 'contributions'
    sidenav = 'exports'
    template_name = 'contributions/contributor_export.html'
