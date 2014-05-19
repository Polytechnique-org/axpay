# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

from __future__ import unicode_literals, print_function

import factory

from django.utils import timezone

from . import models


class AllServicesFactory(factory.Factory):
    FACTORY_FOR = models.Service

    items = [
        (models.Service.KIND_STANDARD_SUBSCRIPTION, "Cotisation"),
        (models.Service.KIND_JR_SUBSCRIPTION, "Cotisation J&R X"),
        (models.Service.KIND_JR_SUBSCRIPTION, "Cotisation J&R externe"),
        (models.Service.KIND_COUPLE_SUBSCRIPTION, "Cotisation conjoint"),
        (models.Service.KIND_LIFETIME_SUBSCRIPTION, "Cotisation à vie"),
    ]

    @classmethod
    def _create(cls, target_class, items):
        services = []
        for kind, name in items:
            service, _created = target_class.objects.get_or_create(
                name=name,
                defaults={'kind': kind},
            )
            services.append(service)
        return services


class AllPricesFactory(factory.Factory):
    FACTORY_FOR = models.ServicePrice

    services = factory.SubFactory(AllServicesFactory)
    available_since = factory.LazyAttribute(lambda _o: timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
    available_until = None
    amount = 4200  # 42€

    @classmethod
    def _create(cls, target_class, services, available_since, available_until, amount):
        prices = []
        for service in services:
            price, _created = target_class.objects.get_or_create(
                service=service,
                available_since=available_since,
                available_until=available_until,
                defaults={'amount': amount},
            )
            prices.append(price)

        return prices
