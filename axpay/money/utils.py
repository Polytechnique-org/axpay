# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


def currency(amount):
    """Convert an amount in euro cents to a currency text."""

    return '%d.%02d' % (amount // 100, amount % 100)
