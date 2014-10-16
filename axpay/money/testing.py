# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


import collections
import datetime
import factory
import factory.django

from django.utils import timezone

from axpay.accounts import models as accounts_models
from . import models


class AllProductsFactory(factory.Factory):
    class Meta:
        model = models.Product

    items = [
        (models.Product.KIND_STANDARD_SUBSCRIPTION, "Cotisation"),
        (models.Product.KIND_JR_SUBSCRIPTION, "Cotisation J&R X"),
        (models.Product.KIND_JR_SUBSCRIPTION, "Cotisation J&R externe"),
        (models.Product.KIND_COUPLE_SUBSCRIPTION, "Cotisation conjoint"),
        (models.Product.KIND_LIFETIME_SUBSCRIPTION, "Cotisation à vie"),
    ]

    @classmethod
    def _create(cls, target_class, items):  # pylint: disable=arguments-differ
        products = []
        for kind, name in items:
            product, _created = target_class.objects.get_or_create(
                name=name,
                defaults={'kind': kind},
            )
            products.append(product)
        return products


class AllPricesFactory(factory.Factory):
    class Meta:
        model = models.ProductPrice

    products = factory.SubFactory(AllProductsFactory)
    available_since = factory.LazyAttribute(
        lambda _o: timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
    available_until = None
    amount = 4200  # 42€

    @classmethod
    def _create(cls, target_class, products, available_since, available_until, amount):  # pylint: disable=arguments-differ
        prices = []
        for product in products:
            price, _created = target_class.objects.get_or_create(
                product=product,
                available_since=available_since,
                available_until=available_until,
                defaults={'amount': amount},
            )
            prices.append(price)

        return prices


class ExamplePaymentOwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = accounts_models.Contributor

    full_name = factory.Sequence(lambda n: "John Demo%s" % n)


class ExampleOrderFactory(factory.Factory):
    class Meta:
        model = models.Order
        exclude = ['items', 'product_prices']

    owner = factory.SubFactory(ExamplePaymentOwnerFactory)

    items = [models.Product.KIND_STANDARD_SUBSCRIPTION]
    nb_orders = 1
    payment_kind = models.PaymentMode.KIND_CASH
    latest_order = factory.LazyAttribute(lambda _o: timezone.now())
    ref_date = factory.LazyAttribute(lambda o: o.latest_order - datetime.timedelta(days=365 * o.nb_orders))
    product_prices = factory.LazyAttribute(lambda _o: models.ProductPrice.objects.all())

    @classmethod
    def _setup_next_sequence(cls):
        return models.PaymentMode.objects.count() + 1

    @factory.lazy_attribute_sequence
    def reference(self, n):
        prefixes = {
            models.PaymentMode.KIND_CASH: 'L',
            models.PaymentMode.KIND_CHECK: 'C',
            models.PaymentMode.KIND_CARD: 'CB',
            models.PaymentMode.KIND_DIRECT: 'P',
        }

        return '%s%08d' % (prefixes[self.payment_kind], n)

    @factory.lazy_attribute
    def selected_product_prices(self):
        product_prices = {}
        for price in self.product_prices:
            product_prices[price.product.kind] = price

        return [product_prices[item] for item in self.items]

    @classmethod
    def _create(cls, target_class,
            selected_product_prices, nb_orders, payment_kind,
            latest_order, ref_date, owner, reference):

        ordered_items = []
        aggregated_product_prices = collections.Counter(selected_product_prices)

        payment_mode = models.PaymentMode.objects.create(
            kind=payment_kind,
            owner=owner,
            reference=reference,
        )
        products_total = sum(sp.amount for sp in selected_product_prices)
        for i in range(nb_orders):
            order = target_class.objects.create(
                payment_mode=payment_mode,
                payment_date=ref_date + i * datetime.timedelta(days=365),
                amount=products_total,
                recurring=nb_orders > 1,
            )
            for sp, amount in aggregated_product_prices.items():
                models.OrderItem.objects.create(
                    user=payment_mode.owner,
                    product_price=sp,
                    amount=amount,
                    order=order,
                    billing_date=order.payment_date.date(),
                )
        return order


class ExampleOrdersFactory(factory.Factory):
    class Meta:
        model = models.Order

    prices = factory.SubFactory(AllPricesFactory)

    orders = factory.List([
        factory.SubFactory(ExampleOrderFactory,
            product_prices=factory.SelfAttribute('...prices'),
            items=[models.Product.KIND_STANDARD_SUBSCRIPTION],
            payment_kind=models.PaymentMode.KIND_CASH,
        ),
        factory.SubFactory(ExampleOrderFactory,
            product_prices=factory.SelfAttribute('...prices'),
            items=[models.Product.KIND_STANDARD_SUBSCRIPTION, models.Product.KIND_COUPLE_SUBSCRIPTION],
            payment_kind=models.PaymentMode.KIND_CHECK,
        ),
        factory.SubFactory(ExampleOrderFactory,
            product_prices=factory.SelfAttribute('...prices'),
            items=[models.Product.KIND_STANDARD_SUBSCRIPTION],
            nb_orders=3,
            payment_kind=models.PaymentMode.KIND_CARD,
            ref_date=factory.LazyAttribute(lambda _o: timezone.now() - datetime.timedelta(days=600)),
        ),
        factory.SubFactory(ExampleOrderFactory,
            product_prices=factory.SelfAttribute('...prices'),
            items=[
                models.Product.KIND_STANDARD_SUBSCRIPTION,
                models.Product.KIND_COUPLE_SUBSCRIPTION,
                models.Product.KIND_JR_SUBSCRIPTION,
                models.Product.KIND_JR_SUBSCRIPTION,
            ],
            nb_orders=4,
            payment_kind=models.PaymentMode.KIND_DIRECT,
        ),
    ])

    @classmethod
    def _create(cls, target_class, prices, orders):
        return orders
