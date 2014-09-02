# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.

from django.views import generic
from django.views.generic import edit as generic_edit
from django.views.generic import list as generic_list
from braces import views as braces_views


class AXPayMixin(braces_views.LoginRequiredMixin):
    topnav = ''
    sidenav = ''

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data(**kwargs)
        ctxt.update(
            topnav=self.topnav,
            sidenav=self.sidenav,
        )
        return ctxt


class TemplateView(AXPayMixin, generic.TemplateView):
    pass


class DetailView(AXPayMixin, generic.DetailView):
    pass


class FormView(AXPayMixin, generic.FormView):
    pass


class FilterListView(AXPayMixin, braces_views.SelectRelatedMixin, generic_edit.FormMixin, generic_list.ListView):

    select_related = ()
    context_object_name = 'orders'

    def get_form_kwargs(self):
        """Override to use GET instead of POST."""
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs

    def prepare_queryset(self, qs):
        return qs

    def enrich_queryset(self, qs):
        return qs

    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.prepare_queryset(qs)

        self.form = self.get_form(self.get_form_class())

        if self.form.is_valid() and self.request.GET:
            qs = self.form.filter(qs)
        else:
            qs = self.form.filter(qs, initial=True)
        return self.enrich_queryset(qs)

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data(**kwargs)
        ctxt.update(
            form=self.form,
        )
        return ctxt
