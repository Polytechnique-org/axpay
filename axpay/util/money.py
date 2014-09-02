# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


import decimal


def to_euros(cents):
    return (decimal.Decimal(cents) / decimal.Decimal(100)).quantize(decimal.Decimal('0.01'))
