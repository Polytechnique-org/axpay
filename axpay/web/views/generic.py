# -*- coding: utf-8 -*-
# Copyright (c) 2013 Polytechnique.org. All rights reserved.

from django.views import generic
from braces import views as braces_views


class AXPayMixin(braces_views.LoginRequiredMixin):
    topnav = ''
    sidenav = ''

    def get_context_data(self, **kwargs):
        ctxt = super(AXPayMixin, self).get_context_data(**kwargs)
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
