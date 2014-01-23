# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import datetime

from django.utils import timezone

import factory
import factory.django
import factory.fuzzy

from django_factory_boy import auth as auth_factories

from . import models

class ServiceFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Service

    kind = factory.Iterator([c.0 for c in models.Service.KIND_CHOICES])
    name = factory.Sequence(lambda n: "Service #%s" % n)


class ServicePriceFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.ServicePrice

    service = factory.SubFactory(ServiceFactory)
    amount = factory.fuzzy.FuzzyInteger(100, 10000, step=50)
    available_since = factory.LazyAttribute(lambda _o: timezone.now())
    available_until = factory.LazyAttribute(lambda o: o.available_since + datetime.timedelta(years=1))


class PaymentModeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.PaymentMode

    owner = factory.SubFactory(auth_factories.UserF)
    kind = factory.Iterator([c.0 for c in models.PaymentMode.KIND_CHOICES])
    reference = factory.Sequence(lambda n: "42-42-%12d" % n)


class CashFlowFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.CashFlow

    payment_mode = factory.SubFactory(PaymentModeFactory)
    payment_date = factory.LazyAttribute(lambda _o: timezone.now())
    amount = factory.fuzzy.FuzzyInteger(100, 10000, step=50)


class PaymentFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Payment

    user = factory.SubFactory(auth_factories.UserF)
    service_price = models.SubFactory(ServicePriceFactory)
    cashflow = models.SubFactory(CashFlowFactory,
        # Forward '.user' to the cashflow.payment_mode.owner
        payment_mode__owner=factory.SelfAttribute('...user'),
    )

    billing_date = factory.LazyAttribute(lambda _o: timezone.now().date())
