# -*- coding: utf-8 -*-
# Copyright (c) 2013 AX. All rights reserved.

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


from .views import base as base_views

# Main views
urlpatterns = patterns('',
    url(r'^$', base_views.IndexView.as_view(), name='index'),
    url(r'^sales/', include('axpay.sales.urls', namespace='sales')),
    url(r'^contributions/', include('axpay.contributions.urls', namespace='contributions')),
)

# Utils
urlpatterns += patterns('axpay.util.views',
    url(r'^lang/(?P<lang_code>\w+)/$', 'set_language', name='set_language'),
)

# Auth
urlpatterns += patterns('',
    url(r'^xorgauth/', include('django_authgroupex.urls', namespace='authgroupex')),
    url(r'^login/$', base_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'},
        name='logout'),
)

# Libs

admin.site.login_template = 'authgroupex/admin_login.html'

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
