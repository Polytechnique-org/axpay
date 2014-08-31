# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

from __future__ import unicode_literals, print_function

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import utils


class Service(models.Model):
    """A base service."""

    KIND_STANDARD_SUBSCRIPTION = 'std'
    KIND_JR_SUBSCRIPTION = 'j-r'
    KIND_COUPLE_SUBSCRIPTION = 'couple'
    KIND_LIFETIME_SUBSCRIPTION = 'lifetime'

    KIND_CHOICES = (
        (KIND_STANDARD_SUBSCRIPTION, _("Standard subscription")),
        (KIND_COUPLE_SUBSCRIPTION, _("'second of a couple' subscription")),
        (KIND_LIFETIME_SUBSCRIPTION, _("Lifetime subscription")),
        (KIND_JR_SUBSCRIPTION, _("La jaune & la Rouge subscription")),
    )

    kind = models.CharField(max_length=16, choices=KIND_CHOICES, verbose_name=_("kind"))
    name = models.CharField(max_length=32, unique=True, verbose_name=_("name"))

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_kind_display())


class ServicePriceManager(models.Manager):
    def available(self, at=None):
        if at is None:
            at = timezone.now()

        lower_bound = higher_bound = at

        return self.filter(
            models.Q(available_since__lte=lower_bound) & (
                models.Q(available_until__isnull=True)
                | models.Q(available_until__gte=higher_bound)
            )
        )


class ServicePrice(models.Model):
    """The price of a service at a given time."""

    service = models.ForeignKey(Service, related_name='prices', verbose_name=_("service"))
    amount = models.IntegerField(verbose_name=_("amount"),
        help_text=_("actual price, in euro cents"))

    available_since = models.DateTimeField(verbose_name=_("available since"))
    available_until = models.DateTimeField(blank=True, null=True, verbose_name=_("available until"))

    objects = ServicePriceManager()

    class Meta:
        verbose_name = _("service price")
        verbose_name_plural = _("service prices")

    def __str__(self):
        return "%s: %s (from %s to %s)" % (
            self.service.name,
            utils.currency(self.amount),
            self.available_since,
            self.available_until or 'forever',
        )


class PaymentMode(models.Model):
    """A payment mode.

    Many cash flows may be taken from the same payment mode.
    """

    KIND_CASH = 'cash'
    KIND_CHECK = 'check'
    KIND_CARD = 'card'
    KIND_DIRECT = 'direct'

    KIND_CHOICES = (
        (KIND_CASH, _("Cash")),
        (KIND_CHECK, _("Check")),
        (KIND_CARD, _("Credit card")),
        (KIND_DIRECT, _("Direct debit")),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payment_modes',
        verbose_name=_("owner"))
    kind = models.CharField(max_length=16, choices=KIND_CHOICES,
        verbose_name=_("kind"))
    reference = models.CharField(max_length=32, unique=True, verbose_name=_("reference"))

    class Meta:
        verbose_name = _("payment mode")
        verbose_name_plural = _("payment modes")

    def __str__(self):
        return '%s (%s) for %s' % (
            self.reference, self.get_kind_display(), self.owner.get_full_name() or self.owner.username)


class CashFlow(models.Model):
    """Some money movement.

    One single CashFlow may be used to pay for several services.
    """

    payment_mode = models.ForeignKey(PaymentMode, related_name='cashflows',
        verbose_name=_("payment mode"))
    payment_date = models.DateTimeField(verbose_name=_("payment date"),
        help_text=_("time at which the payment was confirmed"))
    amount = models.IntegerField(verbose_name=_("amount"), help_text=_("actual price, in euro cents"))

    class Meta:
        verbose_name = _("cashflow")
        verbose_name_plural = _("cashflows")

    def __str__(self):
        return "%s on %s at %s" % (
            utils.currency(self.amount),
            self.payment_mode.reference,
            self.payment_date,
        )


class Payment(models.Model):
    """A payment action."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments',
        verbose_name=_("user"), help_text=_("user for whom the service was bought"))
    service_price = models.ForeignKey(ServicePrice, related_name='payments',
        verbose_name=_("service price"))
    amount = models.PositiveIntegerField(verbose_name=_("amount"))
    cashflow = models.ForeignKey(CashFlow, related_name='payments',
        verbose_name=_("cashflow"))

    billing_date = models.DateField(verbose_name=_("billing date"),
        help_text=_("date at which the paid service should be activated"))

    class Meta:
        unique_together = ('user', 'service_price', 'cashflow')
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    def __str__(self):
        return "%s for %s on %s" % (self.service_price.service.name, self.user, self.cashflow)

    @property
    def unit_price(self):
        return self.service_price.amount

    @property
    def total_price(self):
        return self.amount * self.unit_price
