# from django.urls import path
# from django.contrib import admin
# from T1_SupplierResponse import views as callapps_views
# from . import views
from django.conf.urls import include, url, static
#
# urlpatterns = [
# 	path('', views.index, name='index'),
#
#     #url('', include('views.urls')),
# ]
from django.urls import path

from . import views

urlpatterns = [
    url(r'^T1_SupplierResponse', include('T1_SupplierResponse.urls')),
    #path('', views.index, name='index'),
]