#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "axpay.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
