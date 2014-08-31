# -*- coding: utf-8 -*-
# Copyright (c) 2013 AX. All rights reserved.


from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.SalesIndexView.as_view(), name='index'),
    url(r'^payment/register/', views.PaymentRegisterView.as_view(), name='payment-register'),
)
