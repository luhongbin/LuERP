"""LUERP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url, static
from LUERP import views
import T1_SupplierResponse.views
from django.contrib import admin
import workflow.views
import LUERP.views
import selfhelp.urls
import basedata.urls
import purchase.urls


admin.site.site_header = 'LUTEC信息管理系统'
admin.site.site_title = '登录系统后台'
admin.site.site_footer = '宁波耀泰集团'  # 设置后台底部标题
admin.site.index_title = '管理項目'

admin.autodiscover()

api_patterns = [
    url(r'^wechat/', include("apps.wechat.views")),
    url(r'^meeting/', include("apps.meetings.views")),
]

urlpatterns = [
    url('^$', LUERP.views.home),
    #path('admin/', admin.site.urls),
    url(r"^admin/(?P<app>\w+)/(?P<model>\w+)/(?P<object_id>\d+)/change/start", workflow.views.start),
    url(r"^admin/(?P<app>\w+)/(?P<model>\w+)/(?P<object_id>\d+)/change/approve/(?P<operation>\d+)", workflow.views.approve),
    url(r"^admin/(?P<app>\w+)/(?P<model>\w+)/(?P<object_id>\d+)/change/restart/(?P<instance>\d+)", workflow.views.restart),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/basedata/', include(basedata.urls)),
    url(r'^admin/selfhelp/', include(selfhelp.urls)),
    url(r'^admin/purchase/', include(purchase.urls)),
    url(r'^tracking/', include('tracking.urls')),
    #path('T1_SupplierResponse/', admin.site.urls),
    #url(r'^index/$',views.index),
    url(r'^hello/', T1_SupplierResponse.views.index),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^sysadmin/', admin.site.urls),
    url(r'^api/', include(api_patterns)),
    # url(r'^admin/basedata/', basedata.urls),
    # url(r'^admin/selfhelp/', selfhelp.urls),
    #url(r'^T1_SupplierResponse', include('T1_SupplierResponse.urls')),
]
