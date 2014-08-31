# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.


from axpay.web.views import generic
from . import forms

#class UserListView(base.ListView):
#    template_name = 'users_list.html'
#
#    def get_queryset(self):
#        return money_api.get_users()


class PaymentRegisterView(generic.FormView):
    topnav = 'sales'

    form_class = forms.PaymentRegisterForm
    template_name = 'sales/payment_register.html'

    success_url = 'sales:index'

    def form_valid(self, form):
        form.save()
        return super(PaymentRegisterView, self).form_valid(form)


class SalesIndexView(generic.TemplateView):
    topnav = 'sales'
    template_name = 'sales/index.html'
