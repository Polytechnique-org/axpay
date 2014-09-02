# -*- coding: utf-8 -*-



def currency(amount):
    """Convert an amount in euro cents to a currency text."""

    return '%d.%02d' % (amount // 100, amount % 100)
