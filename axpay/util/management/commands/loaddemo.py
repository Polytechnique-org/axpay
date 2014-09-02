# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


from django.core.management import base


from axpay.money import testing as money_testing


class Command(base.NoArgsCommand):
    help = "Load a demo, standard database."

    def handle_noargs(self, **kwargs):
        orders = money_testing.ExampleOrdersFactory()
        print("Setup %d orders" % len(orders))
