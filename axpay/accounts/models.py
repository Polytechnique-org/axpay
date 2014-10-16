# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class ContributorProfileQuerySet(models.QuerySet):
    def up_to_date(self, at=None):
        if at is None:
            at = timezone.now()
        return (self
            .filter(
                models.Q(contributions_payed_until__gte=at.date())
                | models.Q(has_lifetime_contribution=True)
            )
            .distinct()
        )

    def jr_subscribed(self, at=None):
        if at is None:
            at = timezone.now()
        return self.filter(jr_subscribed_until__gte=at.date())


class Contributor(models.Model):
    full_name = models.CharField(_('full name'), max_length=100, blank=True)
    email = models.EmailField(_('email address'), blank=True)

    contributions_payed_until = models.DateField(blank=True, null=True, db_index=True,
        verbose_name=_("contributions payed until"))
    jr_subscribed_until = models.DateField(blank=True, null=True, db_index=True,
        verbose_name=_("subscribed to J&R until"))
    has_lifetime_contribution = models.BooleanField(default=False, db_index=True,
        verbose_name=_("lifetime contribution"))

    objects = ContributorProfileQuerySet.as_manager()

    class Meta:
        verbose_name = _('contributor')
        verbose_name_plural = _('contributors')

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('contributions:contributor-detail', args=[self.pk])

    def up_to_date(self, at):
        if at is None:
            at = timezone.now()
        return (self.has_lifetime_contribution
            or (self.contributions_payed_until is not None
                and self.contributions_payed_until >= at.date()
            )
        )

    def jr_subscribed(self, at):
        if at is None:
            at = timezone.now()
        return (self.jr_subscribed_until is not None
                and self.jr_subscribed_until >= at.date())

