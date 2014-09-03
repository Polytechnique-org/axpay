# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


from django.contrib import admin

from . import models


class ContributorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'has_lifetime_contribution',
        'contributions_payed_until', 'jr_subscribed_until']
    search_fields = ['first_name', 'last_name']
    list_filter = ['has_lifetime_contribution', 'contributions_payed_until', 'jr_subscribed_until']

admin.site.register(models.Contributor, ContributorAdmin)
