# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import utils


def get_expiry_date(billing_date, jr=False):
    if billing_date is None:
        return billing_date
    return datetime.date(year=billing_date.year + 1, month=1, day=1)


def recompute_profile(contributor):

    try:
        latest_contribution_date = (contributor.ordered_items
            .filter(product_price__product__kind__in=Product.VALID_CONTRIBUTION_KINDS)
            .latest('billing_date')
        ).billing_date
    except OrderItem.DoesNotExist:
        latest_contribution_date = None

    lifetime_contribution = (contributor.ordered_items
        .filter(product_price__product__kind__in=Product.FORLIFE_CONTRIBUTION_KINDS)
        .exists()
    )

    try:
        latest_jr_subscription_date = (contributor.ordered_items
            .filter(product_price__product__kind__in=Product.JR_SUBSCRIBED_KINDS)
            .latest('billing_date')
        ).billing_date
    except OrderItem.DoesNotExist:
        latest_jr_subscription_date = None

    contributor.contributions_payed_until = get_expiry_date(latest_contribution_date)
    contributor.jr_subscribed_until = get_expiry_date(latest_jr_subscription_date)
    contributor.has_lifetime_contribution = lifetime_contribution
    contributor.save()



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

    FORLIFE_CONTRIBUTION_KINDS = (
        KIND_LIFETIME_SUBSCRIPTION,
    )

    VALID_CONTRIBUTION_KINDS = (
        KIND_STANDARD_SUBSCRIPTION,
        KIND_COUPLE_SUBSCRIPTION,
    )

    JR_SUBSCRIBED_KINDS = (
        KIND_JR_SUBSCRIPTION,
    )

    kind = models.CharField(max_length=16, choices=KIND_CHOICES, verbose_name=_("kind"))
    name = models.CharField(max_length=32, unique=True, verbose_name=_("name"))

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_kind_display())


class ProductPriceQuerySet(models.QuerySet):
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

    objects = ProductPriceQuerySet.as_manager()

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

    owner = models.ForeignKey('accounts.Contributor', related_name='payment_modes',
        verbose_name=_("owner"))
    kind = models.CharField(max_length=16, choices=KIND_CHOICES,
        verbose_name=_("kind"))
    reference = models.CharField(max_length=32, unique=True, verbose_name=_("reference"))

    class Meta:
        verbose_name = _("payment mode")
        verbose_name_plural = _("payment modes")

    def __str__(self):
        return '%s (%s) for %s' % (
            self.reference, self.get_kind_display(), self.owner.full_name or self.owner.username)


class Order(models.Model):
    """Pay for a set of products on a PaymentMode

    One single Order may be used to pay for several products.
    """

    payment_mode = models.ForeignKey(PaymentMode, related_name='orders',
        verbose_name=_("payment mode"))
    payment_date = models.DateTimeField(verbose_name=_("payment date"),
        help_text=_("time at which the payment was confirmed"))
    amount = models.IntegerField(verbose_name=_("amount"), help_text=_("actual price, in euro cents"))

    recurring = models.BooleanField(default=False,
        verbose_name=_("recurring"), help_text=_("Automatically generated for recurring services"))

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return "%s on %s at %s" % (
            utils.currency(self.amount),
            self.payment_mode.reference,
            self.payment_date,
        )

    def get_absolute_url(self):
        return reverse('sales:order-detail', args=[self.pk])


class OrderItem(models.Model):
    """An item from an order."""

    user = models.ForeignKey('accounts.Contributor', related_name='ordered_items',
        verbose_name=_("user"), help_text=_("user for whom the product was bought"))
    product_price = models.ForeignKey(ProductPrice, related_name='order_items',
        verbose_name=_("product price"))
    amount = models.PositiveIntegerField(verbose_name=_("amount"))
    order = models.ForeignKey(Order, related_name='items',
        verbose_name=_("order"))

    billing_date = models.DateField(verbose_name=_("billing date"),
        help_text=_("date at which the paid product should be activated"))

    class Meta:
        unique_together = ('user', 'product_price', 'order')
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self):
        return "%s for %s on %s" % (self.product_price.product.name, self.user, self.order)

    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)
        recompute_profile(self.user)
        return res

    @property
    def unit_price(self):
        return self.product_price.amount

    @property
    def total_price(self):
        return self.amount * self.unit_price

    @property
    def billing_year(self):
        return self.billing_date.year


def up_to_date(contributor, at=None):
    return contributor.up_to_date(at)

def jr_subscribed(contributor, at=None):
    return contributor.jr_subscribed(at)
