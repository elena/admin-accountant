# -*- coding: utf-8 -*-
"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from . import routers
from subledgers.views import upload_view, dump_view


urlpatterns = [

    # trivial urls
    url(r'^$', TemplateView.as_view(template_name="index.html")),

    url(r'dump/$', dump_view, name="dump-view"),

    # "The Upload"
    url(r'^upload/', upload_view, name="upload-view"),

    # internal app urls

    url(r'^ledgers/',
        include('ledgers.urls')),

    url(r'^bank/reconciliations/',
        include('subledgers.bank_reconciliations.urls')),


    # reports

    url(r'^reports/',
        include('reports.urls')),

    # external urls

    url(r'^api/', include(routers, namespace='api')),

    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
