# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function


def currency(amount):
    """Convert an amount in euro cents to a currency text."""

    return '%d.%02d' % (amount // 100, amount % 100)
