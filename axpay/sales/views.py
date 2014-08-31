# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.


from axpay.money import models as money_models
from axpay.web.views import generic
from . import forms

#class UserListView(base.ListView):
#    template_name = 'users_list.html'
#
#    def get_queryset(self):
#        return money_api.get_users()


class PaymentRegisterView(generic.FormView):
    topnav = 'sales'
    sidenav = 'payment-register'

    form_class = forms.PaymentRegisterForm
    template_name = 'sales/payment_register.html'

    success_url = 'sales:index'

    def get_form_kwargs(self):
        """Override the default kwargs to add our list of available services."""
        kwargs = super(PaymentRegisterView, self).get_form_kwargs()
        kwargs.update(
            services=money_models.ServicePrice.objects.available().order_by('service__name'),
        )
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(PaymentRegisterView, self).form_valid(form)


class SalesIndexView(generic.TemplateView):
    topnav = 'sales'
    sidenav = 'index'
    template_name = 'sales/index.html'
