# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

from __future__ import unicode_literals, print_function

import collections
import datetime
import factory
import factory.django

from django.contrib.auth import models as auth_models
from django.utils import timezone

from . import models


class AllServicesFactory(factory.Factory):
    class Meta:
        model = models.Service

    items = [
        (models.Service.KIND_STANDARD_SUBSCRIPTION, "Cotisation"),
        (models.Service.KIND_JR_SUBSCRIPTION, "Cotisation J&R X"),
        (models.Service.KIND_JR_SUBSCRIPTION, "Cotisation J&R externe"),
        (models.Service.KIND_COUPLE_SUBSCRIPTION, "Cotisation conjoint"),
        (models.Service.KIND_LIFETIME_SUBSCRIPTION, "Cotisation à vie"),
    ]

    @classmethod
    def _create(cls, target_class, items):  # pylint: disable=arguments-differ
        services = []
        for kind, name in items:
            service, _created = target_class.objects.get_or_create(
                name=name,
                defaults={'kind': kind},
            )
            services.append(service)
        return services


class AllPricesFactory(factory.Factory):
    class Meta:
        model = models.ServicePrice

    services = factory.SubFactory(AllServicesFactory)
    available_since = factory.LazyAttribute(
        lambda _o: timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
    available_until = None
    amount = 4200  # 42€

    @classmethod
    def _create(cls, target_class, services, available_since, available_until, amount):  # pylint: disable=arguments-differ
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


class ExamplePaymentOwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.User

    username = factory.Sequence(lambda n: 'demo-owner-%s' % n)
    first_name = "John"
    last_name = factory.Sequence(lambda n: "Demo%s" % n)


class ExamplePaymentFactory(factory.Factory):
    class Meta:
        model = models.Payment
        exclude = ['items', 'service_prices']

    owner = factory.SubFactory(ExamplePaymentOwnerFactory)

    items = [models.Service.KIND_STANDARD_SUBSCRIPTION]
    nb_payments = 1
    payment_kind = models.PaymentMode.KIND_CASH
    latest_payment = factory.LazyAttribute(lambda _o: timezone.now())
    ref_date = factory.LazyAttribute(lambda o: o.latest_payment - datetime.timedelta(days=365 * o.nb_payments))
    service_prices = factory.LazyAttribute(lambda _o: models.ServicePrice.objects.all())

    @classmethod
    def _setup_next_sequence(cls):
        return models.PaymentMode.objects.count() + 1

    @factory.lazy_attribute_sequence
    def reference(self, n):
        prefixes = {
            models.PaymentMode.KIND_CASH: 'L',
            models.PaymentMode.KIND_CHECK: 'C',
            models.PaymentMode.KIND_CARD: 'CB',
            models.PaymentMode.KIND_DIRECT: 'P',
        }

        return '%s%08d' % (prefixes[self.payment_kind], n)

    @factory.lazy_attribute
    def selected_service_prices(self):
        service_prices = {}
        for price in self.service_prices:
            service_prices[price.service.kind] = price

        return [service_prices[item] for item in self.items]

    @classmethod
    def _create(cls, target_class,
            selected_service_prices, nb_payments, payment_kind,
            latest_payment, ref_date, owner, reference):

        payments = []
        aggregated_service_prices = collections.Counter(selected_service_prices)

        payment_mode = models.PaymentMode.objects.create(
            kind=payment_kind,
            owner=owner,
            reference=reference,
        )
        services_total = sum(sp.amount for sp in selected_service_prices)
        for i in range(nb_payments):
            cashflow = models.CashFlow.objects.create(
                payment_mode=payment_mode,
                payment_date=ref_date + i * datetime.timedelta(days=365),
                amount=services_total,
            )
            for sp, amount in aggregated_service_prices.items():
                payment = target_class.objects.create(
                    user=payment_mode.owner,
                    service_price=sp,
                    amount=amount,
                    cashflow=cashflow,
                    billing_date=cashflow.payment_date.date(),
                )
                payments.append(payment)
        return payments


class ExamplePaymentsFactory(factory.Factory):
    class Meta:
        model = models.Payment

    prices = factory.SubFactory(AllPricesFactory)

    payments = factory.List([
        factory.SubFactory(ExamplePaymentFactory,
            service_prices=factory.SelfAttribute('...prices'),
            items=[models.Service.KIND_STANDARD_SUBSCRIPTION],
            payment_kind=models.PaymentMode.KIND_CASH,
        ),
        factory.SubFactory(ExamplePaymentFactory,
            service_prices=factory.SelfAttribute('...prices'),
            items=[models.Service.KIND_STANDARD_SUBSCRIPTION, models.Service.KIND_COUPLE_SUBSCRIPTION],
            payment_kind=models.PaymentMode.KIND_CHECK,
        ),
        factory.SubFactory(ExamplePaymentFactory,
            service_prices=factory.SelfAttribute('...prices'),
            items=[models.Service.KIND_STANDARD_SUBSCRIPTION],
            nb_payments=3,
            payment_kind=models.PaymentMode.KIND_CARD,
        ),
        factory.SubFactory(ExamplePaymentFactory,
            service_prices=factory.SelfAttribute('...prices'),
            items=[
                models.Service.KIND_STANDARD_SUBSCRIPTION,
                models.Service.KIND_COUPLE_SUBSCRIPTION,
                models.Service.KIND_JR_SUBSCRIPTION,
                models.Service.KIND_JR_SUBSCRIPTION,
            ],
            nb_payments=4,
            payment_kind=models.PaymentMode.KIND_DIRECT,
        ),
    ])

    @classmethod
    def _create(cls, target_class, prices, payments):
        return sum(payments, [])
