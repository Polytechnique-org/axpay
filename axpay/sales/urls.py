# -*- coding: utf-8 -*-
# Copyright (c) 2013 AX. All rights reserved.


from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.SalesIndexView.as_view(), name='index'),
    url(r'^order/(?P<pk>\d+)/$', views.OrderDetailView.as_view(), name='order-detail'),
    url(r'^orders/', views.OrderListView.as_view(), name='orders'),
    url(r'^order/register/', views.OrderRegisterView.as_view(), name='order-register'),
)
