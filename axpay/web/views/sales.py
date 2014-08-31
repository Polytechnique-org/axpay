# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.


from . import base
from .. import forms

#class UserListView(base.ListView):
#    template_name = 'users_list.html'
#
#    def get_queryset(self):
#        return money_api.get_users()


class PaymentRegisterView(base.FormView):
    form_class = forms.PaymentRegisterForm
    template_name = 'payment_register.html'

    success_url = '/'

    def form_valid(self, form):
        form.save()
        return super(PaymentRegisterView, self).form_valid(form)
