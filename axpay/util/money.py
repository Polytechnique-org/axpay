# -*- coding: utf-8 -*-
# Copyright (c) 2013 AX. All rights reserved.


import decimal


def to_euros(cents):
    return (decimal.Decimal(cents) / decimal.Decimal(100)).quantize(decimal.Decimal('0.01'))
