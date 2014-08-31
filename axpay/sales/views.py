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
        cashflows = (money_models.CashFlow.objects
            .order_by('-payment_date')
            .select_related(
                'payment_mode__owner',
            )
            )[:10]

        ctxt.update(
            last_cashflows=cashflows,
        )
        return ctxt


class PaymentRegisterView(generic.FormView):
    topnav = 'sales'
    sidenav = 'payment-register'

    form_class = forms.PaymentRegisterForm
    template_name = 'sales/payment_register.html'

    success_url = 'sales:cashflow-detail'

    def get_form_kwargs(self):
        """Override the default kwargs to add our list of available services."""
        kwargs = super(PaymentRegisterView, self).get_form_kwargs()
        kwargs.update(
            services=money_models.ServicePrice.objects.available().order_by('service__name'),
        )
        return kwargs

    def form_valid(self, form):
        data = form.save()
        self._cashflow = data['cashflow']
        return super(PaymentRegisterView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'pk': self._cashflow.pk})


class PaymentListView(generic.TemplateView):
    pass


class CashFlowDetailView(generic.DetailView):
    topnav = 'sales'
    sidenav = 'cashflows'

    model = money_models.CashFlow
    context_object_name = 'cashflow'
    template_name = 'sales/cashflow_detail.html'

    def get_context_data(self, **kwargs):
        ctxt = super(CashFlowDetailView, self).get_context_data(**kwargs)
        cashflow = ctxt['cashflow']
        cashflow_payments = cashflow.payments.select_related(
            'service_price__service',
            'user',
        )
        ctxt.update(
            cashflow_payments=cashflow_payments,
        )
        return ctxt
