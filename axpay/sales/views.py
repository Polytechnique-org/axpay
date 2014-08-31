# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.


from django.core.urlresolvers import reverse, reverse_lazy

from axpay.money import models as money_models
from axpay.web.views import generic

from . import forms

#class UserListView(base.ListView):
#    template_name = 'users_list.html'
#
#    def get_queryset(self):
#        return money_api.get_users()


class SalesIndexView(generic.TemplateView):
    topnav = 'sales'
    sidenav = 'index'
    template_name = 'sales/index.html'

    def get_context_data(self, **kwargs):
        ctxt = super(SalesIndexView, self).get_context_data(**kwargs)
        orders = (money_models.Order.objects
            .order_by('-payment_date')
            .select_related(
                'payment_mode__owner',
            )
            )[:10]

        ctxt.update(
            last_orders=orders,
        )
        return ctxt


class OrderRegisterView(generic.FormView):
    topnav = 'sales'
    sidenav = 'order-register'

    form_class = forms.OrderRegisterForm
    template_name = 'sales/order_register.html'

    success_url = 'sales:order-detail'

    def get_form_kwargs(self):
        """Override the default kwargs to add our list of available products."""
        kwargs = super(OrderRegisterView, self).get_form_kwargs()
        kwargs.update(
            products=money_models.ProductPrice.objects.available().order_by('product__name'),
        )
        return kwargs

    def form_valid(self, form):
        data = form.save()
        self._order = data['order']
        return super(OrderRegisterView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'pk': self._order.pk})


class OrderListView(generic.TemplateView):
    pass


class OrderDetailView(generic.DetailView):
    topnav = 'sales'
    sidenav = 'orders'

    model = money_models.Order
    context_object_name = 'order'
    template_name = 'sales/order_detail.html'

    def get_context_data(self, **kwargs):
        ctxt = super(OrderDetailView, self).get_context_data(**kwargs)
        order = ctxt['order']
        order_items = order.items.select_related(
            'product_price__product',
            'user',
        )
        ctxt.update(
            order_items=order_items,
        )
        return ctxt
