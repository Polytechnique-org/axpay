# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

from __future__ import unicode_literals, print_function

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import utils


class Product(models.Model):
    """A base product."""

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
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_kind_display())


class ProductPriceManager(models.Manager):
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


class ProductPrice(models.Model):
    """The price of a product at a given time."""

    product = models.ForeignKey(Product, related_name='prices', verbose_name=_("product"))
    amount = models.IntegerField(verbose_name=_("amount"),
        help_text=_("actual price, in euro cents"))

    available_since = models.DateTimeField(verbose_name=_("available since"))
    available_until = models.DateTimeField(blank=True, null=True, verbose_name=_("available until"))

    objects = ProductPriceManager()

    class Meta:
        verbose_name = _("product price")
        verbose_name_plural = _("product prices")

    def __str__(self):
        return "%s: %s (from %s to %s)" % (
            self.product.name,
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


class Order(models.Model):
    """Pay for a set of products on a PaymentMode

    One single Order may be used to pay for several products.
    """

    payment_mode = models.ForeignKey(PaymentMode, related_name='orders',
        verbose_name=_("payment mode"))
    payment_date = models.DateTimeField(verbose_name=_("payment date"),
        help_text=_("time at which the payment was confirmed"))
    amount = models.IntegerField(verbose_name=_("amount"), help_text=_("actual price, in euro cents"))

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return "%s on %s at %s" % (
            utils.currency(self.amount),
            self.payment_mode.reference,
            self.payment_date,
        )


class Payment(models.Model):
    """A payment action."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments',
        verbose_name=_("user"), help_text=_("user for whom the product was bought"))
    product_price = models.ForeignKey(ProductPrice, related_name='payments',
        verbose_name=_("product price"))
    amount = models.PositiveIntegerField(verbose_name=_("amount"))
    order = models.ForeignKey(Order, related_name='payments',
        verbose_name=_("order"))

    billing_date = models.DateField(verbose_name=_("billing date"),
        help_text=_("date at which the paid product should be activated"))

    class Meta:
        unique_together = ('user', 'product_price', 'order')
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    def __str__(self):
        return "%s for %s on %s" % (self.product_price.product.name, self.user, self.order)

    @property
    def unit_price(self):
        return self.product_price.amount

    @property
    def total_price(self):
        return self.amount * self.unit_price
